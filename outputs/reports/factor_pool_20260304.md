# 산업생산 Expansion 국면: Fed Funds Rate Granger 검증상 6개월 선행

**생성일**: 2026-03-04 | **Target**: 산업생산지수 MoM% | **출처**: FRED

---

## Executive Summary

> **한 줄 결론**: 현재 산업생산 레짐: Expansion. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **고모멘텀** (Expansion, 신뢰도 37.4%) |
| 레짐 확률 분포 | Neutral: 44.8% | Contraction: 0.0% | Expansion: 55.2% |
| **레짐 모멘텀** | ▲ 안정 Expansion (최근 6개월 중 4회) (`E → N → E → N → E → E`) |
| **선행지표 현재 신호** | Fed Funds Rate ↓(6M 선행), 실업률 ↓(7M 선행), 비농업고용 MoM 증감(천명) ↑(11M 선행) |
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

> **핵심 발견**: **Granger 인과성 검증**에서 Fed Funds Rate 등 **13개 Factor**가 INDPRO를 앞서 움직임을 확인했습니다. Cross-correlation 최적 Lag가 음수(−)로 나타나는 경우는 Granger 인과 방향(Factor→INDPRO)과 다른 방향, 즉 INDPRO 변화에 대한 정책·지표의 **반응 함수**를 포착한 피드백 루프입니다.

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
> **PAYEMS, RETAILSMNSA, DEXUSEU, VIXCLS, TCU, M2SL, PPIACO, DCOILWTICO, DGS2, HOUST, UMCSENT, DGS10, UNRATE**입니다. 단일 방법 의존보다 신뢰도가 높습니다.

### LASSO + ML 교차검증

LASSO(α 교차검증)와 Random Forest가 모두 상위권으로 선별한 Factor:

| 순위 | 지표명 | RF Importance | LASSO 선별 |
| --- | --- | --- | --- |
| 1 | 비농업고용 MoM 증감(천명) | 0.2490 | ✓ |
| 2 | M2 통화량 MoM% | 0.2084 | ✓ |
| 3 | 실업률 | 0.1197 | ✓ |
| 4 | 주택착공 MoM% | 0.1054 | ✓ |
| 5 | WTI 유가 MoM% | 0.0671 | ✓ |
| 6 | PPI MoM% | 0.0477 | ✓ |
| 7 | 설비가동률(%) | 0.0419 | ✓ |
| 8 | 2Y Treasury Yield | 0.0406 | ✓ |

![Feature Importance](outputs/charts/importance_bar_20260304.png)

### 시간적 안정성 (Rolling OLS 36개월 창)

계수가 구간에 따라 흔들리지 않는지 검증. |std/mean| < 0.5 → 안정.

| 구분 | Factor |
|------|--------|
| **안정** | 없음 |
| **불안정** | PAYEMS, UNRATE, HOUST, VIXCLS, M2SL |

| Factor | |std/mean| (CV) | 판정 |
| --- | --- | --- |
| 비농업고용 MoM 증감(천명) | 1.133 | ✗ 불안정 |
| M2 통화량 MoM% | 1.384 | ✗ 불안정 |
| 주택착공 MoM% | 1.416 | ✗ 불안정 |
| 실업률 | 2.775 | ✗ 불안정 |
| VIX 변동성지수 | 4.156 | ✗ 불안정 |

> **불안정 Factor 해석**: 분석 실패가 아닌 경제 구조 변화의 현실을 반영합니다.
> 계수 방향 역전 감지 시 조기 경보 기준으로 활용하십시오 (분기 1회 재평가 권고).


## 4. 무엇을 해야 하는가?

> **핵심 발견**: 현재 **고모멘텀(Expansion)** 국면에서 선행지표가 보내는 신호에 따라
> 세 가지 시나리오로 대응 체계를 분리합니다.
> 레짐 모멘텀: ▲ 안정 Expansion (최근 6개월 중 4회)

### 선행지표 현재 방향 신호

