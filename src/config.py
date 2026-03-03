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
