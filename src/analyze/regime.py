"""GMM 3-state 레짐 탐지 + Shannon Entropy 신뢰도 (EIMAS 이식)."""
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def run_regime(y: pd.Series) -> dict:
    """Expansion / Neutral / Contraction 레짐 판별.

    피처: winsorize(2-98%) + 12m_mean + 6m_mean
    - 이전: MoM% + 12m_mean + 12m_std → 극값(2020 V자 반등)이 Expansion 독점 문제
    - 개선: winsorize로 극값 완화 + std 제거 → 경제 사이클 균형적 포착
    신뢰도 = (1 - Shannon Entropy) * 100   — 0%: 완전 불확실, 100%: 완전 확실.
    """
    clean = y.dropna()
    if len(clean) < 60:
        return {"regime": "UNKNOWN", "probs": {}, "entropy": 1.0,
                "confidence": 0, "regime_series": []}

    s = pd.Series(clean.values)
    # winsorize: 극값 충격(2020 팬데믹 등)이 클러스터를 독점하지 않도록 2-98% 절단
    lo, hi = float(s.quantile(0.02)), float(s.quantile(0.98))
    s_w = s.clip(lo, hi)
    X = np.column_stack([
        s_w.values,
        s_w.rolling(12, min_periods=6).mean().bfill().values,
        s_w.rolling(6, min_periods=3).mean().bfill().values,
    ])
    Xs = StandardScaler().fit_transform(X)

    gmm = GaussianMixture(n_components=3, covariance_type="full",
                          max_iter=200, random_state=42, n_init=5)
    gmm.fit(Xs)

    sorted_idx = np.argsort(gmm.means_[:, 0])
    labels = {sorted_idx[0]: "Contraction", sorted_idx[1]: "Neutral",
              sorted_idx[2]: "Expansion"}

    probs_raw = gmm.predict_proba(Xs[-1:])[0]
    probs = {labels[i]: round(float(p), 4) for i, p in enumerate(probs_raw)}
    current = labels[int(np.argmax(probs_raw))]

    p = probs_raw[probs_raw > 1e-10]
    entropy = round(float(-np.sum(p * np.log2(p)) / np.log2(3)), 4)

    return {
        "regime": current, "probs": probs,
        "entropy": entropy, "confidence": round((1 - entropy) * 100, 1),
        "regime_series": [
            {"date": str(d), "regime": labels[c]}
            for d, c in zip(clean.index, gmm.predict(Xs))
        ],
    }