| 선행지표 | Lag | 현재 방향 | 시나리오 함의 |
| --- | --- | --- | --- |
| Fed Funds Rate | +6M | ↓ | Neutral 전환 경계 |
| 실업률 | +7M | ↓ | Neutral 전환 경계 |
| 비농업고용 MoM 증감(천명) | +11M | ↑ | Expansion 지속 신호 |
| M2 통화량 MoM% | +5M | ↑ | Expansion 지속 신호 |
| WTI 유가 MoM% | +1M | ↑ | Expansion 지속 신호 |

> ↑ = 최근 3개월 상승 추세 / ↓ = 하락 추세 (Factor 원래 단위 기준)

### 시나리오별 대응 프레임

| 시나리오 | 신호 조건 | 핵심 모니터링 Factor(주기) | 대응 권고 |
| --- | --- | --- | --- |
| **Expansion** | 선행 Factor 지속 상승 | 비농업고용 MoM 증감(천명)(분기) / VIX 변동성지수(매월) / 설비가동률(%)(분기) | 현 포지션 유지, 레짐 전환 신호 모니터링 |
| **Neutral** | 혼조 — 방향성 불확실 | 비농업고용 MoM 증감(천명)(분기) / VIX 변동성지수(매월) / 설비가동률(%)(분기) | 분기 1회 Factor Pool 전체 재평가 |
| **Contraction** | 선행 Factor 하락 전환 | 비농업고용 MoM 증감(천명)(분기) / VIX 변동성지수(매월) / 설비가동률(%)(분기) | 조기 경보 발동, 클라이언트 리스크 재검토 |

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
| PAYEMS | 비농업고용 MoM 증감(천명) | 0.7992 |
| UNRATE | 실업률 | 0.2438 |
| HOUST | 주택착공 MoM% | 0.1593 |
| VIXCLS | VIX 변동성지수 | -0.0649 |
| M2SL | M2 통화량 MoM% | -0.0571 |
| RETAILSMNSA | 소매판매 MoM% | 0.0543 |
| DGS2 | 2Y Treasury Yield | 0.0532 |
| TCU | 설비가동률(%) | 0.0430 |
| DEXUSEU | USD/EUR 환율 | -0.0347 |
| PPIACO | PPI MoM% | 0.0309 |
| DGS10 | 10Y Treasury Yield | 0.0182 |
| UMCSENT | 미시간 소비자심리 | 0.0180 |
| DCOILWTICO | WTI 유가 MoM% | 0.0164 |

### B-2. 상관관계 분석 (전체)

| Factor | 지표명 | 상관계수 | p-value | 최적 Lag(월) |
| --- | --- | --- | --- | --- |
| PAYEMS | 비농업고용 MoM 증감(천명) | 0.779 | 0.0000 | 0 |
| M2SL | M2 통화량 MoM% | -0.391 | 0.0000 | 0 |
| DCOILWTICO | WTI 유가 MoM% | 0.371 | 0.0000 | 0 |
| HOUST | 주택착공 MoM% | 0.360 | 0.0000 | 0 |
| PPIACO | PPI MoM% | 0.280 | 0.0000 | 0 |
| VIXCLS | VIX 변동성지수 | -0.239 | 0.0000 | 0 |
| TCU | 설비가동률(%) | -0.189 | 0.0011 | 12 |
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
| TCU | 설비가동률(%) | STRONG | 10 | 0.0016 |
| RETAILSMNSA | 소매판매 MoM% | MODERATE | 12 | 0.0114 |
| UMCSENT | 미시간 소비자심리 | MODERATE | 2 | 0.0225 |
| CPIAUCSL | CPI YoY% | MODERATE | 1 | 0.0376 |
| DEXUSEU | USD/EUR 환율 | WEAK | 7 | 0.0626 |
| HOUST | 주택착공 MoM% | WEAK | 2 | 0.0814 |

## 부록 C: 현재 사이클 집중 분석

