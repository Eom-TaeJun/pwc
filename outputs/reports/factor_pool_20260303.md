# Factor Pool 리서치 보고서

**생성일**: 2026-03-03
**Target**: 산업생산지수 MoM%
**데이터 출처**: FRED (Federal Reserve Bank of St. Louis)

---

## 0. Executive Summary

| 항목 | 내용 |
|------|------|
| **현재 레짐** | **Neutral** |
| 레짐 신뢰도 | 99.9% (Shannon Entropy: 0.001) |
| 레짐 확률 분포 | Expansion: 0.0% | Neutral: 100.0% | Contraction: 0.0% |
| 핵심 선행지표 | FEDFUNDS가 INDPRO 6개월 선행 (Granger STRONG) |
| 클라이언트 권고 | 현재 산업생산 레짐: Neutral. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할 |

![레짐 타임라인](outputs/charts/regime_timeline_20260303.png)

![The Signal](outputs/charts/signal_chart_20260303.png)

## 1. 분석 개요

| 항목 | 내용 |
|------|------|
| Target 변수 | 산업생산지수 MoM% (INDPRO) |
| 분석 기간 | 2000-02-01 ~ 2025-11-01 (309개월) |
| Factor 후보 | 15개 FRED 시계열 |
| 방법론 | LASSO 선별 → 상관관계 분석 → Rolling OLS → RF Feature Importance |
| 생성일 | 2026-03-03 |
| 데이터 출처 | FRED (Federal Reserve Bank of St. Louis) |

## 2. LASSO 선행지표 선별 결과

LASSO 정규화(교차검증 5-Fold)로 12개 Factor 선별.
계수 크기(절댓값)는 상대적 중요도를 나타내며, 0이 아닌 계수만 표시.

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

> **해석**: 계수 부호(+/-)는 INDPRO와의 방향성, 크기는 기여도.

![LASSO 정규화 경로](outputs/charts/lasso_path_20260303.png)

## 3. 상관관계 분석 (시차별)

각 Factor와 INDPRO 간 피어슨 상관계수. 시차 0·3·6·12개월 중 최적 lag 선택 (p < 0.05 기준).

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

![상관관계 히트맵](outputs/charts/correlation_heatmap_20260303.png)

## 3.5 Granger 인과관계 검증

ADF 정상성 변환 후 F-test. STRONG: p<0.01 / MODERATE: p<0.05 / WEAK: p<0.10.

| Factor | 지표명 | 강도 | 최적 Lag(월) | p-value |
| --- | --- | --- | --- | --- |
| FEDFUNDS | Fed Funds Rate | STRONG | 6 | 0.0000 |
| UNRATE | 실업률 | STRONG | 7 | 0.0000 |
| PAYEMS | 비농업고용 MoM 증감(천명) | STRONG | 11 | 0.0000 |
| M2SL | M2 통화량 MoM% | STRONG | 5 | 0.0000 |
| DCOILWTICO | WTI 유가 MoM% | STRONG | 1 | 0.0000 |
| VIXCLS | VIX 변동성지수 | STRONG | 2 | 0.0000 |
| DGS2 | 2Y Treasury Yield | STRONG | 2 | 0.0000 |
| PPIACO | PPI MoM% | STRONG | 1 | 0.0000 |

> Pearson 상관관계(섹션 3)는 동시적 연관성을, Granger는 **시간적 선행성**을 검증합니다.

## 4. ML Feature Importance (Random Forest)

Random Forest(n=100, random_state=42) 기반 Feature Importance.
LASSO 선별 Factor를 대상으로 산정.

| 순위 | Factor | 지표명 | Importance |
| --- | --- | --- | --- |
| 1 | PAYEMS | 비농업고용 MoM 증감(천명) | 0.2666 |
| 2 | M2SL | M2 통화량 MoM% | 0.2268 |
| 3 | UNRATE | 실업률 | 0.1194 |
| 4 | HOUST | 주택착공 MoM% | 0.1046 |
| 5 | DCOILWTICO | WTI 유가 MoM% | 0.0627 |
| 6 | PPIACO | PPI MoM% | 0.0449 |
| 7 | DGS2 | 2Y Treasury Yield | 0.0418 |
| 8 | RETAILSMNSA | 소매판매 MoM% | 0.0357 |
| 9 | DEXUSEU | USD/EUR 환율 | 0.0299 |
| 10 | DGS10 | 10Y Treasury Yield | 0.0272 |

![Feature Importance](outputs/charts/importance_bar_20260303.png)

## 5. Rolling OLS 안정성 검증 (36개월 창)

계수의 시계열 안정성 판별 기준: |std/mean| < 0.5 → 안정, ≥ 0.5 → 불안정.

| 구분 | Factor |
|------|--------|
| **안정 Factor** | 없음 |
| **불안정 Factor** | PAYEMS, UNRATE, HOUST, VIXCLS, DGS2 |

> 불안정 Factor는 구조 변화(금융위기, 팬데믹) 구간에서 관계가 역전될 위험 있음.

## 6. 컨설팅 함의

### 현재 레짐 판단
Neutral (신뢰도 99.9%)

### 선행지표 활용
FEDFUNDS가 INDPRO 6개월 선행 (Granger STRONG)

### 데이터 제약
주요 지표 모두 하드 데이터

### 클라이언트 설명 프레임
현재 산업생산 레짐: Neutral. FEDFUNDS 신호 추이가 생산계획 조기 경보 역할

---
*본 보고서는 FRED 공공 데이터를 기반으로 자동 생성되었습니다. 수치 해석 시 출처(FRED)와 분석 기간을 반드시 명기하십시오.*
