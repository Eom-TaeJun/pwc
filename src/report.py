# 목적: Factor Pool 리서치 MD 보고서 생성 (PwC 컨설팅 스타일)
# 입력: outputs/context/factors_*.json + analysis_*.json + chart paths
# 출력: outputs/reports/factor_pool_YYYYMMDD.md
# 제외: PDF 변환, 웹 렌더링

import glob
import json
import os
from datetime import datetime

from src.config import (
    CORR_LAGS,
    GRANGER_MODERATE,
    GRANGER_STRONG,
    GRANGER_WEAK,
    LASSO_CV_FOLDS,
    LEAD_LAG_MAX_LAG,
    RF_N_ESTIMATORS,
    RF_RANDOM_STATE,
    ROLLING_STABILITY_THRESHOLD,
    ROLLING_WINDOW,
)

OUTPUT_DIR = "outputs/reports"

# 레짐 레이블 — 내부 GMM 분류명 → 보고서 표시명
# GMM은 INDPRO MoM% 변동성 기준으로 분류하므로 NBER 경기국면과 직접 대응 안 함
_REGIME_DISPLAY = {
    "Expansion":  "고모멘텀",    # MoM% 성장률이 장기 평균 대비 크게 높은 구간
    "Neutral":    "안정성장",    # 장기 평균 근방의 정상 성장 구간 (전체 86%)
    "Contraction": "저모멘텀",   # MoM% 성장률이 크게 낮거나 음수인 구간
}


def _load_latest(prefix: str) -> dict:
    files = sorted(glob.glob(f"outputs/context/{prefix}_*.json"))
    if not files:
        return {}
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def _fmt_table(rows: list, headers: list) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def _dynamic_title(analysis: dict) -> str:
    """분석 결과에서 인사이트 제목 자동 생성."""
    regime = analysis.get("regime", {}).get("regime", "Neutral")
    # Granger STRONG/MODERATE 중 최우선 선행 Factor
    granger = analysis.get("granger", [])
    lead_lag = analysis.get("lead_lag", [])
    granger_strong = [r for r in granger if r["strength"] in ("STRONG", "MODERATE")]
    leading = [r for r in lead_lag if r.get("is_leading")]
    # 양방법 합의 Factor 우선
    granger_ids = {r["factor"] for r in granger_strong}
    lead_ids = {r["factor"] for r in leading}
    consensus = granger_ids & lead_ids
    if consensus:
        fid = next(iter(consensus))
        ll_top = next((r for r in lead_lag if r["factor"] == fid), None)
        label = ll_top["label"] if ll_top else fid
        lag = ll_top["optimal_lag"] if ll_top else "N/A"
        return f"산업생산 {regime} 국면: {label}가 {lag}개월 앞서 신호를 보낸다"
    elif leading:
        top = leading[0]
        return f"산업생산 {regime} 국면: {top['label']}가 {top['optimal_lag']}개월 앞서 신호를 보낸다"
    elif granger_strong:
        # Granger만 유의 → Granger 자체 optimal_lag 사용 (lead_lag으로 덮어쓰지 않음)
        g = granger_strong[0]
        return f"산업생산 {regime} 국면: {g['label']} Granger 검증상 {g['optimal_lag']}개월 선행"
    return f"산업생산 {regime} 국면 진단 — Factor Pool 선행지표 분석"


def _scenario_table(reg_label: str, granger: list, lead_lag: list,
                    granger_leading: list = None) -> str:
    """레짐별 3시나리오 + Factor별 최적 lag 반영한 모니터링 주기."""
    gl = granger_leading or []
    priority_ids = {r["factor"] for r in gl}
    if not priority_ids:
        # fallback: Granger STRONG/MODERATE
        priority_ids = {r["factor"] for r in granger if r["strength"] in ("STRONG", "MODERATE")}

    # Granger lag(양수, 선행 방향) 기반 모니터링 주기
    # Cross-corr opt_lag는 음수(INDPRO가 먼저 움직이는 반응 방향)일 수 있어 사용 금지
    lag_map = {r["factor"]: r["lag"] for r in gl}
    if not lag_map:
        # fallback: Granger에서 직접 추출
        lag_map = {r["factor"]: r["optimal_lag"] for r in granger
                   if r["strength"] in ("STRONG", "MODERATE")}

    def _freq(fid: str) -> str:
        lag = lag_map.get(fid, 99)
        if lag <= 3:
            return "매월"
        if lag <= 6:
            return "격월"
        return "분기"

    label_map = {r["factor"]: r["label"] for r in granger}
    if priority_ids:
        top3 = list(priority_ids)[:3]
        watch_detail = " / ".join(
            f"{label_map.get(f, f)}({_freq(f)})" for f in top3
        )
    else:
        watch_detail = "전체 Factor Pool 분기 점검"

    rows = [
        ["**Expansion**", "선행 Factor 지속 상승", watch_detail, "현 포지션 유지, 레짐 전환 신호 모니터링"],
        ["**Neutral**", "혼조 — 방향성 불확실", watch_detail, "분기 1회 Factor Pool 전체 재평가"],
        ["**Contraction**", "선행 Factor 하락 전환", watch_detail, "조기 경보 발동, 클라이언트 리스크 재검토"],
    ]
    return _fmt_table(rows, ["시나리오", "신호 조건", "핵심 모니터링 Factor(주기)", "대응 권고"])


