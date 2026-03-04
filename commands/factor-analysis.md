---
description: FRED 데이터 수집부터 LASSO·Granger·GMM 분석까지 전체 Factor Pool 파이프라인 실행
argument-hint: "[--all | --collect | --analyze | --report]"
---

# Factor Pool 분석 파이프라인

FRED 공개 데이터로 산업생산지수(INDPRO) 선행 Factor를 발굴하는 전체 파이프라인을 실행합니다.

## 실행 옵션

인자가 없거나 `--all`이면 전체 파이프라인 실행:

```bash
python main.py --all
```

단계별 실행:

| 인자 | 실행 내용 |
|------|----------|
| `--collect` | FRED API로 16개 Factor + INDPRO 수집 → `outputs/context/factors_YYYYMMDD.json` |
| `--analyze` | LASSO·Granger·GMM·Rolling OLS·Lead-Lag 분석 → `outputs/context/analysis_YYYYMMDD.json` |
| `--report` | PwC 컨설팅 스타일 보고서 생성 → `outputs/reports/report_YYYYMMDD.md` |
| `--chart` | 차트 생성 → `outputs/charts/` |

## 워크플로

### Step 1: 환경 확인

**Use skill: "factor-research"** 를 로드하여 Factor Pool 도메인 지식을 준비합니다.

- `FRED_API_KEY` 환경변수 설정 확인
- `outputs/` 디렉토리 존재 확인

### Step 2: 데이터 수집

```bash
python main.py --collect
```

수집 후 확인:
- `outputs/context/factors_YYYYMMDD.json` 생성 여부
- 16개 Factor 각각 데이터 존재 여부 (결측 시 FRED ID 확인)
- 이상치 점검: 2020-03~04 팬데믹 구간 spike 정상 범위 내인지

**Human-in-the-Loop Gate [1]**: 데이터 이상치 확인 후 다음 단계 진행

### Step 3: 분석 실행

```bash
python main.py --analyze
```

분석 결과 확인:
- LASSO 선별 Factor ≥ 3개 (비영 계수)
- Granger STRONG/MODERATE Factor ≥ 1개
- GMM 레짐 신뢰도 > 50%

**Human-in-the-Loop Gate [2]**: LASSO 선별 Factor 적절성 도메인 검토

### Step 4: 보고서 생성

**Use skill: "consulting-context"** 를 로드하여 PwC 컨설팅 보고서 형식을 준비합니다.

```bash
python main.py --report
```

보고서 품질 체크:
- None 값 없이 완성되었는가
- Executive Summary 한 줄 결론이 명확한가
- Section 4 시나리오 3개 + 권고 포함되었는가

**Human-in-the-Loop Gate [3]**: 수치 출처·None 값·컨설팅 함의 최종 검토

### Step 5: 테스트 & 린트

```bash
python -m pytest tests/ -q && ruff check src/
```

## 출력물 위치

| 출력물 | 경로 |
|--------|------|
| Factor 데이터 | `outputs/context/factors_YYYYMMDD.json` |
| 분석 결과 | `outputs/context/analysis_YYYYMMDD.json` |
| 보고서 | `outputs/reports/report_YYYYMMDD.md` |
| 차트 | `outputs/charts/*.png` |
