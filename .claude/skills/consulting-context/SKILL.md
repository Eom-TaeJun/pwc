---
name: consulting-context
description: |
  PwC 오퍼레이션 컨설팅 맥락 — Factor Pool 보고서 작성 전체 가이드.
  report_raw_YYYYMMDD.json을 읽어 MD 보고서를 작성할 때 자동 주입됩니다.
  트리거: 보고서 작성, report_raw 읽기, generate-report 커맨드 실행 시.
user-invocable: false
---

# PwC 컨설팅 맥락

> 이 스킬은 보고서 작성 시 자동 주입됩니다. 읽기 전용.

---

## PwC 오퍼레이션 컨설팅에서 Factor 분석 활용법

**오퍼레이션 컨설팅 맥락**:
- 클라이언트: 제조·물류·에너지 섹터 기업
- 핵심 니즈: 수요 예측 → 생산 계획 최적화 → 재고/인력 배치
- Factor Pool 분석의 가치: INDPRO 선행 신호로 수요 변동 1~6개월 선행 감지

### 활용 시나리오

| 시나리오 | Factor 신호 | 컨설팅 제언 |
|---|---|---|
| 경기 둔화 선행 | T10Y2Y 역전 + UMCSENT 하락 | 생산 캐파 축소, 재고 선제 감축 |
| 회복 선행 | HOUST 반등 + 하이일드 스프레드 축소 | 원자재 선매입, 인력 증원 준비 |
| 비용 압력 | WTI 급등 + PPI 상승 | 에너지 헷징, 가격 전가 검토 |
| 금융 긴축 | FEDFUNDS 인상 + KCFSI 상승 | 투자 연기, 현금 보유 확대 |

---

## 제약 데이터 → 설득 논리 프레임

컨설팅 현장에서 데이터는 항상 불완전하다.
제약을 인정하면서도 의사결정 가치를 유지하는 프레임:

### 프레임 1: "방향성 확신, 크기 불확실"

```
[데이터 한계] 2020년 코로나 충격으로 Rolling OLS 계수 불안정.
[설득 논리]  그러나 T10Y2Y의 부호(방향성)는 일관됨.
             INDPRO 반등/하락 방향 예측은 가능하며,
             정확한 크기보다 방향성이 선제적 의사결정에 중요합니다.
```

### 프레임 2: "단일 지표 아닌 포트폴리오 신호"

```
[데이터 한계] 어떤 단일 Factor도 INDPRO를 완벽히 예측하지 못함.
[설득 논리]  LASSO 선별된 4개 Factor가 동시에 같은 방향을 가리킬 때,
             신호의 신뢰도는 개별 Factor보다 통계적으로 유의하게 높습니다.
             (앙상블 접근: 다중 신호 수렴)
```

### 프레임 3: "모델은 보조, 판단은 경영진"

```
[데이터 한계] 지정학 리스크, 정책 서프라이즈는 모델이 포착 못함.
[설득 논리]  이 분석은 경영진의 판단을 대체하는 것이 아니라,
             정량적 기준선(baseline)을 제공합니다.
             "이 신호가 없을 때"와 "있을 때"의 의사결정 품질 차이가
             이 분석의 가치입니다.
```

---

## 보고서 작성 어조 가이드

| 상황 | 권장 표현 | 금지 표현 |
|---|---|---|
| 선행지표 제시 | "~와 양의 상관관계를 보임 (r=0.42, lag=3M)" | "~를 예측한다" |
| 분석 한계 | "백데이터 기반 분석으로 체제 변화 시 재검증 필요" | (한계 생략) |
| 활용 제언 | "~를 모니터링 기준으로 활용 권장" | "~하면 반드시 성공한다" |
| 수치 출처 | "FRED INDPRO, 수집일: YYYY-MM-DD" | (출처 없는 수치) |

---

## 포트폴리오로서의 이 분석

이 프로젝트는 PwC 오퍼레이션 컨설팅 RA 인턴 지원 포트폴리오다.
보고서 작성 시 다음을 항상 염두에 둘 것:

- **RA 인턴의 역할**: 데이터 수집 자동화 + 분석 초안 → 시니어가 검토
- **포트폴리오 목적**: "나는 거시 Factor와 LASSO를 이해하고 자동화할 수 있다"는 증거
- **컨설팅 감각 시연**: 분석 한계를 솔직히 인정하면서 의사결정 가치를 설명하는 능력

---

## 보고서 작성 가이드 (report_raw_YYYYMMDD.json → MD)

> `outputs/context/report_raw_YYYYMMDD.json`을 읽어 아래 구조로 MD 보고서를 작성한다.
> 출력: `outputs/reports/factor_pool_YYYYMMDD.md`

### 전체 구조

