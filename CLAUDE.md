# pwc-factor — Claude Code 운영 규칙

## 경로 규칙

| 역할 | 경로 |
|------|------|
| 데이터 수집 | `src/collect.py` |
| 분석 패키지 | `src/analyze/` (io · lasso · correlation · rolling · importance · regime · granger · lead_lag) |
| 차트 생성 | `src/chart.py` |
| 보고서 생성 | `src/report.py` |
| 출력 루트 | `outputs/` (gitignore) |

## NEVER

- `outputs/` 외부에 데이터/차트/보고서 저장 금지
- `.env` 파일 직접 수정 금지 (FRED_API_KEY 노출 방지)
- `src/analyze/` 파일을 하나로 병합하지 말 것 (각 파일 60줄 이하 유지)
- PDF 변환, 웹 대시보드 추가 금지 (Markdown + PNG 출력만)

## MUST

- 신규 분석 함수는 `src/analyze/` 하위 파일에 추가
- 차트 저장 시 `outputs/charts/` 경로 + `dpi=150`
- 수치 출처 명기: "FRED (Federal Reserve Bank of St. Louis)"
- `consulting-context` 스킬은 읽기 전용 — 수정 금지

## 실행 명령어

```bash
python main.py --factors      # FRED 수집
python main.py --all          # 전체 파이프라인
```

## 검증

```bash
python -c "from src.analyze import analyze; print('OK')"
python -m pytest tests/ -q
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
