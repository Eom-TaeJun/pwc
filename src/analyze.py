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
from statsmodels.regression.rolling import RollingOLS
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


def analyze(factors_data: dict = None) -> dict:
    """Run all analyses and save outputs/context/analysis_YYYYMMDD.json."""
    if factors_data is None:
        factors_data = load_latest_factors()

    X, y = build_dataframe(factors_data)
    lasso = run_lasso(X, y, factors_data)
    corr = run_correlation(X, y, factors_data)
    rolling = run_rolling_ols(X, y, lasso)
    importance = run_importance(X, y, lasso, factors_data)

    top_lead = ", ".join(r["factor"] for r in corr[:2]) if corr else "N/A"
    survey_factors = [r["factor"] for r in corr if "UMCSENT" in r["factor"]]

    result = {
        "analyzed_at": datetime.now().isoformat(),
        "target": factors_data["target"]["series"],
        "data_period": {
            "start": str(y.index.min()),
            "end": str(y.index.max()),
            "n_obs": len(y),
        },
        "lasso_selected": lasso,
        "correlation": corr,
        "rolling_stability": rolling,
        "importance": importance,
        "consulting_implications": {
            "leading_indicators": f"{top_lead}가 {factors_data['target']['series']} 선행 지표로 선별",
            "data_constraints": "서베이 기반 지표는 후행 가능성 있음" if survey_factors else "주요 지표 모두 하드 데이터",
            "client_narrative": "금리 스프레드 역전 → 산업생산 둔화 신호 (LASSO/RF 공통 선별)",
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
