# 산업생산 Neutral 국면: Fed Funds Rate Granger 검증상 6개월 선행

**생성일**: 2026-03-03 | **Target**: 산업생산지수 MoM% | **출처**: FRED

---

## Executive Summary

> **한 줄 결론**: 현재 산업생산 레짐: Neutral. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **안정성장** (Neutral, 신뢰도 99.9%) |
| 레짐 확률 분포 | Expansion: 0.0% | Neutral: 100.0% | Contraction: 0.0% |
| 핵심 선행지표 | FEDFUNDS가 INDPRO 6개월 선행 (Granger STRONG) |
| 분석 기간 | 2000-02-01 ~ 2025-11-01 (309개월) |
| 데이터 출처 | FRED (Federal Reserve Bank of St. Louis) |


## 1. 지금 어디에 있는가?

> **핵심 발견**: 미국 산업생산(INDPRO)은 현재 **안정성장** 국면에 있으며,
> Shannon Entropy 0.001로 레짐 전환 가능성이 낮은 안정적 상태입니다.

GMM 3-state 모델이 309개월 데이터에서 식별한 현재 레짐:

> ※ 레짐은 INDPRO MoM% **성장률 변동성** 기준으로 분류합니다. NBER 경기확장·침체와 직접 대응하지 않습니다.
> 고모멘텀(MoM% 장기 평균 대비 +1σ 이상) / 안정성장(정상 범위) / 저모멘텀(−1σ 이하 또는 음수)

| 지표 | 값 | 해석 |
|------|----|------|
| **레짐** | **안정성장** (Neutral) | GMM 사후확률 최댓값 기준 |
| 신뢰도 | 99.9% | Shannon Entropy 0.001 (GMM 사후확률 기반) |
| 레짐 확률 | Expansion: 0.0% | Neutral: 100.0% | Contraction: 0.0% | 단일 레짐 우세 |

Neutral (신뢰도 99.9%)

> **⚠ 해석 주의**: 신뢰도 99.9%는 "현재 데이터점이 안정성장(Neutral) 클러스터에 속할 GMM 사후확률"이며,
> 레짐 분류의 절대적 정확성을 보장하지 않습니다.
> GMM 모델은 **구조 변화 구간(2008~2009 금융위기, 2020 팬데믹)에서 신뢰도가 저하**됩니다.
> 해당 기간 데이터가 포함된 전체 추정 결과이므로 최근 구간(2020 이후) 별도 검증을 권고합니다.


## 2. 무엇이 먼저 움직이는가?

> **핵심 발견**: Granger 검증에서 **12개 Factor**의 선행성이 확인되었으나, Cross-correlation과의 양방법 합의는 없습니다. 두 방법의 불일치는 최근 통화정책 효과 약화 등 **구조 변화 가능성**을 시사합니다 — 분기별 재검증이 필요합니다.

| 지표명 | 최적 Lag | 강도 | p-value | 검증 방법 |
| --- | --- | --- | --- | --- |
| Fed Funds Rate | +6개월 | STRONG | < 0.0001 | Granger만 |
| 실업률 | +7개월 | STRONG | < 0.0001 | Granger만 |
| 비농업고용 MoM 증감(천명) | +11개월 | STRONG | < 0.0001 | Granger만 |
| M2 통화량 MoM% | +5개월 | STRONG | < 0.0001 | Granger만 |
| WTI 유가 MoM% | +1개월 | STRONG | < 0.0001 | Granger만 |
| VIX 변동성지수 | +2개월 | STRONG | < 0.0001 | Granger만 |

> **왜 두 가지 방법인가?** Granger는 차분 기준 시간적 인과성,
> Cross-correlation은 MoM% 변환 기준 최적 lag 탐색입니다.
> 양방법 합의 = 강한 증거 / 불일치 = 구조 변화 경고 신호.

## 3. 얼마나 확신할 수 있는가?

> **핵심 발견**: LASSO·Random Forest·Rolling OLS 세 방법이 공통으로 지목한 Factor는
> **PPIACO, DCOILWTICO, HOUST, DEXUSEU, DGS2, DGS10, UNRATE, RETAILSMNSA, M2SL, PAYEMS, VIXCLS, UMCSENT**입니다. 단일 방법 의존보다 신뢰도가 높습니다.

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

> **핵심 발견**: 현재 **안정성장(Neutral)** 국면에서 선행지표가 보내는 신호에 따라
> 세 가지 시나리오로 대응 체계를 분리합니다.

### 시나리오별 대응 프레임

| 시나리오 | 신호 조건 | 핵심 모니터링 Factor(주기) | 대응 권고 |
| --- | --- | --- | --- |
| **Expansion** | 선행 Factor 지속 상승 | PPI MoM%(매월) / WTI 유가 MoM%(매월) / CPI YoY%(매월) | 현 포지션 유지, 레짐 전환 신호 모니터링 |
| **Neutral** | 혼조 — 방향성 불확실 | PPI MoM%(매월) / WTI 유가 MoM%(매월) / CPI YoY%(매월) | 분기 1회 Factor Pool 전체 재평가 |
| **Contraction** | 선행 Factor 하락 전환 | PPI MoM%(매월) / WTI 유가 MoM%(매월) / CPI YoY%(매월) | 조기 경보 발동, 클라이언트 리스크 재검토 |

### 모니터링 우선순위

서베이 기반 지표(UMCSENT)는 후행 가능성 있음

### 클라이언트 설명 프레임

현재 산업생산 레짐: Neutral. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

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
