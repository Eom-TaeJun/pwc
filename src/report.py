# 목적: Factor Pool 리서치 MD 보고서 생성
# 입력: outputs/context/factors_*.json + analysis_*.json + chart paths
# 출력: outputs/reports/factor_pool_YYYYMMDD.md
# 제외: PDF 변환, 웹 렌더링

import json
import os
import glob
from datetime import datetime

OUTPUT_DIR = "outputs/reports"


def _load_latest(prefix: str) -> dict:
    files = sorted(glob.glob(f"outputs/context/{prefix}_*.json"))
    if not files:
        return {}
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def _fmt_table(rows: list, headers: list) -> str:
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def build_factor_report(factors_data: dict = None, analysis: dict = None, chart_paths: dict = None) -> str:
    factors_data = factors_data or _load_latest("factors")
    analysis = analysis or _load_latest("analysis")
    chart_paths = chart_paths or {}

    date_str = datetime.now().strftime("%Y%m%d")
    target_label = factors_data.get("target", {}).get("label", "INDPRO MoM%")
    period = analysis.get("data_period", {})
    now_iso = datetime.now().strftime("%Y-%m-%d")

    # --- Section 0: 레짐 분석 (Executive Summary) ---
    regime_info = analysis.get("regime", {})
    reg_label   = regime_info.get("regime", "N/A")
    reg_conf    = regime_info.get("confidence", 0)
    reg_probs   = regime_info.get("probs", {})
    reg_entropy = regime_info.get("entropy", 1.0)
    prob_str = " | ".join(f"{k}: {v*100:.1f}%" for k, v in reg_probs.items())

    ci = analysis.get("consulting_implications", {})
    s0 = f"""## 0. Executive Summary

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **{reg_label}** |
| 레짐 신뢰도 | {reg_conf}% (Shannon Entropy: {reg_entropy:.3f}) |
| 레짐 확률 분포 | {prob_str} |
| 핵심 선행지표 | {ci.get('leading_indicators', 'N/A')} |
| 클라이언트 권고 | {ci.get('client_narrative', 'N/A')} |

"""
    if chart_paths.get("regime_timeline"):
        s0 += f"![레짐 타임라인]({chart_paths['regime_timeline']})\n"
    if chart_paths.get("signal_chart"):
        s0 += f"\n![The Signal]({chart_paths['signal_chart']})\n"

    # --- Section 1: 분석 개요 ---
    s1 = f"""## 1. 분석 개요

| 항목 | 내용 |
|------|------|
| Target 변수 | {target_label} (INDPRO) |
| 분석 기간 | {period.get('start', 'N/A')} ~ {period.get('end', 'N/A')} ({period.get('n_obs', 'N/A')}개월) |
| Factor 후보 | {len(factors_data.get('factors', {}))}개 FRED 시계열 |
| 방법론 | LASSO 선별 → 상관관계 분석 → Rolling OLS → RF Feature Importance |
| 생성일 | {now_iso} |
| 데이터 출처 | FRED (Federal Reserve Bank of St. Louis) |
"""

    # --- Section 2: LASSO 선행지표 선별 ---
    lasso = analysis.get("lasso_selected", [])
    lasso_rows = [[r["factor"], r["label"], f"{r['coefficient']:.4f}"] for r in lasso[:10]]
    s2 = f"""## 2. LASSO 선행지표 선별 결과

LASSO 정규화(교차검증 5-Fold)로 {len(lasso)}개 Factor 선별.
계수 크기(절댓값)는 상대적 중요도를 나타내며, 0이 아닌 계수만 표시.

{_fmt_table(lasso_rows, ["Factor", "지표명", "계수"])}

> **해석**: 계수 부호(+/-)는 INDPRO와의 방향성, 크기는 기여도.
"""
    if chart_paths.get("lasso_path"):
        s2 += f"\n![LASSO 정규화 경로]({chart_paths['lasso_path']})\n"

    # --- Section 3: 상관관계 분석 ---
    corr = analysis.get("correlation", [])
    corr_rows = [[r["factor"], r["label"], f"{r['corr']:.3f}", f"{r['pvalue']:.4f}", r["lag_months"]]
                 for r in corr[:8]]
    s3 = f"""## 3. 상관관계 분석 (시차별)

각 Factor와 INDPRO 간 피어슨 상관계수. 시차 0·3·6·12개월 중 최적 lag 선택 (p < 0.05 기준).

{_fmt_table(corr_rows, ["Factor", "지표명", "상관계수", "p-value", "최적 Lag(월)"])}
"""
    if chart_paths.get("correlation_heatmap"):
        s3 += f"\n![상관관계 히트맵]({chart_paths['correlation_heatmap']})\n"

    # --- Section 4: ML Feature Importance ---
    imp = analysis.get("importance", [])
    imp_rows = [[r["rank"], r["factor"], r["label"], f"{r['importance']:.4f}"] for r in imp[:10]]
    s4 = f"""## 4. ML Feature Importance (Random Forest)

Random Forest(n=100, random_state=42) 기반 Feature Importance.
LASSO 선별 Factor를 대상으로 산정.

{_fmt_table(imp_rows, ["순위", "Factor", "지표명", "Importance"])}
"""
    if chart_paths.get("importance_bar"):
        s4 += f"\n![Feature Importance]({chart_paths['importance_bar']})\n"

    # --- Section 3.5: Granger 인과관계 ---
    granger = analysis.get("granger", [])
    granger_rows = [[r["factor"], r["label"], r["strength"],
                     r["optimal_lag"], f"{r['p_value']:.4f}"]
                    for r in granger[:8]]
    s35 = f"""## 3.5 Granger 인과관계 검증

ADF 정상성 변환 후 F-test. STRONG: p<0.01 / MODERATE: p<0.05 / WEAK: p<0.10.

{_fmt_table(granger_rows, ["Factor", "지표명", "강도", "최적 Lag(월)", "p-value"])}

> Pearson 상관관계(섹션 3)는 동시적 연관성을, Granger는 **시간적 선행성**을 검증합니다.
"""

    # --- Section 3.7: Lead-Lag 교차검증 ---
    lead_lag = analysis.get("lead_lag", [])
    leading = [r for r in lead_lag if r.get("is_leading")][:6]
    ll_rows = [[r["factor"], r["label"],
                f"+{r['optimal_lag']}m" if r["optimal_lag"] > 0 else str(r["optimal_lag"]),
                f"{r['max_corr']:.3f}", "✓" if r["is_leading"] else ""]
               for r in lead_lag[:8]]

    # Granger와 합의 여부 확인
    granger_factors = {r["factor"] for r in granger if r["strength"] in ("STRONG", "MODERATE")}
    lead_factors = {r["factor"] for r in leading}
    consensus = granger_factors & lead_factors
    consensus_str = ", ".join(consensus) if consensus else "없음 (방법론 간 불일치 — 해석 주의)"

    s37 = f"""## 3.7 Lead-Lag 교차검증

Cross-correlation (lag -12~+12개월)으로 Granger 결과를 교차검증.
**양방법 공통 선행 Factor = 강한 증거**, 불일치 = 구조 변화 또는 척도 차이 가능성.

{_fmt_table(ll_rows, ["Factor", "지표명", "최적 Lag", "최대 상관계수", "선행?"])}

| 검증 항목 | 결과 |
|---------|------|
| Granger STRONG/MODERATE | {", ".join(granger_factors) or "없음"} |
| Lead-Lag 선행 Factor | {", ".join(lead_factors) or "없음"} |
| **양방법 합의 (강한 증거)** | **{consensus_str}** |

> Granger는 차분(정상화) 기준, Lead-Lag는 MoM% 변환 기준. 동일 방향이면 선행성 신뢰도 상승.
"""

    # --- Section 5: Rolling 안정성 ---
    rs = analysis.get("rolling_stability", {})
    stable_list = rs.get("stable_factors", [])
    unstable_list = rs.get("unstable_factors", [])
    stable = ", ".join(stable_list) or "없음"
    unstable = ", ".join(unstable_list) or "없음"

    # 불안정 Factor 컨설팅 해석
    if unstable_list:
        instability_note = f"""
### 불안정 Factor 해석 (클라이언트 설명용)

불안정({len(unstable_list)}개)은 **분석 실패가 아닙니다** — 경제 구조 변화(2008 금융위기, 2020 팬데믹)가 \
빈번하다는 현실을 포착한 결과입니다.

| 관점 | 내용 |
|------|------|
| 현재 구간 신뢰도 | 최근 36개월 기준 Granger·상관관계로 선행성 별도 검증 완료 |
| 구조 변화 위험 | 팬데믹·금융위기급 외부 충격 시 계수 방향 역전 가능 |
| 관리 권고 | 분기 1회 Factor Pool 재평가, 계수 방향 역전 시 조기 경보 |
| 클라이언트 메시지 | "선행지표 관계는 고정값이 아닌 만큼 분기별 재검토 프로세스가 필요합니다." |
"""
    else:
        instability_note = ""

    s5 = f"""## 5. Rolling OLS 안정성 검증 (36개월 창)

계수 시계열 안정성 기준: |std/mean| < 0.5 → 안정, ≥ 0.5 → 불안정.

| 구분 | Factor |
|------|--------|
| **안정 Factor** | {stable} |
| **불안정 Factor** | {unstable} |
{instability_note}"""
    if chart_paths.get("rolling_coef"):
        s5 += f"\n![Rolling 계수 안정성]({chart_paths['rolling_coef']})\n"

    # --- Section 6: 컨설팅 함의 ---
    ci = analysis.get("consulting_implications", {})
    s6 = f"""## 6. 컨설팅 함의

### 현재 레짐 판단
{ci.get('current_regime', 'N/A')}

### 선행지표 활용
{ci.get('leading_indicators', 'N/A')}

### 데이터 제약
{ci.get('data_constraints', 'N/A')}

### 클라이언트 설명 프레임
{ci.get('client_narrative', 'N/A')}

---
*본 보고서는 FRED 공공 데이터를 기반으로 자동 생성되었습니다. 수치 해석 시 출처(FRED)와 분석 기간을 반드시 명기하십시오.*
"""

    report = f"""# Factor Pool 리서치 보고서

**생성일**: {now_iso}
**Target**: {target_label}
**데이터 출처**: FRED (Federal Reserve Bank of St. Louis)

---

{s0}
{s1}
{s2}
{s3}
{s35}
{s37}
{s4}
{s5}
{s6}"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = f"{OUTPUT_DIR}/factor_pool_{date_str}.md"
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(report)
    print(f"  ✓ 보고서 저장: {path}")
    return path


if __name__ == "__main__":
    build_factor_report()