```
# {dynamic_title_from_json}
생성일 | target_label | 출처: FRED

---
Executive Summary
Section 1: 지금 어디에 있는가?     (regime)
Section 2: 무엇이 먼저 움직이는가?  (leading_indicators)
Section 3: 얼마나 확신할 수 있는가? (lasso + rf + rolling)
Section 4: 무엇을 해야 하는가?      (scenarios + actions)
---
부록 A: 방법론  (meta.params)
부록 B: 전체 데이터 테이블  (correlation + granger_full + lasso)
부록 C: 현재 사이클 집중 분석  (short_period_analysis)
부록 D: Company Event × 매크로 레짐  (company_events)
부록 E: 멀티관점 토론  (factor_directions → 아래 E 섹션 참조)
```

---

### Dynamic Title 생성 방법

`leading_indicators.signals` 첫 번째 항목을 사용:
```
산업생산 {regime.label} 국면: {signals[0].label}가 {signals[0].lag}개월 앞서 신호를 보낸다
```
신호가 없으면: `산업생산 {regime.label} 국면 진단 — Factor Pool 선행지표 분석`

---

### Executive Summary 작성법

`report_raw.regime` 필드 사용:
- **현재 레짐**: `regime.label` + 한국어(`regime.display_label`) + 신뢰도(`regime.confidence_pct`%)
- **레짐 확률**: `regime.probs` 딕셔너리
- **레짐 모멘텀**: `regime.recent_6m` (최근 6개월 시퀀스, E/N/C 약자) + `expansion_count` 기반 요약:
  - expansion_count ≥ 4: `▲ 안정 Expansion (최근 6개월 중 N회)`
  - expansion_count ≥ 2: `△ Expansion 전환 중 (최근 6개월 중 N회 — 불안정)`
  - 그 외: `▽ Neutral 우세`
- **선행지표 현재 신호**: `leading_indicators.signals[:3]`에서 `label + direction + lag` 조합
- **분석 기간**: `meta.analysis_period`

---

### Section 1: 지금 어디에 있는가?

`regime.entropy` 기반 해석:
- entropy < 0.8: "레짐 전환 가능성이 낮은 안정적 상태"
- entropy ≥ 0.8: "복수 국면 혼재 — 불확실성 높음"

**반드시 포함할 주의사항**:
> GMM 레짐은 INDPRO MoM% 성장률 변동성 기준. NBER 경기확장·침체와 직접 대응하지 않음.
> 구조 변화 구간(2008~2009, 2020)에서 모델 신뢰도 저하.

---

### Section 2: 무엇이 먼저 움직이는가?

`leading_indicators.signals` + `leading_indicators.granger_full` 사용.

**표 형식**:
| 지표명 | Granger 선행 | 강도 | 현재 방향 |
|--------|------------|------|---------|
| {label} | +{lag}개월 | {strength} | {direction} |

**해석 주의**: Cross-corr lag가 음수인 경우 = 피드백 루프 (INDPRO → Factor 반응 방향). 선행 판단은 Granger(+) 기준.

`consensus_factors`(양방법 합의)가 있으면 "강한 선행 증거"로 강조.

---

### Section 3: 얼마나 확신할 수 있는가?

1. **RF + LASSO 교차검증**: `rf_importance[:8]` 테이블. `lasso_selected: true`인 항목 ✓ 표시.
   - `dual_confirmed` = LASSO + RF 모두 선별 → "최강 신뢰도" 강조.
2. **Rolling OLS 안정성**: `rolling_stability.stable_factors` / `unstable_factors` / `stability_scores`(CV ratio).
   - 불안정 Factor 해석: "구조 변화의 신호 — 분기 1회 재평가 권고" (분석 실패 아님!)

---

### Section 4: 무엇을 해야 하는가?

`factor_directions` + `leading_indicators.signals`에서 현재 방향 확인 후 시나리오 테이블 작성:

| 시나리오 | 신호 조건 | 핵심 모니터링 Factor(주기) | 대응 권고 |
|---------|---------|----------------------|---------|
| Expansion | 선행 Factor 지속 상승 | {상위 Factor} | 현 포지션 유지 |
| Neutral | 혼조 | {상위 Factor} | 분기 1회 재평가 |
| Contraction | 선행 Factor 하락 | {상위 Factor} | 조기 경보, 리스크 재검토 |

모니터링 주기: lag ≤ 3M → 매월 / lag ≤ 6M → 격월 / 그 외 → 분기.

---

### 부록 A: 방법론

`meta.params`에서 모든 파라미터를 표로 정리:

| 단계 | 방법 | 파라미터 | 목적 |
|------|------|---------|------|
| 레짐 분류 | GMM 3-state | n_components=3 | 거시 국면 구분 |
| Factor 선별 | LASSO (LassoCV) | CV Folds={lasso_cv_folds}, α={lasso_alpha} | 희소 선형 선별 |
| 선행성 검증 | Granger F-test | ADF 정상화, maxlag={granger_maxlag} | 시간적 인과성 |
| ML 중요도 | Random Forest | n={rf_n_estimators} | 비선형 기여도 |
| 안정성 | Rolling OLS | window={rolling_window}개월 | 계수 불안정 탐지 |
| 구조 변화 | ruptures PELT | pen={break_penalty}, min_size={break_min_size}개월 | 사이클 분할 |

