# 목적: 보고서 원재료(raw data) 추출 → report_raw_YYYYMMDD.json
# 입력: outputs/context/factors_*.json + analysis_*.json + chart paths
# 출력: outputs/context/report_raw_YYYYMMDD.json  ← agent가 이 파일을 읽어 MD 작성
# 마크다운 생성 로직 없음. 지능은 .claude/skills/consulting-context/SKILL.md 에 있음.

import glob
import json
import os
from datetime import datetime

from src.config import (
    CORR_LAGS, GRANGER_MODERATE, GRANGER_STRONG, GRANGER_WEAK,
    LASSO_CV_FOLDS, LEAD_LAG_MAX_LAG, RF_N_ESTIMATORS, RF_RANDOM_STATE,
    ROLLING_STABILITY_THRESHOLD, ROLLING_WINDOW,
    SHORT_PERIOD_MONTHS, SHORT_ROLLING_WINDOW, SHORT_GRANGER_MAX_LAG,
    BREAK_PENALTY, BREAK_MIN_SIZE,
)

_REGIME_DISPLAY = {"Expansion": "고모멘텀", "Neutral": "안정성장", "Contraction": "저모멘텀"}


def _load_latest(prefix: str) -> dict:
    files = sorted(glob.glob(f"outputs/context/{prefix}_*.json"))
    return json.load(open(files[-1], encoding="utf-8")) if files else {}


def build_raw_data(
    factors_data: dict = None, analysis: dict = None, chart_paths: dict = None
) -> str:
    """분석 JSON + 차트 경로 → report_raw_YYYYMMDD.json (agent 입력 원재료).

    보고서 작성 지능은 .claude/skills/consulting-context/SKILL.md 참조.
    """
    factors_data = factors_data or _load_latest("factors")
    analysis     = analysis     or _load_latest("analysis")
    chart_paths  = chart_paths  or {}
    date_str     = datetime.now().strftime("%Y%m%d")

    reg     = analysis.get("regime", {})
    fdata   = factors_data.get("factors", {})
    rseries = reg.get("regime_series", [])

    def _dir(fid: str) -> str:
        vals = [d["value"] for d in fdata.get(fid, {}).get("data", [])[-4:]
                if d.get("value") is not None]
        return ("↑" if vals[-1] > (vals[-3] if len(vals) >= 3 else vals[0]) else "↓") \
               if len(vals) >= 2 else "N/A"

    def _regime_at(ym: str) -> str:
        return {r["date"][:7]: r["regime"] for r in rseries}.get(ym, "N/A")

    recent_6 = [r["regime"] for r in rseries[-6:]] if len(rseries) >= 6 else []
    lasso    = analysis.get("lasso_selected", [])
    lasso_ids = {r["factor"] for r in lasso}
    imp      = analysis.get("importance", [])

    # company events regime overlay chart
    chart_overlay = None
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from company_events.regime_overlay import draw as _draw
        chart_overlay = _draw(date_str)
    except Exception:
        pass

    MP_FACTORS = ["FEDFUNDS", "T10Y2Y", "DGS10", "PAYEMS", "UNRATE",
                  "RETAILSMNSA", "DCOILWTICO", "PPIACO", "VIXCLS", "TCU"]

    raw = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "report_date": date_str,
            "target_label": factors_data.get("target", {}).get("label", "INDPRO MoM%"),
            "data_source": "FRED (Federal Reserve Bank of St. Louis)",
            "analysis_period": analysis.get("data_period", {}),
            "params": {
                "lasso_cv_folds": LASSO_CV_FOLDS,
                "lasso_alpha": analysis.get("lasso_alpha"),
                "granger_maxlag": LEAD_LAG_MAX_LAG,
                "granger_strong": GRANGER_STRONG, "granger_moderate": GRANGER_MODERATE,
                "granger_weak": GRANGER_WEAK,
                "rolling_window": ROLLING_WINDOW, "rolling_threshold": ROLLING_STABILITY_THRESHOLD,
                "rf_n_estimators": RF_N_ESTIMATORS, "rf_random_state": RF_RANDOM_STATE,
                "corr_lags": CORR_LAGS, "break_penalty": BREAK_PENALTY,
                "break_min_size": BREAK_MIN_SIZE, "short_period_months": SHORT_PERIOD_MONTHS,
                "short_rolling_window": SHORT_ROLLING_WINDOW,
                "short_granger_maxlag": SHORT_GRANGER_MAX_LAG,
            },
        },
        "regime": {
            **reg,
            "display_label": _REGIME_DISPLAY.get(reg.get("regime", ""), ""),
            "recent_6m": recent_6,
            "expansion_count": recent_6.count("Expansion"),
        },
        "leading_indicators": {
            "signals": [
                {"factor": r["factor"], "label": r["label"], "lag": r["lag"],
                 "strength": r["strength"], "direction": _dir(r["factor"])}
                for r in analysis.get("granger_leading", [])[:6]
            ],
            "granger_full": analysis.get("granger", []),
            "lead_lag": analysis.get("lead_lag", []),
            "consensus_factors": list(
                {r["factor"] for r in analysis.get("granger", [])
                 if r["strength"] in ("STRONG", "MODERATE")}
                & {r["factor"] for r in analysis.get("lead_lag", []) if r.get("is_leading")}
            ),
        },
        "lasso":          {"alpha": analysis.get("lasso_alpha"), "selected": lasso},
        "rf_importance":  [{**r, "lasso_selected": r["factor"] in lasso_ids} for r in imp[:8]],
        "dual_confirmed": list(lasso_ids & {r["factor"] for r in imp}),
        "rolling_stability": analysis.get("rolling_stability", {}),
        "correlation":    analysis.get("correlation", []),
        "short_period_analysis": analysis.get("short_period_analysis", {}),
        "factor_directions": {
            fid: {"label": fdata.get(fid, {}).get("label", fid),
                  "direction": _dir(fid),
                  "last_value": (fdata.get(fid, {}).get("data") or [{}])[-1].get("value")}
            for fid in MP_FACTORS
        },
        "company_events": {
            "chart_path": chart_overlay,
            "key_dates": [
                {"event": "Reddit — OpenAI 계약",     "ym": "2024-05", "regime": _regime_at("2024-05")},
                {"event": "Reddit — Q3 어닝 급등",     "ym": "2024-10", "regime": _regime_at("2024-10")},
                {"event": "Reddit — Dynp break 1",    "ym": "2025-01", "regime": _regime_at("2025-01")},
                {"event": "Samsung — Tesla 2nm 계약", "ym": "2025-07", "regime": _regime_at("2025-07")},
                {"event": "Samsung — Dynp break",     "ym": "2025-08", "regime": _regime_at("2025-08")},
            ],
        },
        "consulting_implications": analysis.get("consulting_implications", {}),
        "chart_paths": chart_paths,
    }

    os.makedirs("outputs/context", exist_ok=True)
    path = f"outputs/context/report_raw_{date_str}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 보고서 원재료 저장: {path}")
    return path


if __name__ == "__main__":
    build_raw_data()
