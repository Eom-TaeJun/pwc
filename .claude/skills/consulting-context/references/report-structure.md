# 보고서 구조 가이드 (report_raw_YYYYMMDD.json → MD)

> 출력: `outputs/reports/factor_pool_YYYYMMDD.md`

## 전체 구조

```
# {dynamic_title}
생성일 | target_label | 출처: FRED
---
Executive Summary
Section 1: 지금 어디에 있는가?
Section 2: 무엇이 먼저 움직이는가?
Section 3: 얼마나 확신할 수 있는가?
Section 4: 무엇을 해야 하는가?
---
부록 A: 방법론
부록 B: 전체 데이터 테이블
부록 C: 현재 사이클 집중 분석
부록 D: Company Event × 매크로 레짐
부록 E: 멀티관점 토론
```

## Dynamic Title

`leading_indicators.signals[0]` 사용:
```
산업생산 {regime.label} 국면: {signals[0].label}가 {signals[0].lag}개월 앞서 신호를 보낸다
```
신호 없으면: `산업생산 {regime.label} 국면 진단 — Factor Pool 선행지표 분석`

## Executive Summary

| 항목 | JSON 필드 |
|------|---------|
| 현재 레짐 | `regime.label` + `regime.display_label` + `regime.confidence_pct`% |
| 레짐 확률 | `regime.probs` |
| 레짐 모멘텀 | `regime.recent_6m` (E/N/C 시퀀스) + `expansion_count` 기반 요약 |
| 선행지표 신호 | `leading_indicators.signals[:3]` (label + direction + lag) |
| 분석 기간 | `meta.analysis_period` |

**모멘텀 레이블**: expansion_count ≥ 4 → `▲ 안정 Expansion` / ≥ 2 → `△ 전환 중` / 그 외 → `▽ Neutral 우세`

## Section 1: 지금 어디에 있는가?

- `regime.entropy` < 0.8: "안정적 상태" / ≥ 0.8: "복수 국면 혼재"
- **필수 주의사항**: GMM은 INDPRO MoM% 변동성 기준 — NBER 경기국면과 직접 대응 안 함

## Section 2: 무엇이 먼저 움직이는가?

표: `leading_indicators.signals` (지표명 | Granger 선행 | 강도 | 현재 방향)

**주의**: Cross-corr lag 음수 = 피드백 루프. 선행 판단은 Granger(+) 기준.

`consensus_factors` 있으면 "양방법 합의 — 강한 선행 증거"로 강조.

## Section 3: 얼마나 확신할 수 있는가?

1. **RF + LASSO**: `rf_importance[:8]` 표, `lasso_selected: true` → ✓
   - `dual_confirmed` = 최강 신뢰도 강조
2. **Rolling OLS**: `rolling_stability` 안정/불안정 분류 + CV ratio
   - 불안정 = 구조 변화 신호 (분석 실패 아님)

## Section 4: 무엇을 해야 하는가?

`factor_directions` + `leading_indicators.signals`에서 현재 방향 읽어 시나리오 표 작성:

| 시나리오 | 신호 조건 | 모니터링 Factor | 대응 |
|---------|---------|--------------|------|
| Expansion | 선행 Factor 지속 상승 | {상위} | 현 포지션 유지 |
| Neutral | 혼조 | {상위} | 분기 재평가 |
| Contraction | 선행 Factor 하락 | {상위} | 조기 경보 |

모니터링 주기: lag ≤ 3M → 매월 / ≤ 6M → 격월 / 그 외 → 분기

## 부록 A: 방법론

`meta.params` 전체를 표로 정리 + **필수 경고문 2개**:
1. Vintage 데이터 주의 (FRED 수정값 기준)
2. 구조 변화 구간(ZLB, 팬데믹) 신뢰도 저하

## 부록 B: 전체 데이터 테이블

- B-1: `lasso.selected` (Factor | 지표명 | 계수)
- B-2: `correlation` (Factor | 지표명 | r | p-value | lag)
- B-3: `granger_full` (p-value < 0.0001 → "< 0.0001")

## 부록 C: 현재 사이클 집중 분석

`short_period_analysis` 비어있으면 생략.
- C-0: PELT 세그먼트 타임라인
- C-1: Granger 선행성 — 장기 vs 현재 (신규 부상 / 지속 / 약화)
- C-2: LASSO 선별 — 장기 vs 현재
- C-3: Rolling OLS 안정성 (현재 사이클)

## 부록 D: Company Event × 매크로 레짐

`company_events` 사용.
- D-1: `key_dates` 표 (이벤트 | 날짜 | GMM 레짐)
- D-2: Samsung(연동) vs Reddit(비연동) 비교 표
- D-3: 차트 (`company_events.chart_path`) + 한계 명시

## 부록 E: 멀티관점 토론

`factor_directions`에서 Expansion 정합 방향 대조:

| Factor | Expansion 방향 |
|--------|-------------|
| FEDFUNDS | ↓ | T10Y2Y | ↑ | DGS10 | ↑ |
| PAYEMS | ↑ | UNRATE | ↓ | RETAILSMNSA | ↑ |
| DCOILWTICO | ↓ | PPIACO | ↓ | VIXCLS | ↓ | TCU | ↑ |

3관점 구성 + 합의 판정:
- 🟢 3개 → High Confidence / 🟢+🟡 ≥ 2 → Moderate / 🔴 ≥ 2 → Caution / 그 외 → Uncertain

## 품질 체크리스트

- [ ] `None` 문자열 없음
- [ ] Executive Summary 한 줄 결론 (수치 포함)
- [ ] Section 4 시나리오 3개
- [ ] 부록 A 파라미터 전체 기재
- [ ] 수치마다 출처 명기 (FRED)