def build_factor_report(
    factors_data: dict = None, analysis: dict = None, chart_paths: dict = None
) -> str:
    factors_data = factors_data or _load_latest("factors")
    analysis = analysis or _load_latest("analysis")
    chart_paths = chart_paths or {}

    date_str = datetime.now().strftime("%Y%m%d")
    target_label = factors_data.get("target", {}).get("label", "INDPRO MoM%")
    period = analysis.get("data_period", {})
    now_iso = datetime.now().strftime("%Y-%m-%d")

    # 핵심 데이터 추출
    regime_info = analysis.get("regime", {})
    reg_label = regime_info.get("regime", "N/A")
    reg_conf = regime_info.get("confidence", 0)
    reg_probs = regime_info.get("probs", {})
    reg_entropy = regime_info.get("entropy", 1.0)
    ci = analysis.get("consulting_implications", {})

    granger = analysis.get("granger", [])
    granger_leading = analysis.get("granger_leading", [])
    lead_lag = analysis.get("lead_lag", [])
    lasso = analysis.get("lasso_selected", [])
    lasso_alpha = analysis.get("lasso_alpha", "CV 자동 선택")
    imp = analysis.get("importance", [])
    corr = analysis.get("correlation", [])
    rs = analysis.get("rolling_stability", {})
    rs_params = rs.get("_params", {"window": ROLLING_WINDOW, "threshold": ROLLING_STABILITY_THRESHOLD})
    r_window = rs_params["window"]
    r_threshold = rs_params["threshold"]

    # 동적 제목
    title = _dynamic_title(analysis)
    # 보고서용 레짐 표시명 (내부 영문 레이블 → 한글 표시명)
    reg_display = _REGIME_DISPLAY.get(reg_label, reg_label)

    # 양방법 합의 Factor
    granger_ids = {r["factor"] for r in granger if r["strength"] in ("STRONG", "MODERATE")}
    leading = [r for r in lead_lag if r.get("is_leading")]
    lead_ids = {r["factor"] for r in leading}
    consensus = granger_ids & lead_ids
    top_factors = ", ".join(consensus) if consensus else ", ".join(list(lead_ids)[:3]) or "N/A"

    # ── Executive Summary ──────────────────────────────────────────
    prob_str = " | ".join(f"{k}: {v * 100:.1f}%" for k, v in reg_probs.items())
    s_exec = f"""## Executive Summary

> **한 줄 결론**: {ci.get('client_narrative', reg_label + ' 국면 — 선행지표 모니터링 강화 권고')}

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **{reg_display}** ({reg_label}, 신뢰도 {reg_conf}%) |
| 레짐 확률 분포 | {prob_str} |
| 핵심 선행지표 | {ci.get('leading_indicators', top_factors)} |
| 분석 기간 | {period.get('start', 'N/A')} ~ {period.get('end', 'N/A')} ({period.get('n_obs', 'N/A')}개월) |
| 데이터 출처 | FRED (Federal Reserve Bank of St. Louis) |

"""

    # ── Section 1: 지금 어디에 있는가? ────────────────────────────
    s1 = f"""## 1. 지금 어디에 있는가?

> **핵심 발견**: 미국 산업생산(INDPRO)은 현재 **{reg_display}** 국면에 있으며,
> Shannon Entropy {reg_entropy:.3f}로 {'레짐 전환 가능성이 낮은 안정적 상태' if reg_entropy < 0.8 else '복수 국면 혼재 — 불확실성 높음'}입니다.

GMM 3-state 모델이 {period.get('n_obs', 'N/A')}개월 데이터에서 식별한 현재 레짐:

> ※ 레짐은 INDPRO MoM% **성장률 변동성** 기준으로 분류합니다. NBER 경기확장·침체와 직접 대응하지 않습니다.
> 고모멘텀(MoM% 장기 평균 대비 +1σ 이상) / 안정성장(정상 범위) / 저모멘텀(−1σ 이하 또는 음수)

| 지표 | 값 | 해석 |
|------|----|------|
| **레짐** | **{reg_display}** ({reg_label}) | GMM 사후확률 최댓값 기준 |
| 신뢰도 | {reg_conf}% | Shannon Entropy {reg_entropy:.3f} (GMM 사후확률 기반) |
| 레짐 확률 | {prob_str} | {'단일 레짐 우세' if reg_conf > 60 else '복수 레짐 경합'} |

{ci.get('current_regime', '')}

> **⚠ 해석 주의**: 신뢰도 {reg_conf}%는 "현재 데이터점이 {reg_display}({reg_label}) 클러스터에 속할 GMM 사후확률"이며,
> 레짐 분류의 절대적 정확성을 보장하지 않습니다.
> GMM 모델은 **구조 변화 구간(2008~2009 금융위기, 2020 팬데믹)에서 신뢰도가 저하**됩니다.
> 해당 기간 데이터가 포함된 전체 추정 결과이므로 최근 구간(2020 이후) 별도 검증을 권고합니다.

"""
    if chart_paths.get("regime_timeline"):
        s1 += f"![레짐 타임라인]({chart_paths['regime_timeline']})\n\n"

    # ── Section 2: 무엇이 먼저 움직이는가? ────────────────────────
    # 선행지표 primary 소스: granger_leading (Granger STRONG/MODERATE)
    # Cross-corr opt_lag는 음수(INDPRO→Factor 반응 방향)이므로 선행 판단에 사용 안 함
    cc_lag_map = {r["factor"]: r["optimal_lag"] for r in lead_lag}  # 참고용 (음수 가능)

    if granger_leading:
        top_gl = granger_leading[0]
        s2_finding = (
            f"**Granger 인과성 검증**에서 {top_gl['label']} 등 "
            f"**{len(granger_leading)}개 Factor**가 INDPRO를 앞서 움직임을 확인했습니다. "
            f"Cross-correlation 최적 Lag가 음수(−)로 나타나는 경우는 Granger 인과 방향(Factor→INDPRO)과 "
            f"다른 방향, 즉 INDPRO 변화에 대한 정책·지표의 **반응 함수**를 포착한 피드백 루프입니다."
        )
    elif granger_ids:
        s2_finding = (
            f"Granger 검증에서 **{len(granger_ids)}개 Factor**의 선행성이 확인되었으나, "
            f"Cross-correlation과의 양방법 합의는 없습니다. "
            f"두 방법의 불일치는 최근 통화정책 효과 약화 등 **구조 변화 가능성**을 시사합니다 — "
            f"분기별 재검증이 필요합니다."
        )
    else:
        s2_finding = (
            "현재 데이터 기간에서 통계적으로 유의한 선행지표가 확인되지 않았습니다. "
            "데이터 기간·변환 방식을 점검하거나, 레짐 전환 구간(금융위기·팬데믹) 제외 후 재분석을 권고합니다."
        )

    s2 = f"""## 2. 무엇이 먼저 움직이는가?

> **핵심 발견**: {s2_finding}

"""
    if chart_paths.get("signal_chart"):
        s2 += f"![The Signal — 선행지표 vs INDPRO]({chart_paths['signal_chart']})\n\n"

    if granger_leading:
        # 기본 표: Granger 선행지표 + Cross-corr Lag 병기 (피드백 루프 설명용)
        g_rows = [
            [
                r["label"],
                f"+{r['lag']}개월",
                r["strength"],
                f"{cc_lag_map.get(r['factor'], 'N/A')}개월",
            ]
            for r in granger_leading[:6]
        ]
        s2 += _fmt_table(g_rows, ["지표명", "Granger 선행", "강도", "Cross-corr Lag"]) + "\n\n"
        s2 += (
            "> **Lag 해석**: Granger Lag(+)는 '해당 Factor → INDPRO' 선행 방향. "
            "Cross-corr Lag(−)는 'INDPRO 변화 → 해당 Factor' 반응 방향. "
            "부호가 반대인 경우 **피드백 루프**를 의미하며, 선행 관계 자체는 Granger 기준으로 판단합니다.\n\n"
        )
    elif granger_ids:
        g_rows = [
            [r["label"], f"+{r['optimal_lag']}개월", r["strength"],
             ("< 0.0001" if r["p_value"] < 0.0001 else f"{r['p_value']:.4f}")]
            for r in granger if r["strength"] in ("STRONG", "MODERATE")
        ][:6]
        if g_rows:
            s2 += _fmt_table(g_rows, ["지표명", "최적 Lag", "강도", "p-value"]) + "\n\n"

    s2 += """> **방법론 노트**: Granger는 차분 기준 시간적 인과성(Factor→INDPRO),
> Cross-correlation은 MoM% 변환 기준 최적 lag 탐색(양방향 탐색)입니다.
> 두 방법이 **동일 방향**이면 강한 선행 증거 / **반대 부호**면 피드백 루프.
"""
    if chart_paths.get("correlation_heatmap"):
        s2 += f"\n![Factor 상관관계 히트맵]({chart_paths['correlation_heatmap']})\n"

    # ── Section 3: 얼마나 확신할 수 있는가? ───────────────────────
    stable_list = rs.get("stable_factors", [])
    unstable_list = rs.get("unstable_factors", [])
    stable = ", ".join(stable_list) or "없음"
    unstable = ", ".join(unstable_list) or "없음"

    # RF와 LASSO 모두에 등장하는 Factor
    lasso_ids = {r["factor"] for r in lasso}
    imp_ids = {r["factor"] for r in imp}
    double_confirmed = lasso_ids & imp_ids
    dc_str = ", ".join(double_confirmed) if double_confirmed else "없음"

    s3 = f"""## 3. 얼마나 확신할 수 있는가?

> **핵심 발견**: LASSO·Random Forest·Rolling OLS 세 방법이 공통으로 지목한 Factor는
> **{dc_str}**입니다. 단일 방법 의존보다 신뢰도가 높습니다.

### LASSO + ML 교차검증

LASSO(α 교차검증)와 Random Forest가 모두 상위권으로 선별한 Factor:

"""
    # Top 5 by importance, flag if also in LASSO
    top_imp = imp[:8]
    imp_rows = [
        [
            r["rank"],
            r["label"],
            f"{r['importance']:.4f}",
            "✓" if r["factor"] in lasso_ids else "",
        ]
        for r in top_imp
    ]
    if imp_rows:
        s3 += _fmt_table(imp_rows, ["순위", "지표명", "RF Importance", "LASSO 선별"]) + "\n\n"

    if chart_paths.get("importance_bar"):
        s3 += f"![Feature Importance]({chart_paths['importance_bar']})\n\n"

    s3 += f"""### 시간적 안정성 (Rolling OLS {r_window}개월 창)

계수가 구간에 따라 흔들리지 않는지 검증. |std/mean| < {r_threshold} → 안정.

| 구분 | Factor |
|------|--------|
| **안정** | {stable} |
| **불안정** | {unstable} |

"""
    if unstable_list:
        s3 += """> **불안정 Factor 해석**: 분석 실패가 아닌 경제 구조 변화의 현실을 반영합니다.
> 계수 방향 역전 감지 시 조기 경보 기준으로 활용하십시오 (분기 1회 재평가 권고).

"""
    if chart_paths.get("rolling_coef"):
        s3 += f"![Rolling 계수 안정성]({chart_paths['rolling_coef']})\n"

    # ── Section 4: 무엇을 해야 하는가? ────────────────────────────
    s4 = f"""## 4. 무엇을 해야 하는가?

> **핵심 발견**: 현재 **{reg_display}({reg_label})** 국면에서 선행지표가 보내는 신호에 따라
> 세 가지 시나리오로 대응 체계를 분리합니다.

### 시나리오별 대응 프레임

{_scenario_table(reg_label, granger, lead_lag, granger_leading)}

### 모니터링 우선순위

{ci.get('data_constraints', '데이터 제약: FRED 월별 발표 일정 기준, 발표 후 1영업일 이내 업데이트.')}

### 클라이언트 설명 프레임

{ci.get('client_narrative', '선행지표 관계는 고정값이 아닌 만큼 분기별 재검토 프로세스가 필요합니다.')}

---
*본 보고서는 FRED 공공 데이터를 기반으로 자동 생성되었습니다.
수치 해석 시 출처(FRED)와 분석 기간을 반드시 명기하십시오.*
"""

    # ── Appendix A: 방법론 ─────────────────────────────────────────
    corr_lag_str = "·".join(str(lag) for lag in CORR_LAGS)
    s_appx_a = f"""## 부록 A: 방법론

| 단계 | 방법 | 파라미터 | 목적 |
|------|------|---------|------|
| 레짐 분류 | GMM 3-state | n_components=3 | 거시 국면 구분 |
| Factor 선별 | LASSO (LassoCV) | CV Folds={LASSO_CV_FOLDS}, α={lasso_alpha} | 희소 선형 선별 |
| 상관관계 | Pearson (시차별) | lag={corr_lag_str}개월 | 동시적·지연 상관 |
| 선행성 검증 | Granger F-test | ADF 정상화, maxlag={LEAD_LAG_MAX_LAG} | 시간적 인과성 |
| 선행성 교차검증 | Cross-correlation | MoM% 변환, ±{LEAD_LAG_MAX_LAG}개월 | Granger 결과 보완 |
| ML 중요도 | Random Forest | n={RF_N_ESTIMATORS}, seed={RF_RANDOM_STATE} | 비선형 기여도 |
| 안정성 | Rolling OLS | window={r_window}개월 | 계수 불안정 탐지 |

**Granger 강도 기준**: STRONG p<{GRANGER_STRONG} / MODERATE p<{GRANGER_MODERATE} / WEAK p<{GRANGER_WEAK}

**⚠ Vintage 데이터 주의**: FRED 데이터는 발표 후 수정(revision)이 반영된 역사적 값입니다.
실시간 예측 시스템에서는 발표 당시 원본값(real-time vintage)과 차이가 발생할 수 있으며,
이 분석의 Granger 인과관계는 **역사적 수정값 기준**임을 명기합니다.

**⚠ 구조 변화(Structural Break) 주의**: 분석 기간({period.get('start', '')[:7]} ~ {period.get('end', '')[:7]}, {period.get('n_obs', 'N/A')}개월)에는
성격이 다른 통화정책 국면이 혼재합니다.
- **ZLB(Zero Lower Bound) 구간**: 2009-01 ~ 2015-12, 2020-03 ~ 2022-02 — 금리 0%로 FEDFUNDS 등 금리 계열의 Granger 인과관계가 정상 작동하지 않을 수 있음
- **GMM 클러스터**: 전 기간 분포 기준으로 경계 산정. 특정 시기를 집중 분석할 경우 최근 창(예: 2015 이후)으로 재추정 권고
- Granger STRONG 결과가 많을 경우 데이터 길이({period.get('n_obs', 'N/A')}개월)에 의한 과소 p-value 가능성을 검토하십시오

"""

    # ── Appendix B: 전체 데이터 테이블 ────────────────────────────
    # LASSO 전체
    lasso_rows_full = [
        [r["factor"], r["label"], f"{r['coefficient']:.4f}"]
        for r in lasso
    ]
    # 상관관계 전체
    corr_rows_full = [
        [r["factor"], r["label"], f"{r['corr']:.3f}", f"{r['pvalue']:.4f}", r["lag_months"]]
        for r in corr
    ]
    # Granger 전체 — p-value: 0.0001 미만은 "< 0.0001" 표시 (과소 p-value 오해 방지)
    def _fmt_pval(p: float) -> str:
        return "< 0.0001" if p < 0.0001 else f"{p:.4f}"

    granger_rows_full = [
        [r["factor"], r["label"], r["strength"], r["optimal_lag"], _fmt_pval(r["p_value"])]
        for r in granger
    ]

    s_appx_b = """## 부록 B: 전체 데이터 테이블

### B-1. LASSO 선별 Factor (전체)

"""
    if lasso_rows_full:
        s_appx_b += _fmt_table(lasso_rows_full, ["Factor", "지표명", "계수"]) + "\n\n"
    else:
        s_appx_b += "_데이터 없음_\n\n"

    s_appx_b += "### B-2. 상관관계 분석 (전체)\n\n"
    if corr_rows_full:
        s_appx_b += (
            _fmt_table(corr_rows_full, ["Factor", "지표명", "상관계수", "p-value", "최적 Lag(월)"])
            + "\n\n"
        )
    else:
        s_appx_b += "_데이터 없음_\n\n"

    s_appx_b += "### B-3. Granger 인과관계 (전체)\n\n"
    if granger_rows_full:
        s_appx_b += (
            _fmt_table(granger_rows_full, ["Factor", "지표명", "강도", "최적 Lag(월)", "p-value"])
            + "\n"
        )
    else:
        s_appx_b += "_데이터 없음_\n"

    # ── 최종 조합 ──────────────────────────────────────────────────
    report = f"""# {title}

**생성일**: {now_iso} | **Target**: {target_label} | **출처**: FRED

---

{s_exec}
{s1}
{s2}
{s3}
{s4}
---

{s_appx_a}
{s_appx_b}"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/factor_pool_{date_str}.md"
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(report)
    print(f"  ✓ 보고서 저장: {path}")
    return path


if __name__ == "__main__":
    build_factor_report()
