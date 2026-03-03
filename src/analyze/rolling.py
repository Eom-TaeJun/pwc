"""Rolling OLS 안정성 검증."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from src.config import ROLLING_WINDOW, ROLLING_STABILITY_THRESHOLD, ROLLING_TOP_N


def run_rolling_ols(X: pd.DataFrame, y: pd.Series,
                    selected_factors: list,
                    window: int = ROLLING_WINDOW) -> dict:
    """Classify LASSO-selected factors as stable/unstable.

    Stability criterion: |std/mean| < ROLLING_STABILITY_THRESHOLD → stable.
    Returns _params for report transparency.
    """
    factors = [f["factor"] for f in selected_factors[:ROLLING_TOP_N]]
    if not factors:
        return {"stable_factors": [], "unstable_factors": [], "rolling_coefs": {},
                "_params": {"window": window, "threshold": ROLLING_STABILITY_THRESHOLD}}

    Xsub = sm.add_constant(X[factors])
    params = RollingOLS(y, Xsub, window=window).fit().params.dropna()

    rolling_coefs, stable, unstable = {}, [], []
    for fac in factors:
        if fac not in params.columns:
            continue
        series = params[fac].dropna()
        ratio = abs(series.std() / series.mean()) if series.mean() != 0 else np.inf
        rolling_coefs[fac] = [{"date": d, "coef": round(v, 6)} for d, v in series.items()]
        (stable if ratio < ROLLING_STABILITY_THRESHOLD else unstable).append(fac)

    return {"stable_factors": stable, "unstable_factors": unstable,
            "rolling_coefs": rolling_coefs,
            "_params": {"window": window, "threshold": ROLLING_STABILITY_THRESHOLD}}
