"""Rolling OLS 안정성 검증 (36개월 창)."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS


def run_rolling_ols(X: pd.DataFrame, y: pd.Series,
                    selected_factors: list, window: int = 36) -> dict:
    """Classify LASSO-selected factors as stable/unstable (|std/mean| threshold 0.5)."""
    factors = [f["factor"] for f in selected_factors[:5]]
    if not factors:
        return {"stable_factors": [], "unstable_factors": [], "rolling_coefs": {}}

    Xsub = sm.add_constant(X[factors])
    params = RollingOLS(y, Xsub, window=window).fit().params.dropna()

    rolling_coefs, stable, unstable = {}, [], []
    for fac in factors:
        if fac not in params.columns:
            continue
        series = params[fac].dropna()
        ratio = abs(series.std() / series.mean()) if series.mean() != 0 else np.inf
        rolling_coefs[fac] = [{"date": d, "coef": round(v, 6)} for d, v in series.items()]
        (stable if ratio < 0.5 else unstable).append(fac)

    return {"stable_factors": stable, "unstable_factors": unstable,
            "rolling_coefs": rolling_coefs}
