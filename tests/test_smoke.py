"""Smoke tests — import 검증 + 함수 단위 mock 실행."""
import pytest
import pandas as pd
import numpy as np


# ── Import 검증 ──────────────────────────────────────────────────────────────

def test_imports():
    from src.analyze import (
        analyze, build_dataframe, load_latest_factors,
        run_lasso, run_correlation, run_rolling_ols,
        run_importance, run_regime, run_granger, run_lead_lag,
    )
    from src import collect, chart, report


# ── Mock 데이터 픽스처 ────────────────────────────────────────────────────────

@pytest.fixture
def mock_Xy():
    np.random.seed(42)
    dates = pd.date_range("2000-01", periods=120, freq="MS").strftime("%Y-%m-%d")
    y = pd.Series(np.random.randn(120) * 0.5, index=dates, name="INDPRO")
    X = pd.DataFrame({
        "FEDFUNDS": np.random.randn(120),
        "T10Y2Y":   np.random.randn(120),
        "UNRATE":   np.random.randn(120),
    }, index=dates)
    return X, y


@pytest.fixture
def mock_factors_data(mock_Xy):
    X, y = mock_Xy
    return {
        "target": {
            "series": "INDPRO", "label": "산업생산지수 MoM%",
            "data": [{"date": d, "value": v} for d, v in y.items()],
        },
        "factors": {
            col: {"label": col, "data": [{"date": d, "value": v}
                  for d, v in X[col].items()]}
            for col in X.columns
        },
    }


# ── 단위 테스트 ───────────────────────────────────────────────────────────────

def test_lasso(mock_Xy, mock_factors_data):
    from src.analyze.lasso import run_lasso
    X, y = mock_Xy
    result = run_lasso(X, y, mock_factors_data)
    assert isinstance(result, list)
    if result:
        assert "factor" in result[0] and "coefficient" in result[0]


def test_correlation(mock_Xy, mock_factors_data):
    from src.analyze.correlation import run_correlation
    X, y = mock_Xy
    result = run_correlation(X, y, mock_factors_data)
    assert isinstance(result, list)


def test_regime(mock_Xy):
    from src.analyze.regime import run_regime
    _, y = mock_Xy
    result = run_regime(y)
    assert result["regime"] in ("Expansion", "Neutral", "Contraction", "UNKNOWN")
    assert 0 <= result["confidence"] <= 100


def test_build_dataframe(mock_factors_data):
    from src.analyze.io import build_dataframe
    X, y = build_dataframe(mock_factors_data)
    assert len(X) == len(y)
    assert len(X) > 0


def test_lead_lag(mock_Xy, mock_factors_data):
    from src.analyze.lead_lag import run_lead_lag
    X, y = mock_Xy
    result = run_lead_lag(X, y, mock_factors_data)
    assert len(result) == len(X.columns)
    assert all("is_leading" in r for r in result)
