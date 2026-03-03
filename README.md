# PwC Factor Pool 리서치

FRED 거시경제 변수 20개에서 LASSO로 핵심 선행지표를 선별하고,
Rolling OLS 안정성과 RF Feature Importance로 검증하는 포트폴리오 프로젝트.
Target: INDPRO (산업생산지수 MoM%).

---

## 설치

```bash
pip install -r requirements.txt
cp .env.example .env   # FRED_API_KEY 입력
```

---

## 실행

```bash
python main.py --factors       # FRED 20개 Factor 수집
python main.py --correlate     # 상관관계 + lag 분석
python main.py --importance    # LASSO 선별 + RF Feature Importance
python main.py --report        # 컨설팅 보고서 생성
python main.py --all           # 전체 파이프라인 실행
```

---

## 출력 구조

```
outputs/
├── context/          # 수집 데이터 JSON (factor_YYYYMMDD.json)
├── reports/          # 분석 보고서 MD (factor_report_YYYYMMDD.md)
└── charts/           # 시각화 PNG (factor_importance_YYYYMMDD.png)
```

---

## 에이전트

| 에이전트 | 모델 | 역할 |
|---------|------|------|
| `pwc-lead` | sonnet | 파이프라인 조율 + 품질 검토 |
| `factor-collector` | haiku | FRED 데이터 수집 (경량) |
| `lasso-analyst` | sonnet | LASSO + 통계 분석 |
| `report-writer` | sonnet | 컨설팅 보고서 작성 |
