"""Random Forest Feature Importance."""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def run_importance(X: pd.DataFrame, y: pd.Series,
                   selected_factors: list, factors_data: dict = None) -> list:
    """RF feature importance on LASSO-selected factors (fallback: all)."""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}
    factors = [f["factor"] for f in selected_factors] or list(X.columns)
    factors = [f for f in factors if f in X.columns]
    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X[factors], y)
    return [
        {"factor": fac, "importance": round(imp, 6), "rank": i + 1,
         "label": label_map.get(fac, fac)}
        for i, (fac, imp) in enumerate(
            sorted(zip(factors, rf.feature_importances_), key=lambda t: t[1], reverse=True)
        )
    ]
