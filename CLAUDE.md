# pwc-factor — Claude Code 운영 규칙

> 세부 명세(방법론 결정 이유, 성공 기준, 데이터 제약)는 `spec.md` 참조.

## 경로

| 역할 | 경로 |
|------|------|
| 데이터 수집 | `src/collect.py` |
| 분석 패키지 | `src/analyze/` (io · lasso · correlation · rolling · importance · regime · granger · lead_lag) |
| 차트 생성 | `src/chart.py` |
| 보고서 생성 | `src/report.py` |
| 출력 루트 | `outputs/` (gitignore) |

## NEVER — 절대 금지

- **NEVER** `outputs/` 외부에 데이터·차트·보고서 저장
- **NEVER** `.env` 직접 수정 (FRED_API_KEY 노출)
- **NEVER** `src/analyze/` 파일을 단일 파일로 병합 (각 모듈 60줄 이하 유지)
- **NEVER** PDF 변환, 웹 대시보드 추가 (Markdown + PNG만)
- **NEVER** `.claude/skills/` 파일 수정 (읽기 전용 도메인 지식)

## MUST — 반드시 준수

- **MUST** 신규 분석 함수는 `src/analyze/` 하위 모듈에 추가
- **MUST** 차트 저장: `outputs/charts/`, `dpi=150`
- **MUST** 수치 출처 명기: "FRED (Federal Reserve Bank of St. Louis)"
- **MUST** 변경 후 검증: `python -m pytest tests/ -q && ruff check src/`
- **MUST** 보고서에 None 값 없이 완성 후 커밋

## 실행

```bash
python main.py --all          # 전체 파이프라인
python -m pytest tests/ -q    # 테스트
ruff check src/               # 린트
```

## 어휘 레지스터

| 사용 | 금지 |
|------|------|
| Factor Pool | 변수 풀 |
| 선행지표 선별 | 변수 선택 |
| LASSO 선별 | 회귀 필터링 |
| Rolling OLS 안정성 | 슬라이딩 윈도우 |
| Feature Importance | 피처 중요도 |
| 컨설팅 함의 | 결론 |
