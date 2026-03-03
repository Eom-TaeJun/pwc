"""LASSO 선행지표 선별 (LassoCV)."""
import pandas as pd
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

from src.config import LASSO_CV_FOLDS


def run_lasso(X: pd.DataFrame, y: pd.Series, factors_data: dict = None) -> dict:
    """Non-zero LASSO coefficients sorted by magnitude.

    Returns:
        {"selected": [...], "alpha": float}  — alpha는 CV 선택값 (재현성 기록용)
    """
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = LassoCV(cv=LASSO_CV_FOLDS, max_iter=10000).fit(Xs, y)
    selected = [
        {"factor": col, "coefficient": round(coef, 4), "label": label_map.get(col, col)}
        for col, coef in zip(X.columns, model.coef_)
        if coef != 0
    ]
    return {
        "selected": sorted(selected, key=lambda r: abs(r["coefficient"]), reverse=True),
        "alpha": round(float(model.alpha_), 6),
    }
