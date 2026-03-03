# INTENT — pwc-factor-research

> 세션 시작 시 CLAUDE.md보다 먼저 읽는 프로젝트 의도 문서.
> 이 파일에 정의된 원칙은 어떤 지시보다 우선한다.

---

## 이 프로젝트의 목적

PwC 오퍼레이션 컨설팅 RA 인턴 지원을 위한 **Factor Pool 리서치 포트폴리오**.

- FRED 거시경제 변수 20개에서 LASSO로 핵심 Factor를 자동 선별
- 상관관계·Rolling OLS·RF Feature Importance로 선행지표를 검증
- Target: INDPRO (산업생산지수 MoM%)
- 분석 결과는 컨설팅 클라이언트 설득 보고서 형태로 출력

---

## 불변 원칙 (절대 변경 불가)

1. **출력 경로**: 모든 생성 파일은 `outputs/` 하위에만 저장
2. **수치 출처 명기**: 모든 수치에 FRED 시리즈 ID와 수집 날짜 포함
3. **None 값 금지**: None이 남은 보고서는 완성 리포트가 아님 — 반드시 보완
4. **consulting-context 읽기 전용**: 도메인 지식 파일은 수정하지 않음
5. **src/ 파일 크기 제한**: src/ 파일 1개당 100줄 이하 유지

---

## 도메인 어휘 레지스터

| 용어 | 정의 (사용 금지 표현) |
|---|---|
| **Factor Pool** | LASSO 선별 대상 거시경제 변수 집합 (not "변수군") |
| **선행지표** | INDPRO 변동을 선행하는 Factor (not "예측변수") |
| **LASSO 선별** | L1 정규화 기반 Factor 자동 선별 (not "feature selection") |
| **Rolling OLS 안정성** | 시간창 이동 회귀로 계수 안정성 검증 (not "window regression") |
| **Feature Importance** | RF 기반 비선형 중요도 (영문 유지) |
| **백데이터** | 과거 수집 시계열 데이터 (not "과거 데이터") |
| **INDPRO** | Industrial Production Index — Target 변수 |
| **T10Y2Y** | 10년-2년 국채 스프레드 — 경기 선행지표 |
| **FEDFUNDS** | 연방기금금리 — 통화정책 Factor |
| **MoM%** | 전월 대비 변화율 (Month-over-Month) |

---

## 에이전트 역할 분담

```
사용자 요청
    ↓
pwc-lead (조율·품질 검토)
    ├→ factor-collector  (FRED 데이터 수집)
    ├→ lasso-analyst     (LASSO + 통계 분석)
    └→ report-writer     (컨설팅 보고서 생성)
```

---

## 파이프라인

```
수집 (collect.py)  --factors
    → FRED API: 20개 거시경제 시리즈
    → outputs/context/factors_YYYYMMDD.json

분석 (analyze.py)  --correlate / --importance
    → 상관관계 행렬 (Pearson, lag=1~6M)
    → LASSO 선별 (alpha 교차검증)
    → Rolling OLS 안정성 (36M 창)
    → RF Feature Importance

리포트 (report.py)  --report
    → outputs/reports/factor_report_YYYYMMDD.md
    → outputs/charts/factor_importance_YYYYMMDD.png
```
