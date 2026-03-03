"""Pearson 상관관계 분석 (시차별)."""
import pandas as pd
from scipy import stats

from src.config import CORR_LAGS


def run_correlation(X: pd.DataFrame, y: pd.Series, factors_data: dict) -> list:
    """Best lag (p<0.05) per factor; sorted by |corr| descending."""
    label_map = {fid: fd.get("label", fid)
                 for fid, fd in factors_data.get("factors", {}).items()}
    results = []
    for col in X.columns:
        best = {"corr": 0, "pvalue": 1, "lag_months": 0}
        for lag in CORR_LAGS:
            aligned = pd.concat([X[col].shift(lag), y], axis=1).dropna()
            if len(aligned) < 10:
                continue
            r, p = stats.pearsonr(aligned.iloc[:, 0], aligned.iloc[:, 1])
            if p < 0.05 and abs(r) > abs(best["corr"]):
                best = {"corr": round(r, 4), "pvalue": round(p, 6), "lag_months": lag}
        if best["pvalue"] < 0.05:
            results.append({"factor": col, "label": label_map.get(col, col), **best})
    return sorted(results, key=lambda r: abs(r["corr"]), reverse=True)