> **분석 기간**: 2000-02 ~ 2025-11 (309개월)
> **방법**: ruptures PELT (rbf), pen=15.0, min_size=6개월
> Granger maxlag=6, Rolling 창=24개월.
>
> 고정 캘린더 창(예: "최근 60개월") 대신 **PELT 구조 변화 탐지로 정의된 현재 사이클 세그먼트**를 분석합니다.
> 개별 기업 분석 시에도 동일한 원리 적용: 협업 발표·사업 모델 전환 이벤트 전후로 세그먼트를 분리합니다.

### C-1. Granger 선행성 — 장기 vs 현재 사이클 비교

| 구분 | Factor(지표명) | 컨설팅 함의 |
| --- | --- | --- |
| 지속 선행 (양기간 공통) | 비농업고용 MoM 증감(천명), VIX 변동성지수, 설비가동률(%), M2 통화량 MoM%, PPI MoM%, CPIAUCSL, WTI 유가 MoM%, 2Y Treasury Yield, Fed Funds Rate, 미시간 소비자심리, 10Y Treasury Yield, 실업률 | 구조적 선행 — 높은 신뢰도 |
| 현 사이클 부상 | 없음 | 현 사이클 특이 요인 — 추적 강화 |
| 현 사이클 약화 | 소매판매 MoM% | 관계 소멸 가능 — 재검증 필요 |

### C-2. LASSO 선별 — 장기 vs 현재 사이클 비교

| 구분 | Factor(지표명) | 컨설팅 함의 |
| --- | --- | --- |
| 지속 선별 (양기간 공통) | 비농업고용 MoM 증감(천명), 소매판매 MoM%, USD/EUR 환율, VIX 변동성지수, 설비가동률(%), M2 통화량 MoM%, PPI MoM%, WTI 유가 MoM%, 2Y Treasury Yield, 주택착공 MoM%, 미시간 소비자심리, 10Y Treasury Yield, 실업률 | 장단기 모두 유효 |
| 현 사이클 부상 | 없음 | 현 사이클 특이 요인 |
| 현 사이클 약화 | 없음 | 역할 약화 — 모니터링 축소 검토 |

### C-3. 현재 사이클 Rolling OLS 안정성 (24개월 창)

| 구분 | Factor |
|------|--------|
| **안정** | 없음 |
| **불안정** | PAYEMS, UNRATE, HOUST, VIXCLS, M2SL |

> **해석 지침**: 장기에서 안정 → 현재 사이클에서 불안정으로 전환된 Factor는
> 구조 변화의 전형적 신호입니다. 현재 사이클에서 새로 안정화된 Factor가
> 이번 사이클의 실질 선행지표 후보입니다.


## 부록 D: Company Event × 매크로 레짐 연동 분석

> **방법론**: GMM 3-state 레짐(Expansion/Neutral/Contraction)을 개별 기업 이벤트 시점에 오버레이.
> 매크로 Factor Pool 분석(INDPRO 기준)과 기업 구조 변화의 정합성을 시각화합니다.

### D-1. 핵심 이벤트 시점별 GMM 레짐

| 이벤트 | 날짜(YM) | GMM 레짐 |
| --- | --- | --- |
| Reddit — OpenAI 계약 | 2024-05 | Neutral |
| Reddit — Q3 어닝 주가 급등 | 2024-10 | Neutral |
| Reddit — Dynp break 1 | 2025-01 | Neutral |
| Samsung — Tesla 2nm 계약 | 2025-07 | Expansion |
| Samsung — Dynp break | 2025-08 | Neutral |

### D-2. 연동 패턴 비교

| 항목 | Samsung Electronics | Reddit (RDDT) |
|------|-------------------|---------------|
| 이벤트 | Tesla 2nm 파운드리 계약 (2025-07-28) | OpenAI 파트너십 (2024-05-16) |
| 이벤트 시점 레짐 | **Expansion** | Neutral |
| Dynp break 시점 레짐 | Neutral (2025-08) | Neutral (2025-01) |
| 매크로 연동 | **연동** — AI 제조 수요 확장과 타이밍 정합 | **비연동** — 사이클 무관 구조 변화 |
| 포트폴리오 서사 | 매크로 Expansion이 AI 파운드리 피벗 성공의 배경 | AI 데이터 수익화는 경기 사이클을 초월한 독자 전환 |

