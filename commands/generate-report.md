---
description: report_raw JSON에서 PwC 컨설팅 스타일 MD 보고서 작성 (report-writer 에이전트 사용)
argument-hint: "[YYYYMMDD | latest]"
---

# PwC 컨설팅 보고서 생성

`outputs/context/report_raw_YYYYMMDD.json`(손질된 재료)을 읽어
`report-writer` 에이전트가 `consulting-context` 스킬 가이드로 최종 MD 보고서를 작성합니다.

## 아키텍처

```
python main.py --report
  └→ src/report.py (build_raw_data)
       └→ outputs/context/report_raw_YYYYMMDD.json   ← 이 파일이 입력

/generate-report (이 커맨드)
  └→ report-writer 에이전트
       ├→ consulting-context SKILL.md (보고서 작성 지능)
       ├→ factor-research SKILL.md (Factor 해석 지식)
       └→ outputs/reports/factor_pool_YYYYMMDD.md   ← 최종 보고서
```

## 워크플로

### Step 1: 원재료 확인

**Use skill: "consulting-context"** 를 로드하여 보고서 작성 가이드를 준비합니다.
**Use skill: "factor-research"** 를 로드하여 Factor 해석 지식을 준비합니다.

인자로 날짜 지정 가능 (예: `generate-report 20260304`).
인자 없으면 가장 최신 파일 사용:

```bash
ls outputs/context/report_raw_*.json | sort | tail -1
```

### Step 2: raw JSON 구조 확인

`report_raw_*.json`의 최상위 키:

| 키 | 내용 |
|----|------|
| `meta` | 분석 기간, 파라미터 (부록 A용) |
| `regime` | 레짐 + 모멘텀 (Section 1, Exec Summary) |
| `leading_indicators` | Granger 선행지표 신호 (Section 2) |
| `lasso` | LASSO 선별 결과 (Section 3, 부록 B) |
| `rf_importance` | RF 중요도 (Section 3) |
| `dual_confirmed` | LASSO + RF 모두 선별 Factor (Section 3) |
| `rolling_stability` | Rolling OLS 안정성 (Section 3) |
| `correlation` | 상관관계 전체 (부록 B) |
| `short_period_analysis` | 현재 사이클 분석 (부록 C) |
| `factor_directions` | 10개 Factor 현재 방향 (Section 4, 부록 E) |
| `company_events` | 이벤트 × 레짐 연동 (부록 D) |
| `consulting_implications` | 컨설팅 함의 (Section 4) |
| `chart_paths` | 차트 파일 경로 |

### Step 3: report-writer 에이전트 실행

**Use agent: "report-writer"** 에게 다음을 전달합니다:
1. `report_raw_YYYYMMDD.json` 경로
2. consulting-context 스킬 가이드 참조 지시
3. 출력 경로: `outputs/reports/factor_pool_YYYYMMDD.md`

### Step 4: 품질 검증

```bash
grep -c "None" outputs/reports/factor_pool_*.md  # 0이어야 함
```

체크리스트:
- [ ] `None` 문자열 없음
- [ ] Executive Summary 한 줄 결론 (수치 포함)
- [ ] Section 4 시나리오 3개
- [ ] 부록 A 파라미터 전체
- [ ] 부록 D 차트 경로 정확

### Human-in-the-Loop Gate

보고서 생성 후 확인:
- 수치 출처·None 값·컨설팅 함의 최종 검토
- 이상 없으면 커밋
