# 산업생산 Expansion 국면: Fed Funds Rate Granger 검증상 6개월 선행

**생성일**: 2026-03-03 | **Target**: 산업생산지수 MoM% | **출처**: FRED

---

## Executive Summary

> **한 줄 결론**: 현재 산업생산 레짐: Expansion. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **고모멘텀** (Expansion, 신뢰도 37.4%) |
| 레짐 확률 분포 | Neutral: 44.8% | Contraction: 0.0% | Expansion: 55.2% |
| 핵심 선행지표 | FEDFUNDS가 INDPRO 6개월 선행 (Granger STRONG) |
| 분석 기간 | 2000-02-01 ~ 2025-11-01 (309개월) |
| 데이터 출처 | FRED (Federal Reserve Bank of St. Louis) |


## 1. 지금 어디에 있는가?

> **핵심 발견**: 미국 산업생산(INDPRO)은 현재 **고모멘텀** 국면에 있으며,
> Shannon Entropy 0.626로 레짐 전환 가능성이 낮은 안정적 상태입니다.

GMM 3-state 모델이 309개월 데이터에서 식별한 현재 레짐:

> ※ 레짐은 INDPRO MoM% **성장률 변동성** 기준으로 분류합니다. NBER 경기확장·침체와 직접 대응하지 않습니다.
> 고모멘텀(MoM% 장기 평균 대비 +1σ 이상) / 안정성장(정상 범위) / 저모멘텀(−1σ 이하 또는 음수)

| 지표 | 값 | 해석 |
|------|----|------|
| **레짐** | **고모멘텀** (Expansion) | GMM 사후확률 최댓값 기준 |
| 신뢰도 | 37.4% | Shannon Entropy 0.626 (GMM 사후확률 기반) |
| 레짐 확률 | Neutral: 44.8% | Contraction: 0.0% | Expansion: 55.2% | 복수 레짐 경합 |

Expansion (신뢰도 37.4%)

> **⚠ 해석 주의**: 신뢰도 37.4%는 "현재 데이터점이 고모멘텀(Expansion) 클러스터에 속할 GMM 사후확률"이며,
> 레짐 분류의 절대적 정확성을 보장하지 않습니다.
> GMM 모델은 **구조 변화 구간(2008~2009 금융위기, 2020 팬데믹)에서 신뢰도가 저하**됩니다.
> 해당 기간 데이터가 포함된 전체 추정 결과이므로 최근 구간(2020 이후) 별도 검증을 권고합니다.


## 2. 무엇이 먼저 움직이는가?

> **핵심 발견**: **Granger 인과성 검증**에서 Fed Funds Rate 등 **12개 Factor**가 INDPRO를 앞서 움직임을 확인했습니다. Cross-correlation 최적 Lag가 음수(−)로 나타나는 경우는 Granger 인과 방향(Factor→INDPRO)과 다른 방향, 즉 INDPRO 변화에 대한 정책·지표의 **반응 함수**를 포착한 피드백 루프입니다.

| 지표명 | Granger 선행 | 강도 | Cross-corr Lag |
| --- | --- | --- | --- |
| Fed Funds Rate | +6개월 | STRONG | -11개월 |
| 실업률 | +7개월 | STRONG | 0개월 |
| 비농업고용 MoM 증감(천명) | +11개월 | STRONG | -12개월 |
| M2 통화량 MoM% | +5개월 | STRONG | 0개월 |
| WTI 유가 MoM% | +1개월 | STRONG | -10개월 |
| VIX 변동성지수 | +2개월 | STRONG | -8개월 |

> **Lag 해석**: Granger Lag(+)는 '해당 Factor → INDPRO' 선행 방향. Cross-corr Lag(−)는 'INDPRO 변화 → 해당 Factor' 반응 방향. 부호가 반대인 경우 **피드백 루프**를 의미하며, 선행 관계 자체는 Granger 기준으로 판단합니다.

> **방법론 노트**: Granger는 차분 기준 시간적 인과성(Factor→INDPRO),
> Cross-correlation은 MoM% 변환 기준 최적 lag 탐색(양방향 탐색)입니다.
> 두 방법이 **동일 방향**이면 강한 선행 증거 / **반대 부호**면 피드백 루프.

## 3. 얼마나 확신할 수 있는가?

