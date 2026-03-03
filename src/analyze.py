"""
목적: LASSO 선행지표 선별 + 상관관계 + Rolling OLS + RF Feature Importance
입력: outputs/context/factors_YYYYMMDD.json
출력: outputs/context/analysis_YYYYMMDD.json
제외: 딥러닝, 실시간 데이터
"""
import json, os, glob
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from statsmodels.regression.rolling import RollingOLS
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
import statsmodels.api as sm
from scipy import stats

OUTPUT_DIR = "outputs/context"


def load_latest_factors() -> dict:
    """Load the most recent factors_YYYYMMDD.json from OUTPUT_DIR."""
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "factors_*.json")))
    if not files:
        raise FileNotFoundError(f"No factors files in {OUTPUT_DIR}")
    with open(files[-1]) as f:
        return json.load(f)


def build_dataframe(factors_data: dict) -> tuple:
    """Convert factors_data into aligned (X, y) with date index."""
    y = pd.Series(
        {d["date"]: d["value"] for d in factors_data["target"]["data"]},
        name=factors_data["target"]["series"],
    ).sort_index()

    cols = {}
    for factor_id, factor_data in factors_data.get("factors", {}).items():
        cols[factor_id] = {d["date"]: d["value"] for d in factor_data.get("data", [])}

    X = pd.DataFrame(cols).sort_index()
    common = X.index.intersection(y.index)
    X, y = X.loc[common].dropna(), y.loc[common]
    common = X.index.intersection(y.index)
    return X.loc[common], y.loc[common]


def run_lasso(X: pd.DataFrame, y: pd.Series, factors_data: dict = None) -> list:
    """Select factors via LassoCV; return non-zero coefficients sorted by magnitude."""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid) for fid, fd in factors_data.get("factors", {}).items()}
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = LassoCV(cv=5, max_iter=10000).fit(Xs, y)
    results = [
        {"factor": col, "coefficient": round(coef, 4), "label": label_map.get(col, col)}
        for col, coef in zip(X.columns, model.coef_)
        if coef != 0
    ]
    return sorted(results, key=lambda r: abs(r["coefficient"]), reverse=True)


def run_correlation(X: pd.DataFrame, y: pd.Series, factors_data: dict) -> list:
    """Find best lag (0,3,6,12m) per factor using Pearson r, p<0.05."""
    label_map = {fid: fd.get("label", fid) for fid, fd in factors_data.get("factors", {}).items()}
    results = []
    for col in X.columns:
        best = {"corr": 0, "pvalue": 1, "lag_months": 0}
        for lag in [0, 3, 6, 12]:
            x_lag = X[col].shift(lag)
            aligned = pd.concat([x_lag, y], axis=1).dropna()
            if len(aligned) < 10:
                continue
            r, p = stats.pearsonr(aligned.iloc[:, 0], aligned.iloc[:, 1])
            if p < 0.05 and abs(r) > abs(best["corr"]):
                best = {"corr": round(r, 4), "pvalue": round(p, 6), "lag_months": lag}
        if best["pvalue"] < 0.05:
            results.append({"factor": col, "label": label_map.get(col, col), **best})
    return sorted(results, key=lambda r: abs(r["corr"]), reverse=True)


def run_rolling_ols(X: pd.DataFrame, y: pd.Series, selected_factors: list, window: int = 36) -> dict:
    """Rolling OLS on LASSO-selected factors (up to 5); classify stability."""
    factors = [f["factor"] for f in selected_factors[:5]]
    if not factors:
        return {"stable_factors": [], "unstable_factors": [], "rolling_coefs": {}}

    Xsub = sm.add_constant(X[factors])
    model = RollingOLS(y, Xsub, window=window).fit()
    params = model.params.dropna()

    rolling_coefs, stable, unstable = {}, [], []
    for fac in factors:
        if fac not in params.columns:
            continue
        series = params[fac].dropna()
        ratio = abs(series.std() / series.mean()) if series.mean() != 0 else np.inf
        rolling_coefs[fac] = [{"date": d, "coef": round(v, 6)} for d, v in series.items()]
        (stable if ratio < 0.5 else unstable).append(fac)

    return {"stable_factors": stable, "unstable_factors": unstable, "rolling_coefs": rolling_coefs}


def run_importance(X: pd.DataFrame, y: pd.Series, selected_factors: list, factors_data: dict = None) -> list:
    """RF feature importance on LASSO-selected factors (fallback: all)."""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid) for fid, fd in factors_data.get("factors", {}).items()}
    factors = [f["factor"] for f in selected_factors] or list(X.columns)
    factors = [f for f in factors if f in X.columns]
    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X[factors], y)
    results = [
        {"factor": fac, "importance": round(imp, 6), "rank": i + 1, "label": label_map.get(fac, fac)}
        for i, (fac, imp) in enumerate(
            sorted(zip(factors, rf.feature_importances_), key=lambda t: t[1], reverse=True)
        )
    ]
    return results


