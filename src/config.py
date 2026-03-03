"""분석 파라미터 중앙 관리 — 여기만 바꾸면 코드·보고서 텍스트 모두 반영."""

# LASSO
LASSO_CV_FOLDS: int = 5

# Random Forest
RF_N_ESTIMATORS: int = 100
RF_RANDOM_STATE: int = 42

# Rolling OLS
ROLLING_WINDOW: int = 36          # 개월
ROLLING_STABILITY_THRESHOLD: float = 0.5  # |std/mean| 기준

# Granger Causality
GRANGER_MAX_LAG: int = 12         # 최대 검증 lag (개월)
GRANGER_STRONG: float = 0.01
GRANGER_MODERATE: float = 0.05
GRANGER_WEAK: float = 0.10

# Lead-Lag Cross-Correlation
LEAD_LAG_MAX_LAG: int = 12        # ± 개월

# Correlation
CORR_LAGS: list = [0, 3, 6, 12]  # 검증 시차 (개월)

# Rolling OLS — 상위 Factor 수
ROLLING_TOP_N: int = 5

# Short-Period Analysis (단기 집중 분석)
SHORT_PERIOD_MONTHS: int = 60        # fallback: ruptures 미설치 시 최근 N개월 창
SHORT_ROLLING_WINDOW: int = 24       # 단기 Rolling OLS 창 (상한; 세그먼트 길이에 맞게 자동 축소)
SHORT_GRANGER_MAX_LAG: int = 6       # 단기 Granger 최대 Lag (데이터 부족 방지)

# Structural Break Detection — ruptures PELT (rbf)
# Paper: Truong et al. (2020) arXiv:1801.00826
# min_size 근거:
#   - Bry-Boschan (1971) 비즈니스 사이클 최소 국면 = 5개월 (월간 데이터 표준)
#   - CEPR/NBER 실무 관례 = 6개월
#   - Bai-Perron ε=0.10 (T=300) = 30개월 → 거시경제 구조 변화 검정용이나
#     2020 COVID(2개월 저점), 2022 금리 인상(16개월) 탐지에는 과보수적
#   - 결론: 6개월 = Bry-Boschan 하한 + 단기 경제 사이클 탐지 균형점
BREAK_PENALTY: float = 15.0          # 높을수록 break 수 감소 (경험값: 2~4개 기대)
BREAK_MIN_SIZE: int = 6              # 세그먼트 최소 길이 (개월) — Bry-Boschan 하한

# ── 이벤트 기반 기간 분할 기준 (Named Segments) ──────────────────────────────
# 고정 캘린더 기간 분할 — PELT가 아닌 경제적 이벤트 기반으로 명시적 정의
# 각 기준은 분석 보고서에 반드시 명기해야 함 (MUST per CLAUDE.md)

# 거시: 통화정책 사이클 (FRED FEDFUNDS 기반)
# Post-COVID → 2024-09: 초저금리 → 급격한 금리 인상 → 고금리 유지 = "고금리기"
# 2024-09-18: 연준 첫 금리 인하 (25bp, FOMC 성명) = 금리 인하 사이클 시작
RATE_HIGH_ERA_START: str = "2020-03-01"   # COVID 충격 → 제로금리 → 급격 인상 통합 기간
RATE_HIGH_ERA_END:   str = "2024-09-01"   # 연준 첫 인하 직전
RATE_CUT_ERA_START:  str = "2024-09-01"   # 연준 첫 인하 (2024-09-18 FOMC) 반영 월 시작