> **핵심 발견**: LASSO·Random Forest·Rolling OLS 세 방법이 공통으로 지목한 Factor는
> **RETAILSMNSA, DEXUSEU, DGS10, UNRATE, DGS2, VIXCLS, DCOILWTICO, M2SL, PAYEMS, UMCSENT, HOUST, PPIACO**입니다. 단일 방법 의존보다 신뢰도가 높습니다.

### LASSO + ML 교차검증

LASSO(α 교차검증)와 Random Forest가 모두 상위권으로 선별한 Factor:

| 순위 | 지표명 | RF Importance | LASSO 선별 |
| --- | --- | --- | --- |
| 1 | 비농업고용 MoM 증감(천명) | 0.2666 | ✓ |
| 2 | M2 통화량 MoM% | 0.2268 | ✓ |
| 3 | 실업률 | 0.1194 | ✓ |
| 4 | 주택착공 MoM% | 0.1046 | ✓ |
| 5 | WTI 유가 MoM% | 0.0627 | ✓ |
| 6 | PPI MoM% | 0.0449 | ✓ |
| 7 | 2Y Treasury Yield | 0.0418 | ✓ |
| 8 | 소매판매 MoM% | 0.0357 | ✓ |

![Feature Importance](outputs/charts/importance_bar_20260303.png)

### 시간적 안정성 (Rolling OLS 36개월 창)

계수가 구간에 따라 흔들리지 않는지 검증. |std/mean| < 0.5 → 안정.

| 구분 | Factor |
|------|--------|
| **안정** | 없음 |
| **불안정** | PAYEMS, UNRATE, HOUST, VIXCLS, DGS2 |

> **불안정 Factor 해석**: 분석 실패가 아닌 경제 구조 변화의 현실을 반영합니다.
> 계수 방향 역전 감지 시 조기 경보 기준으로 활용하십시오 (분기 1회 재평가 권고).


## 4. 무엇을 해야 하는가?

> **핵심 발견**: 현재 **고모멘텀(Expansion)** 국면에서 선행지표가 보내는 신호에 따라
> 세 가지 시나리오로 대응 체계를 분리합니다.

### 시나리오별 대응 프레임

| 시나리오 | 신호 조건 | 핵심 모니터링 Factor(주기) | 대응 권고 |
| --- | --- | --- | --- |
| **Expansion** | 선행 Factor 지속 상승 | 소매판매 MoM%(분기) / 10Y Treasury Yield(매월) / 실업률(분기) | 현 포지션 유지, 레짐 전환 신호 모니터링 |
| **Neutral** | 혼조 — 방향성 불확실 | 소매판매 MoM%(분기) / 10Y Treasury Yield(매월) / 실업률(분기) | 분기 1회 Factor Pool 전체 재평가 |
| **Contraction** | 선행 Factor 하락 전환 | 소매판매 MoM%(분기) / 10Y Treasury Yield(매월) / 실업률(분기) | 조기 경보 발동, 클라이언트 리스크 재검토 |

### 모니터링 우선순위

서베이 기반 지표(UMCSENT)는 후행 가능성 있음

### 클라이언트 설명 프레임

현재 산업생산 레짐: Expansion. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

---
*본 보고서는 FRED 공공 데이터를 기반으로 자동 생성되었습니다.
수치 해석 시 출처(FRED)와 분석 기간을 반드시 명기하십시오.*

---

## 부록 A: 방법론

| 단계 | 방법 | 파라미터 | 목적 |
|------|------|---------|------|
| 레짐 분류 | GMM 3-state | n_components=3 | 거시 국면 구분 |
| Factor 선별 | LASSO (LassoCV) | CV Folds=5, α=0.020252 | 희소 선형 선별 |
| 상관관계 | Pearson (시차별) | lag=0·3·6·12개월 | 동시적·지연 상관 |
| 선행성 검증 | Granger F-test | ADF 정상화, maxlag=12 | 시간적 인과성 |
| 선행성 교차검증 | Cross-correlation | MoM% 변환, ±12개월 | Granger 결과 보완 |
| ML 중요도 | Random Forest | n=100, seed=42 | 비선형 기여도 |
| 안정성 | Rolling OLS | window=36개월 | 계수 불안정 탐지 |

**Granger 강도 기준**: STRONG p<0.01 / MODERATE p<0.05 / WEAK p<0.1

**⚠ Vintage 데이터 주의**: FRED 데이터는 발표 후 수정(revision)이 반영된 역사적 값입니다.
실시간 예측 시스템에서는 발표 당시 원본값(real-time vintage)과 차이가 발생할 수 있으며,
이 분석의 Granger 인과관계는 **역사적 수정값 기준**임을 명기합니다.

