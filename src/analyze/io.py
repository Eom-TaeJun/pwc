"""데이터 로딩 + DataFrame 빌드."""
import json, os, glob
import pandas as pd

OUTPUT_DIR = "outputs/context"


def load_latest_factors() -> dict:
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "factors_*.json")))
    if not files:
        raise FileNotFoundError(f"No factors files in {OUTPUT_DIR}")
    with open(files[-1]) as f:
        return json.load(f)


def build_dataframe(factors_data: dict) -> tuple:
    """factors_data → (X: DataFrame, y: Series) with aligned date index."""
    y = pd.Series(
        {d["date"]: d["value"] for d in factors_data["target"]["data"]},
        name=factors_data["target"]["series"],
    ).sort_index()

    cols = {
        fid: {d["date"]: d["value"] for d in fd.get("data", [])}
        for fid, fd in factors_data.get("factors", {}).items()
    }
    X = pd.DataFrame(cols).sort_index()
    common = X.index.intersection(y.index)
    X, y = X.loc[common].dropna(), y.loc[common]
    common = X.index.intersection(y.index)
    return X.loc[common], y.loc[common]
