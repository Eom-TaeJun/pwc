"""지정 기간 Factor 분석 — 통화정책 사이클 / 이벤트 전후 공통 프레임워크."""
import pandas as pd

from .lasso import run_lasso
from .granger import run_granger
from .correlation import run_correlation
from .rolling import run_rolling_ols
from src.config import SHORT_GRANGER_MAX_LAG, SHORT_ROLLING_WINDOW


def run_period_analysis(
    X: pd.DataFrame, y: pd.Series, factors_data: dict,
    start: str = None, end: str = None, label: str = "",
) -> dict:
    """지정 기간 슬라이스로 LASSO + Granger + 상관관계 분석.

    Args:
        start / end: "YYYY-MM-DD" 형식. None이면 경계 없음.
        label: 보고서용 기간 이름 (예: "금리 인하기 (2024-09~)")

    Returns:
        dict with keys: label, data_period, lasso_selected,
        granger_leading, correlation, rolling_stability,
        effective_rolling_window.
        관측 수 부족(< 18) 시 {"error": ..., "label": label} 반환.
    """
    Xp = _slice(X, start, end)
    yp = _slice(y, start, end)

    if len(yp) < 18:
        return {"error": f"관측 수 부족 ({len(yp)}개)", "label": label,
                "data_period": {"n_obs": len(yp)}}

    window = max(6, min(SHORT_ROLLING_WINDOW, len(yp) // 3))
    lasso_r  = run_lasso(Xp, yp, factors_data)
    granger  = run_granger(Xp, yp, factors_data, max_lag=SHORT_GRANGER_MAX_LAG)
    corr     = run_correlation(Xp, yp, factors_data)
    rolling  = run_rolling_ols(Xp, yp, lasso_r["selected"], window=window)

    return {
        "label": label,
        "data_period": {
            "start": str(yp.index.min()), "end": str(yp.index.max()),
            "n_obs": len(yp),
        },
        "lasso_selected": lasso_r["selected"],
        "granger_leading": [
            {"factor": g["factor"], "label": g["label"],
             "lag": g["optimal_lag"], "strength": g["strength"]}
            for g in granger if g["strength"] in ("STRONG", "MODERATE")
        ],
        "correlation": corr,
        "rolling_stability": rolling,
        "effective_rolling_window": window,
    }


def _slice(s, start, end):
    if start and end:
        return s.loc[start:end]
    if start:
        return s.loc[start:]
    if end:
        return s.loc[:end]
    return s