**⚠ 구조 변화(Structural Break) 주의**: 분석 기간(2000-02 ~ 2025-11, 309개월)에는
성격이 다른 통화정책 국면이 혼재합니다.
- **ZLB(Zero Lower Bound) 구간**: 2009-01 ~ 2015-12, 2020-03 ~ 2022-02 — 금리 0%로 FEDFUNDS 등 금리 계열의 Granger 인과관계가 정상 작동하지 않을 수 있음
- **GMM 클러스터**: 전 기간 분포 기준으로 경계 산정. 특정 시기를 집중 분석할 경우 최근 창(예: 2015 이후)으로 재추정 권고
- Granger STRONG 결과가 많을 경우 데이터 길이(309개월)에 의한 과소 p-value 가능성을 검토하십시오


## 부록 B: 전체 데이터 테이블

### B-1. LASSO 선별 Factor (전체)

| Factor | 지표명 | 계수 |
| --- | --- | --- |
| PAYEMS | 비농업고용 MoM 증감(천명) | 0.8052 |
| UNRATE | 실업률 | 0.2204 |
| HOUST | 주택착공 MoM% | 0.1597 |
| VIXCLS | VIX 변동성지수 | -0.0701 |
| DGS2 | 2Y Treasury Yield | 0.0662 |
| RETAILSMNSA | 소매판매 MoM% | 0.0549 |
| M2SL | M2 통화량 MoM% | -0.0540 |
| PPIACO | PPI MoM% | 0.0343 |
| UMCSENT | 미시간 소비자심리 | 0.0280 |
| DGS10 | 10Y Treasury Yield | 0.0179 |
| DEXUSEU | USD/EUR 환율 | -0.0172 |
| DCOILWTICO | WTI 유가 MoM% | 0.0097 |

### B-2. 상관관계 분석 (전체)

| Factor | 지표명 | 상관계수 | p-value | 최적 Lag(월) |
| --- | --- | --- | --- | --- |
| PAYEMS | 비농업고용 MoM 증감(천명) | 0.779 | 0.0000 | 0 |
| M2SL | M2 통화량 MoM% | -0.391 | 0.0000 | 0 |
| DCOILWTICO | WTI 유가 MoM% | 0.371 | 0.0000 | 0 |
| HOUST | 주택착공 MoM% | 0.360 | 0.0000 | 0 |
| PPIACO | PPI MoM% | 0.280 | 0.0000 | 0 |
| VIXCLS | VIX 변동성지수 | -0.239 | 0.0000 | 0 |
| UNRATE | 실업률 | 0.181 | 0.0014 | 3 |
| RETAILSMNSA | 소매판매 MoM% | 0.146 | 0.0102 | 0 |
| FEDFUNDS | Fed Funds Rate | -0.117 | 0.0442 | 12 |

### B-3. Granger 인과관계 (전체)

| Factor | 지표명 | 강도 | 최적 Lag(월) | p-value |
| --- | --- | --- | --- | --- |
| FEDFUNDS | Fed Funds Rate | STRONG | 6 | < 0.0001 |
| UNRATE | 실업률 | STRONG | 7 | < 0.0001 |
| PAYEMS | 비농업고용 MoM 증감(천명) | STRONG | 11 | < 0.0001 |
| M2SL | M2 통화량 MoM% | STRONG | 5 | < 0.0001 |
| DCOILWTICO | WTI 유가 MoM% | STRONG | 1 | < 0.0001 |
| VIXCLS | VIX 변동성지수 | STRONG | 2 | < 0.0001 |
| DGS2 | 2Y Treasury Yield | STRONG | 2 | < 0.0001 |
| PPIACO | PPI MoM% | STRONG | 1 | < 0.0001 |
| DGS10 | 10Y Treasury Yield | STRONG | 1 | 0.0001 |
| RETAILSMNSA | 소매판매 MoM% | MODERATE | 12 | 0.0114 |
| UMCSENT | 미시간 소비자심리 | MODERATE | 2 | 0.0225 |
| CPIAUCSL | CPI YoY% | MODERATE | 1 | 0.0376 |
| DEXUSEU | USD/EUR 환율 | WEAK | 7 | 0.0626 |
| HOUST | 주택착공 MoM% | WEAK | 2 | 0.0814 |