**필수 경고문 2개**:
1. Vintage 데이터 주의 (FRED 수정값 기준)
2. 구조 변화 구간 (ZLB, 팬데믹) 신뢰도 저하

---

### 부록 B: 전체 데이터 테이블

- **B-1**: `lasso.selected` 전체 (Factor | 지표명 | 계수)
- **B-2**: `correlation` 전체 (Factor | 지표명 | 상관계수 | p-value | 최적 Lag)
- **B-3**: `leading_indicators.granger_full` 전체. p-value < 0.0001 → "< 0.0001" 표기.

---

### 부록 C: 현재 사이클 집중 분석

`short_period_analysis` 필드 사용. 비어있으면 섹션 생략.

핵심 구조:
- **C-0**: PELT 세그먼트 타임라인 (구조 변화 시점)
- **C-1**: Granger 선행성 — 장기 vs 현재 비교 (신규 부상 / 지속 / 약화)
- **C-2**: LASSO 선별 — 장기 vs 현재 비교
- **C-3**: 현재 사이클 Rolling OLS 안정성

해석 지침: "현재 사이클에서 새로 안정화된 Factor = 이번 사이클 실질 선행지표 후보"

---

### 부록 D: Company Event × 매크로 레짐

`company_events` 필드 사용.

**D-1**: `key_dates` 테이블 (이벤트 | 날짜 | GMM 레짐)

**D-2**: Samsung vs Reddit 연동 패턴 비교:

| 항목 | Samsung Electronics | Reddit (RDDT) |
|------|-------------------|--------------|
| 이벤트 | Tesla 2nm 파운드리 계약 (2025-07) | OpenAI 파트너십 (2024-05) |
| 매크로 연동 | **연동** — Expansion 국면과 타이밍 정합 | **비연동** — 전 시점 Neutral |
| 서사 | AI 제조 수요 확장 파운드리 피벗 | AI 수익화는 경기 사이클 초월 구조 변화 |

**D-3**: 차트 참조 (`company_events.chart_path`)

**한계 명시**: "현재 레짐 오버레이는 배경 조건 확인 수준. 주가 수익률과의 직접 Granger 검증은 미구현."

---

### 부록 E: 멀티관점 토론

`factor_directions` 필드를 읽어 3관점을 독립 분석.

**Expansion 정합 방향**:
| Factor | Expansion 방향 |
|--------|-------------|
| FEDFUNDS | ↓ (금리 하락) |
| T10Y2Y | ↑ (스프레드 확대) |
| DGS10 | ↑ (성장 기대) |
| PAYEMS | ↑ (고용 증가) |
| UNRATE | ↓ (실업 감소) |
| RETAILSMNSA | ↑ |
| DCOILWTICO | ↓ (비용 완화) |
| PPIACO | ↓ (마진 개선) |
| VIXCLS | ↓ (불확실성 감소) |
| TCU | ↑ (가동률 상승) |

**관점 구성**:
- 매크로 관점: FEDFUNDS, T10Y2Y, DGS10 → "통화정책 사이클이 생산을 어디로 이끄는가?"
- 실물경제 관점: PAYEMS, UNRATE, RETAILSMNSA → "노동·소비 수요가 생산을 선행하는가?"
- 비용·심리 관점: DCOILWTICO, PPIACO, VIXCLS, TCU → "비용 압박과 가동률이 생산을 제약하는가?"

**관점별 verdict 판정**:
- 모든 Factor Expansion 정합 → 🟢 Expansion 지속
- 과반 정합 → 🟡 Expansion 우세 (일부 역신호)
- 과반 역신호 → 🔴 Neutral/Contraction 우세
- 동수 → ⚪ 혼조

**합의 판정**:
- 🟢 3개 → ✅ High Confidence
- 🟢 + 🟡 ≥ 2개 → ⚠️ Moderate Confidence
- 🔴 ≥ 2개 → 🚨 Caution
- 그 외 → ❓ Uncertain

---

### 품질 체크리스트 (커밋 전 필수)

- [ ] `None` 문자열 없음: `grep -n "None" outputs/reports/factor_pool_*.md | wc -l` → 0
- [ ] 모든 수치에 출처 명기 (FRED)
- [ ] Executive Summary 한 줄 결론 수치 포함
- [ ] Section 4 시나리오 3개 모두 작성
- [ ] 부록 A 방법론 파라미터 전체 기재
- [ ] 부록 D 차트 경로 정확한가 (`company_events.chart_path` 실제 존재 확인)
