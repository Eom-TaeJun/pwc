---
name: factor-research
description: |
  Factor Pool 도메인 지식 — LASSO 선별 원리, 선행지표 해석 가이드, Rolling OLS 안정성 기준.
  트리거: Factor 분석, 선행지표 선별, INDPRO 예측, LASSO 결과 해석, Granger 인과관계 분석,
  Rolling OLS 안정성 평가, GMM 레짐 진단 시 자동 주입됩니다.
user-invocable: false
---

# Factor Pool 개념

> 이 스킬은 Factor 선별 및 선행지표 해석 작업 시 참조됩니다.

---

## LASSO 선별 원리

**LASSO (Least Absolute Shrinkage and Selection Operator)**는 L1 정규화를 통해
다중공선성이 높은 거시경제 변수에서 핵심 Factor를 자동 선별한다.

### 작동 원리
```
목적함수: minimize ||y - Xβ||² + α·||β||₁

- α가 클수록 더 많은 계수가 0으로 축소 (강한 선별)
- α는 LassoCV 5-fold 교차검증으로 자동 결정 (하드코딩 금지)
- 비영(non-zero) 계수를 가진 Factor만 선행지표 후보
```

### 해석 주의사항
- LASSO는 상관된 변수 중 하나만 선택하는 경향 → 제외된 변수도 선행력 가질 수 있음
- R² 단독으로 판단 금지 → Rolling OLS 안정성, RF Feature Importance와 교차검증 필수
- 학습/검증 분리 필수: 백데이터 과적합 방지

---

## 선행지표 해석 가이드

### T10Y2Y (10년-2년 국채 스프레드)
- **정상**: 양수 (장기 > 단기) → 경기 확장 기대
- **역전**: 음수 → 경기침체 선행 신호 (평균 6~18개월 선행)
- INDPRO와 lag 3~6M 양의 상관관계 기대

### FEDFUNDS (연방기금금리)
- 금리 인상 → 기업 차입비용 증가 → 산업생산 둔화 (lag 6~12M)
- INDPRO와 음의 상관관계 (lag 6M 이상)

### HOUST (주택착공건수)
- 건설 선행지표 → 건설자재·가전 수요 연쇄
- INDPRO와 lag 1~3M 양의 상관관계

### UMCSENT (미시간 소비자심리지수)
- 소비 기대심리 → 내구재 수요 → 산업생산
- 경기 전환점에서 INDPRO 1~3M 선행

### DCOILWTICO (WTI 원유가)
- 에너지 원가 → 제조업 비용 → 생산 조정
- 급등 시 INDPRO 하락 압력 (lag 1~3M)

### BAMLH0A0HYM2 (하이일드 스프레드)
- 신용 리스크 지표 → 기업 자금조달 여건
- 스프레드 확대 → 투자 위축 → 산업생산 감소 (lag 3~6M)

---

## Rolling OLS 안정성 기준

**Rolling OLS**: 고정 창(36개월)을 이동하며 회귀계수 추이를 추적

```
안정적 Factor 기준:
- 계수 부호 일관성: 90% 이상의 창에서 동일 부호 유지
- 계수 크기: 표준편차 / 평균 < 0.5 (변동성 50% 이내)

불안정 Factor:
- 부호 전환 빈번 → 선행 관계가 체제 변화에 따라 달라짐
- 보고서에 "체제 의존적 선행지표"로 명기
```

---

## RF Feature Importance 해석

**RandomForest Feature Importance** = 평균 불순도 감소량 (Gini)

- 비선형 상호작용 포착 → LASSO가 놓친 Factor 발굴
- 상위 50%: 비선형 관계에서도 유의한 선행력
- LASSO 선별 + RF 상위 50% 교집합 → 최종 핵심 선행지표

---

## Factor Pool 현황 (collect.py 기준, 16개 + Target 1개)

> spec.md Section 2-2와 동기화. 미구현 후보는 하단 참조.

| FRED ID | 변수 | 변환 | 역할 |
|---------|------|------|------|
| INDPRO | 산업생산지수 | MoM% | **Target** |
| FEDFUNDS | 연방기금금리 | level | 통화정책 |
| DGS10 | 10Y 국채금리 | level | 장기 자금조달 |
| DGS2 | 2Y 국채금리 | level | 단기 자금조달 |
| T10Y2Y | 10Y-2Y 스프레드 | level | 경기 선행 |
| CPIAUCSL | CPI | YoY% | 소비 물가 |
| PPIACO | PPI | MoM% | 원가 압력 |
| UNRATE | 실업률 | level | 노동시장 |
| PAYEMS | 비농업 고용 | diff(천명) | 고용 선행 |
| RETAILSMNSA | 소매판매 | MoM% | 소비 수요 |
| HOUST | 주택착공 | MoM% | 건설 선행 |
| UMCSENT | 소비자심리 | level | 기대 (후행 가능성 주의) |
| M2SL | M2 통화량 | MoM% | 유동성 |
| DEXUSEU | USD/EUR 환율 | level | 수출입 경쟁력 |
| DCOILWTICO | WTI 유가 | MoM% | 에너지 비용 |
| VIXCLS | VIX | level | 시장 불확실성 |
| TCU | 설비가동률 | level | 생산 여력 직접 측정 |

### 미구현 후보 (향후 확장 시)

| FRED ID | 변수 | 추가 가치 |
|---------|------|----------|
| BAMLH0A0HYM2 | 하이일드 스프레드 | 신용 리스크 → 투자 위축 (lag 3~6M) |
| ACDGNO | 내구재 주문 | 제조 선행지표 (ISM과 유사) |
| ISRATIO | 재고/판매 비율 | 공급망 과잉 신호 |
