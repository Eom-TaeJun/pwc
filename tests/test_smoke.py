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
    assert isinstance(result, dict)
    assert "selected" in result and "alpha" in result
    assert isinstance(result["selected"], list)
    assert isinstance(result["alpha"], float)
    if result["selected"]:
        assert "factor" in result["selected"][0] and "coefficient" in result["selected"][0]


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


def test_build_factor_report(tmp_path, mock_factors_data):
    """build_factor_report가 mock 분석 데이터로 MD 파일을 생성하는지 확인."""
    from src.report import build_factor_report
    import src.report as rep_module

    mock_analysis = {
        "data_period": {"start": "2000-01", "end": "2010-01", "n_obs": 120},
        "regime": {"regime": "Neutral", "confidence": 60, "probs": {"Neutral": 0.6}, "entropy": 0.7},
        "lasso_selected": [{"factor": "T10Y2Y", "label": "Yield Spread", "coefficient": 0.3}],
        "correlation": [{"factor": "T10Y2Y", "label": "Yield Spread", "corr": 0.5, "pvalue": 0.01, "lag_months": 3}],
        "granger": [{"factor": "T10Y2Y", "label": "Yield Spread", "strength": "STRONG", "optimal_lag": 3, "p_value": 0.005, "f_statistic": 8.2}],
        "lead_lag": [{"factor": "T10Y2Y", "label": "Yield Spread", "optimal_lag": 3, "max_corr": 0.5, "zero_corr": 0.3, "is_leading": True}],
        "importance": [{"rank": 1, "factor": "T10Y2Y", "label": "Yield Spread", "importance": 0.45}],
        "rolling_stability": {"stable_factors": ["T10Y2Y"], "unstable_factors": [], "_params": {"window": 36, "threshold": 0.5}},
        "consulting_implications": {"current_regime": "중립 국면", "leading_indicators": "T10Y2Y", "data_constraints": "없음", "client_narrative": "테스트"},
    }

    orig_dir = rep_module.OUTPUT_DIR
    rep_module.OUTPUT_DIR = str(tmp_path)
    try:
        path = build_factor_report(mock_factors_data, mock_analysis)
        assert path.endswith(".md")
        content = open(path, encoding="utf-8").read()
        assert "지금 어디에 있는가" in content
        assert "무엇이 먼저 움직이는가" in content
        assert "부록 A" in content
    finally:
        rep_module.OUTPUT_DIR = orig_dir
