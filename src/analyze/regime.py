"""GMM 3-state 레짐 탐지 + Shannon Entropy 신뢰도 (EIMAS 이식)."""
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def run_regime(y: pd.Series) -> dict:
    """Expansion / Neutral / Contraction 레짐 판별.

    신뢰도 = (1 - Shannon Entropy) * 100   — 0%: 완전 불확실, 100%: 완전 확실.
    """
    clean = y.dropna()
    if len(clean) < 60:
        return {"regime": "UNKNOWN", "probs": {}, "entropy": 1.0,
                "confidence": 0, "regime_series": []}

    s = pd.Series(clean.values)
    X = np.column_stack([
        s.values,
        s.rolling(12).mean().bfill().values,
        s.rolling(12).std().bfill().values,
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
