"""INDPRO 구조 변화 시점 탐지 — ruptures PELT (rbf) + fallback.

Method: Pruned Exact Linear Time (PELT) with RBF kernel cost.
비모수적 분포 변화(수준·분산·자기상관 구조 동시 탐지).
Paper: Truong, Oudre & Vayatis (2020), arXiv:1801.00826.
"""
import pandas as pd

from src.config import BREAK_MIN_SIZE, BREAK_PENALTY, SHORT_PERIOD_MONTHS

try:
    import ruptures as rpt
    _HAS_RUPTURES = True
except ImportError:
    _HAS_RUPTURES = False


def detect_breaks(y: pd.Series) -> list:
    """데이터 기반 구조 변화 시점 탐지 → 세그먼트 목록 반환.

    ruptures 미설치 또는 탐지 실패 시 최근 SHORT_PERIOD_MONTHS 창 1개 세그먼트로 폴백.

    Returns:
        list of {"start", "end", "n_obs", "segment"} — 마지막 = 현재(최근) 세그먼트.
    """
    clean = y.dropna()
    if not _HAS_RUPTURES or len(clean) < BREAK_MIN_SIZE * 2:
        return [_make_seg(clean.iloc[-SHORT_PERIOD_MONTHS:], 1, fallback=True)]

    try:
        algo = rpt.Pelt(model="rbf", min_size=BREAK_MIN_SIZE, jump=1)
        raw = algo.fit(clean.values.reshape(-1, 1)).predict(pen=BREAK_PENALTY)
        bkps = [b for b in raw if b < len(clean)]
    except Exception:
        return [_make_seg(clean.iloc[-SHORT_PERIOD_MONTHS:], 1, fallback=True)]

    if not bkps:
        return [_make_seg(clean, 1)]

    segments = []
    for i, (s, e) in enumerate(zip([0] + bkps, bkps + [len(clean)])):
        seg = clean.iloc[s:e]
        if len(seg) >= BREAK_MIN_SIZE:
            segments.append(_make_seg(seg, i + 1))

    return segments or [_make_seg(clean.iloc[-SHORT_PERIOD_MONTHS:], 1, fallback=True)]


def _make_seg(s: pd.Series, idx: int, fallback: bool = False) -> dict:
    d = {"start": str(s.index[0]), "end": str(s.index[-1]),
         "n_obs": len(s), "segment": idx}
    if fallback:
        d["fallback"] = True
    return d