### D-3. 방법론 해석

![Company Event × 매크로 레짐 오버레이](outputs/charts/company_regime_overlay_20260304.png)

- **Samsung**: Tesla 계약(2025-07)이 Expansion 국면에서 체결 → 매크로 생산 확대 수요가
  AI 파운드리 사업의 실수요를 뒷받침. Factor Pool의 PAYEMS(고용 선행)·M2SL(유동성)이
  동 기간 STRONG 신호를 유지한 것과 방향 일치.
- **Reddit**: 계약(2024-05)부터 break(2025-01)까지 모든 핵심 시점이 Neutral.
  원인은 금리 인하(2024-09)가 아니라 **Q3 어닝(2024-10-29)을 통한 AI 매출 실적 확인** →
  시장이 발표(5월) 아닌 증거(10월) 이후 구조 재평가. 이는 Factor Pool의 매크로 신호와
  독립적인 기업 특유 구조 변화임.
- **방법론 한계**: GMM은 INDPRO MoM%를 기준으로 학습. 주가 수익률과의 직접 Granger
  검증은 미구현(향후 확장 가능). 현재 레짐 오버레이는 **배경 조건 확인** 수준.


## 부록 E: 멀티관점 토론 (Multi-Perspective Debate)

> **설계 원칙** (spec.md Section 7): 동일 분석 데이터를 3관점에서 독립 해석.
> 공통 신호 = 강한 증거 / 불일치 = 구조 변화 리스크로 클라이언트에 전달.

### E-1. 관점별 결론

| 관점 | 결론 |
| --- | --- |
| 매크로 관점 | 🟡 Expansion 우세 (일부 역신호) |
| 실물경제 관점 | 🟢 Expansion 지속 |
| 비용·심리 관점 | ⚪ 혼조 (방향 불명확) |

**종합 합의**: ⚠️ **Moderate Confidence** — 2관점 Expansion, 1관점 역신호

### E-2. Factor별 상세 신호

| 관점 | Factor | 현재값 | 방향(Exp 정합) | Granger 강도 |
| --- | --- | --- | --- | --- |
| 매크로 관점 | Fed Funds Rate | 3.64 | ↓ (✓) | STRONG |
| 매크로 관점 | 10Y-2Y Yield Spread | 0.65 | ↑ (✓) | — |
| 매크로 관점 | 10Y Treasury Yield | 4.13 | ↓ (✗) | STRONG |
| 실물경제 관점 | 비농업고용 MoM 증감(천명) | 130.00 | ↑ (✓) | STRONG |
| 실물경제 관점 | 실업률 | 4.30 | ↓ (✓) | STRONG |
| 실물경제 관점 | 소매판매 MoM% | -0.35 | ↑ (✓) | MODERATE |
| 비용·심리 관점 | WTI 유가 MoM% | 3.57 | ↑ (✗) | STRONG |
| 비용·심리 관점 | PPI MoM% | 0.27 | ↓ (✓) | STRONG |
| 비용·심리 관점 | VIX 변동성지수 | 19.21 | ↑ (✗) | STRONG |
| 비용·심리 관점 | 설비가동률(%) | 76.21 | ↑ (✓) | STRONG |

> ✓ = 해당 방향이 Expansion 정합 / ✗ = 역방향 (Neutral·Contraction 우호)

### E-3. 해석 가이드

| 합의 등급 | 의미 | 권고 |
|---------|------|------|
| High Confidence | 3관점 동일 방향 | 현 시나리오(Expansion) 신뢰도 높음 — 포지션 유지 |
| Moderate | 2:1 분할 | 소수 의견 Factor 집중 모니터링 — 분기 재평가 |
| Caution | 2관점 이상 역신호 | 레짐 전환 선제 대응 체계 가동 |
| Uncertain | 3관점 모두 다름 | 구조 변화 구간 — 모든 포지션 재검토 |

**현재 등급**: **Moderate**

