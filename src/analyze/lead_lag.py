"""Cross-correlation lead-lag 분석 (level 시계열 → MoM diff 통일)."""
import numpy as np
import pandas as pd

from src.config import LEAD_LAG_MAX_LAG


def _to_mom(s: pd.Series) -> pd.Series:
    """Level 시계열(분산 증가 추세)을 MoM% diff로 변환해 INDPRO와 척도 맞춤.

    이미 차분 형태(변동률)이면 그대로 반환.
    판별 기준: 표준편차가 평균보다 작고 절댓값 범위가 50% 이내 → 이미 변화율로 가정.
    """
    clean = s.dropna()
    if len(clean) < 12:
        return s
    cv = abs(clean.std() / clean.mean()) if clean.mean() != 0 else np.inf
    if cv < 0.5:          # 이미 변화율(MoM% 등) 형태
        return s
    return s.pct_change() * 100   # level → MoM%


def run_lead_lag(X: pd.DataFrame, y: pd.Series,
                 factors_data: dict = None, max_lag: int = LEAD_LAG_MAX_LAG) -> list:
    """lag -12~+12 루프로 optimal lag 탐색.

    positive lag → Factor가 INDPRO를 선행 (is_leading=True).
    """
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}

    results = []
    for col in X.columns:
        x_adj = _to_mom(X[col])
        corrs = {}
        for lag in range(-max_lag, max_lag + 1):
            if lag > 0:
                c = x_adj.iloc[:-lag].corr(y.iloc[lag:])
            elif lag < 0:
                c = x_adj.iloc[-lag:].corr(y.iloc[:lag])
            else:
                c = x_adj.corr(y)
            corrs[lag] = float(c) if not np.isnan(c) else 0.0

        opt_lag = max(corrs, key=lambda k: abs(corrs[k]))
        max_corr = corrs[opt_lag]
        zero_corr = corrs[0]
        is_leading = opt_lag > 0 and abs(max_corr) > abs(zero_corr)

        results.append({"factor": col, "label": label_map.get(col, col),
                        "optimal_lag": opt_lag, "max_corr": round(max_corr, 4),
                        "zero_corr": round(zero_corr, 4), "is_leading": is_leading})

    return sorted(results, key=lambda r: (-int(r["is_leading"]), -abs(r["max_corr"])))
