"""Granger 인과관계 검증 (ADF 정상성 변환 → F-test, EIMAS 이식)."""
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests, adfuller

from src.config import GRANGER_MAX_LAG, GRANGER_STRONG, GRANGER_MODERATE, GRANGER_WEAK


def _stationary(s: pd.Series) -> pd.Series:
    for _ in range(2):
        try:
            if adfuller(s.dropna())[1] < 0.05:
                return s
        except Exception:
            return s
        s = s.diff()
    return s


def run_granger(X: pd.DataFrame, y: pd.Series,
                factors_data: dict = None, max_lag: int = GRANGER_MAX_LAG) -> list:
    """Factor → INDPRO Granger causality."""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}

    results, y_stat = [], _stationary(y)
    for col in X.columns:
        try:
            df = pd.DataFrame({"y": y_stat, "x": _stationary(X[col])}).dropna()
            if len(df) < max_lag * 3:
                continue
            gc = grangercausalitytests(df[["y", "x"]], maxlag=max_lag, verbose=False)
            best_lag, best_p, best_f = 1, 1.0, 0.0
            for lag in range(1, max_lag + 1):
                f, p = gc[lag][0]["ssr_ftest"][:2]
                if p < best_p:
                    best_lag, best_p, best_f = lag, p, f
            strength = ("STRONG" if best_p < GRANGER_STRONG
                        else "MODERATE" if best_p < GRANGER_MODERATE
                        else "WEAK" if best_p < GRANGER_WEAK else "NONE")
            if best_p < GRANGER_WEAK:
                results.append({"factor": col, "label": label_map.get(col, col),
                                 "optimal_lag": best_lag, "p_value": round(best_p, 6),
                                 "f_statistic": round(best_f, 4), "strength": strength})
        except Exception as e:
            print(f"  [Granger] {col} 실패: {e}")
    return sorted(results, key=lambda r: r["p_value"])
