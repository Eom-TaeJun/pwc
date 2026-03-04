import json
import os
from datetime import datetime
import requests

OUTPUT_DIR = "outputs/context"
FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES_META = {
    "FEDFUNDS": {"label": "Fed Funds Rate", "transform": "level"},
    "DGS10": {"label": "10Y Treasury Yield", "transform": "level"},
    "DGS2": {"label": "2Y Treasury Yield", "transform": "level"},
    "T10Y2Y": {"label": "10Y-2Y Yield Spread", "transform": "level"},
    "CPIAUCSL": {"label": "CPI YoY%", "transform": "yoy"},
    "PPIACO": {"label": "PPI MoM%", "transform": "mom"},
    "UNRATE": {"label": "실업률", "transform": "level"},
    "PAYEMS": {"label": "비농업고용 MoM 증감(천명)", "transform": "diff"},
    "RETAILSMNSA": {"label": "소매판매 MoM%", "transform": "mom"},
    "HOUST": {"label": "주택착공 MoM%", "transform": "mom"},
    "UMCSENT": {"label": "미시간 소비자심리", "transform": "level"},
    "M2SL": {"label": "M2 통화량 MoM%", "transform": "mom"},
    "DEXUSEU": {"label": "USD/EUR 환율", "transform": "level"},
    "DCOILWTICO": {"label": "WTI 유가 MoM%", "transform": "mom"},
    "VIXCLS": {"label": "VIX 변동성지수", "transform": "level"},
    "TCU": {"label": "설비가동률(%)", "transform": "level"},
}

def fetch_fred_series(series_id: str, start: str = "2000-01-01") -> list:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
        "frequency": "m",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        obs = r.json().get("observations", [])
        return [(o["date"], float(o["value"])) for o in obs if o["value"] not in (".", "")]
    except Exception as e:
        print(f"Warning: {series_id} failed: {e}")
        return []

def apply_transform(raw: list, transform: str) -> list:
    if not raw or len(raw) < 2:
        return []

    data = [(d, v) for d, v in raw if v is not None]
    if transform == "level":
        return [{"date": d, "value": round(v, 4)} for d, v in data]

    result = []
    for i in range(1, len(data)):
        date, val = data[i]
        prev_val = data[i - 1][1]

        if transform == "mom":
            pct = ((val / prev_val) - 1) * 100
        elif transform == "yoy":
            prev_val = data[i - 12][1] if i >= 12 else prev_val
            pct = ((val / prev_val) - 1) * 100
        elif transform == "diff":
            pct = val - prev_val

        result.append({"date": date, "value": round(pct, 4)})

    return result

def collect() -> dict:
    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY env var not set")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    target_raw = fetch_fred_series("INDPRO")
    target = {
        "series": "INDPRO",
        "label": "산업생산지수 MoM%",
        "data": apply_transform(target_raw, "mom"),
    }

    factors = {}
    for series_id, meta in SERIES_META.items():
        raw = fetch_fred_series(series_id)
        factors[series_id] = {
            "label": meta["label"],
            "transform": meta["transform"],
            "data": apply_transform(raw, meta["transform"]),
        }

    result = {
        "collected_at": datetime.utcnow().isoformat() + "Z",
        "target": target,
        "factors": factors,
    }

    timestamp = datetime.now().strftime("%Y%m%d")
    outfile = f"{OUTPUT_DIR}/factors_{timestamp}.json"
    with open(outfile, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Saved: {outfile}")
    return result

if __name__ == "__main__":
    collect()