def run_regime(y: pd.Series) -> dict:
    """GMM 3-state regime detection on INDPRO MoM%. (EIMAS regime_analyzer.py 이식)
    Expansion / Neutral / Contraction + Shannon Entropy 신뢰도."""
    clean = y.dropna()
    if len(clean) < 60:
        return {"regime": "UNKNOWN", "probs": {}, "entropy": 1.0, "confidence": 0, "regime_series": []}

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

    # 평균 수익률 기준 정렬: Contraction(낮음) → Neutral → Expansion(높음)
    sorted_idx = np.argsort(gmm.means_[:, 0])
    labels = {sorted_idx[0]: "Contraction", sorted_idx[1]: "Neutral", sorted_idx[2]: "Expansion"}

    probs_raw = gmm.predict_proba(Xs[-1:])[0]
    probs = {labels[i]: round(float(p), 4) for i, p in enumerate(probs_raw)}
    current_regime = labels[int(np.argmax(probs_raw))]

    # Shannon Entropy (정규화)
    p = probs_raw[probs_raw > 1e-10]
    entropy = round(float(-np.sum(p * np.log2(p)) / np.log2(3)), 4)
    confidence = round((1 - entropy) * 100, 1)

    regime_series = [
        {"date": str(d), "regime": labels[c]}
        for d, c in zip(clean.index, gmm.predict(Xs))
    ]
    return {"regime": current_regime, "probs": probs,
            "entropy": entropy, "confidence": confidence,
            "regime_series": regime_series}


def run_granger(X: pd.DataFrame, y: pd.Series,
                factors_data: dict = None, max_lag: int = 12) -> list:
    """Granger causality: Factor → INDPRO. (EIMAS shock_propagation/granger.py 이식)
    ADF 정상성 변환 → grangercausalitytests → 최적 lag + p-value."""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}

    def _stationary(s):
        for _ in range(2):
            try:
                if adfuller(s.dropna())[1] < 0.05:
                    return s
            except Exception:
                return s
            s = s.diff()
        return s

    results = []
    y_stat = _stationary(y)
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
            strength = ("STRONG" if best_p < 0.01 else
                        "MODERATE" if best_p < 0.05 else
                        "WEAK" if best_p < 0.10 else "NONE")
            if best_p < 0.10:
                results.append({"factor": col, "label": label_map.get(col, col),
                                 "optimal_lag": best_lag,
                                 "p_value": round(best_p, 6),
                                 "f_statistic": round(best_f, 4),
                                 "strength": strength})
        except Exception as e:
            print(f"  [Granger] {col} 실패: {e}")
    return sorted(results, key=lambda r: r["p_value"])


def run_lead_lag(X: pd.DataFrame, y: pd.Series,
                 factors_data: dict = None, max_lag: int = 12) -> list:
    """Cross-correlation lead-lag: Factor가 INDPRO를 몇 개월 선행하는가.
    (EIMAS shock_propagation/lead_lag.py 이식)"""
    label_map = {}
    if factors_data:
        label_map = {fid: fd.get("label", fid)
                     for fid, fd in factors_data.get("factors", {}).items()}

    results = []
    for col in X.columns:
        corrs = {}
        for lag in range(-max_lag, max_lag + 1):
            if lag > 0:
                c = X[col].iloc[:-lag].corr(y.iloc[lag:])
            elif lag < 0:
                c = X[col].iloc[-lag:].corr(y.iloc[:lag])
            else:
                c = X[col].corr(y)
            corrs[lag] = float(c) if not np.isnan(c) else 0.0

        opt_lag = max(corrs, key=lambda k: abs(corrs[k]))
        max_corr = corrs[opt_lag]
        zero_corr = corrs[0]
        is_leading = opt_lag > 0 and abs(max_corr) > abs(zero_corr)

        results.append({"factor": col, "label": label_map.get(col, col),
                         "optimal_lag": opt_lag,
                         "max_corr": round(max_corr, 4),
                         "zero_corr": round(zero_corr, 4),
                         "is_leading": is_leading})

    return sorted(results, key=lambda r: (-int(r["is_leading"]), -abs(r["max_corr"])))


def analyze(factors_data: dict = None) -> dict:
    """Run all analyses and save outputs/context/analysis_YYYYMMDD.json."""
    if factors_data is None:
        factors_data = load_latest_factors()

    X, y = build_dataframe(factors_data)
    lasso    = run_lasso(X, y, factors_data)
    corr     = run_correlation(X, y, factors_data)
    rolling  = run_rolling_ols(X, y, lasso)
    importance = run_importance(X, y, lasso, factors_data)
    regime   = run_regime(y)
    granger  = run_granger(X, y, factors_data)
    lead_lag = run_lead_lag(X, y, factors_data)

    survey_factors = [r["factor"] for r in corr if "UMCSENT" in r["factor"]]
    top_g   = granger[0] if granger else None
    top_fac = top_g["factor"] if top_g else (corr[0]["factor"] if corr else "N/A")
    top_lag = top_g["optimal_lag"] if top_g else 0
    reg_str = regime.get("regime", "N/A")
    reg_conf = regime.get("confidence", 0)

    result = {
        "analyzed_at": datetime.now().isoformat(),
        "target": factors_data["target"]["series"],
        "data_period": {
            "start": str(y.index.min()),
            "end": str(y.index.max()),
            "n_obs": len(y),
        },
        "regime": regime,
        "lasso_selected": lasso,
        "correlation": corr,
        "granger": granger,
        "lead_lag": lead_lag,
        "rolling_stability": rolling,
        "importance": importance,
        "consulting_implications": {
            "current_regime": f"{reg_str} (신뢰도 {reg_conf}%)",
            "leading_indicators": (
                f"{top_fac}가 INDPRO {top_lag}개월 선행"
                + (f" (Granger {top_g['strength']})" if top_g else "")
            ),
            "data_constraints": "서베이 기반 지표(UMCSENT)는 후행 가능성 있음" if survey_factors else "주요 지표 모두 하드 데이터",
            "client_narrative": f"현재 산업생산 레짐: {reg_str}. {top_fac} 신호 추이가 생산계획 조기 경보 역할",
        },
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"analysis_{datetime.now().strftime('%Y%m%d')}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_path}")
    return result


if __name__ == "__main__":
    analyze()
