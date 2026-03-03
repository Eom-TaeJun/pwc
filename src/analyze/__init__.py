"""Factor 분석 패키지 — 오케스트레이터."""
import json
import os
from datetime import datetime

from .io import load_latest_factors, build_dataframe
from .lasso import run_lasso
from .correlation import run_correlation
from .rolling import run_rolling_ols
from .importance import run_importance
from .regime import run_regime
from .granger import run_granger
from .lead_lag import run_lead_lag
from .break_detect import detect_breaks
from .period import run_period_analysis

from src.config import RATE_HIGH_ERA_START, RATE_HIGH_ERA_END, RATE_CUT_ERA_START

OUTPUT_DIR = "outputs/context"

__all__ = [
    "load_latest_factors", "build_dataframe",
    "run_lasso", "run_correlation", "run_rolling_ols",
    "run_importance", "run_regime", "run_granger", "run_lead_lag",
    "analyze",
]


def analyze(factors_data: dict = None) -> dict:
    """전체 분석 → outputs/context/analysis_YYYYMMDD.json."""
    if factors_data is None:
        factors_data = load_latest_factors()

    X, y = build_dataframe(factors_data)
    lasso_result = run_lasso(X, y, factors_data)
    lasso        = lasso_result["selected"]
    lasso_alpha  = lasso_result["alpha"]
    corr         = run_correlation(X, y, factors_data)
    rolling      = run_rolling_ols(X, y, lasso)
    importance = run_importance(X, y, lasso, factors_data)
    regime     = run_regime(y)
    granger    = run_granger(X, y, factors_data)
    lead_lag   = run_lead_lag(X, y, factors_data)

    # Granger STRONG/MODERATE → 실질 선행지표 목록 (Cross-correlation과 독립적으로 계산)
    granger_leading = [
        {"factor": g["factor"], "label": g["label"],
         "lag": g["optimal_lag"], "strength": g["strength"]}
        for g in granger if g["strength"] in ("STRONG", "MODERATE")
    ]

    top_g    = granger[0] if granger else None
    top_fac  = top_g["factor"] if top_g else (corr[0]["factor"] if corr else "N/A")
    top_lag  = top_g["optimal_lag"] if top_g else 0
    reg_str  = regime.get("regime", "N/A")
    reg_conf = regime.get("confidence", 0)
    # UMCSENT는 서베이 기반 — corr 또는 lasso 어디에든 포함되면 경고
    survey   = (
        [r["factor"] for r in corr if "UMCSENT" in r["factor"]] or
        [r["factor"] for r in lasso if "UMCSENT" in r["factor"]]
    )

    # ── 현재 사이클 분석 (PELT 기반) ────────────────────────────────
    breaks = detect_breaks(y)
    current_seg = breaks[-1]
    current_period = run_period_analysis(
        X, y, factors_data,
        start=current_seg["start"], end=current_seg["end"],
        label="현재 사이클 (PELT 감지)",
    )
    # short_period_analysis 하위 호환 필드 유지
    sp_lasso          = [{"factor": r["factor"], "label": r.get("label", r["factor"]),
                          "coefficient": r.get("coefficient", 0)}
                         for r in current_period.get("lasso_selected", [])]
    sp_granger_leading = current_period.get("granger_leading", [])
    sp_corr            = current_period.get("correlation", [])

    # ── 통화정책 사이클별 분석 ────────────────────────────────────────
    rate_high = run_period_analysis(
        X, y, factors_data,
        start=RATE_HIGH_ERA_START, end=RATE_HIGH_ERA_END,
        label="포스트코로나 고금리기 (2020-03 ~ 2024-09)",
    )
    rate_cut = run_period_analysis(
        X, y, factors_data,
        start=RATE_CUT_ERA_START,
        label="금리 인하기 (2024-09 ~ 현재)",
    )

    result = {
        "analyzed_at": datetime.now().isoformat(),
        "target": factors_data["target"]["series"],
        "data_period": {
            "start": str(y.index.min()), "end": str(y.index.max()), "n_obs": len(y)
        },
        "regime": regime,
        "lasso_selected": lasso,
        "lasso_alpha": lasso_alpha,
        "correlation": corr,
        "granger": granger,
        "granger_leading": granger_leading,
        "lead_lag": lead_lag,
        "rolling_stability": rolling,
        "importance": importance,
        "short_period_analysis": {
            "method": "fallback_fixed" if current_seg.get("fallback") else "ruptures_pelt",
            "all_segments": breaks,
            "current_segment": current_seg,
            **{k: v for k, v in current_period.items()
               if k not in ("label",)},
            "lasso_selected": sp_lasso,
            "granger_leading": sp_granger_leading,
            "correlation": sp_corr,
        },
        "policy_period_analysis": {
            "rate_high_era": rate_high,
            "rate_cut_era": rate_cut,
        },
        "consulting_implications": {
            "current_regime": f"{reg_str} (신뢰도 {reg_conf}%)",
            "leading_indicators": (
                f"{top_fac}가 INDPRO {top_lag}개월 선행"
                + (f" (Granger {top_g['strength']})" if top_g else "")
            ),
            "data_constraints": (
                "서베이 기반 지표(UMCSENT)는 후행 가능성 있음"
                if survey else "주요 지표 모두 하드 데이터"
            ),
            "client_narrative": (
                f"현재 산업생산 레짐: {reg_str}. "
                f"{top_fac} 신호 추이가 생산계획 조기 경보 역할"
            ),
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"analysis_{datetime.now().strftime('%Y%m%d')}.json")
    with open(path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved: {path}")
    return result
