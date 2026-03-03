"""
목적: Factor Pool 분석 차트 생성 (4종)
입력: outputs/context/analysis_YYYYMMDD.json
출력: outputs/charts/*.png
제외: 인터랙티브 차트, 웹 대시보드
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from sklearn.linear_model import lasso_path
import json, os, glob
import numpy as np
import pandas as pd
from datetime import datetime

OUTPUT_DIR = "outputs/charts"


def get_font():
    """Return NanumGothic FontProperties, fallback to DejaVu Sans."""
    for name in fm.findSystemFonts(fontpaths=None, fontext="ttf"):
        if "NanumGothic" in name:
            return fm.FontProperties(fname=name)
    return fm.FontProperties(family="DejaVu Sans")


def correlation_heatmap(X_df, analysis: dict, date_str: str) -> str:
    """Plot factor-target correlation heatmap and save PNG."""
    try:
        font = get_font()
        fig, ax = plt.subplots(figsize=(10, 6))
        corr_mat = X_df.corr()
        im = ax.imshow(corr_mat, cmap="RdBu_r", vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(len(corr_mat.columns)))
        ax.set_yticks(range(len(corr_mat.columns)))
        ax.set_xticklabels(corr_mat.columns, rotation=45, ha="right", fontproperties=font)
        ax.set_yticklabels(corr_mat.columns, fontproperties=font)
        for i in range(len(corr_mat)):
            for j in range(len(corr_mat.columns)):
                ax.text(j, i, f"{corr_mat.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
        ax.set_title("Factor-Target 상관관계 히트맵", fontproperties=font)
        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"correlation_heatmap_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: correlation_heatmap failed: {e}")
        return ""


def lasso_path_chart(X_df, y_series, analysis: dict, date_str: str) -> str:
    """Plot LASSO regularization path for top 5 selected factors."""
    try:
        font = get_font()
        selected = [r["factor"] for r in analysis.get("lasso_selected", [])[:5]]
        cols = [c for c in selected if c in X_df.columns] or list(X_df.columns[:5])
        X = X_df[cols].values
        y = y_series.values
        alphas, coefs, _ = lasso_path(X, y, eps=1e-3)
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, col in enumerate(cols):
            ax.plot(np.log10(alphas), coefs[i], label=col)
        ax.set_xlabel("log(alpha)", fontproperties=font)
        ax.set_ylabel("Coefficient", fontproperties=font)
        ax.set_title("LASSO 정규화 경로", fontproperties=font)
        ax.legend(prop=font)
        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"lasso_path_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: lasso_path failed: {e}")
        return ""


def importance_bar(analysis: dict, date_str: str) -> str:
    """Horizontal bar chart of RF feature importance (top 10)."""
    try:
        font = get_font()
        items = sorted(analysis.get("importance", []), key=lambda r: r["importance"])[-10:]
        labels = [r["factor"] for r in items]
        values = [r["importance"] for r in items]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(labels, values, color="steelblue")
        ax.set_xlabel("Importance", fontproperties=font)
        ax.set_title("ML Feature Importance (Random Forest)", fontproperties=font)
        ax.set_yticklabels(labels, fontproperties=font)
        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"importance_bar_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: importance_bar failed: {e}")
        return ""


def rolling_coef(analysis: dict, date_str: str) -> str:
    """Line chart of rolling OLS coefficients for top 3 stable factors."""
    try:
        font = get_font()
        stable = analysis.get("rolling_stability", {}).get("stable_factors", [])[:3]
        coef_data = analysis.get("rolling_stability", {}).get("rolling_coefs", {})
        if not stable:
            print("Warning: no stable factors for rolling_coef chart")
            return ""
        fig, ax = plt.subplots(figsize=(10, 6))
        for fac in stable:
            if fac not in coef_data:
                continue
            records = coef_data[fac]
            dates = [r["date"] for r in records]
            coefs = np.array([r["coef"] for r in records])
            std = coefs.std()
            ax.plot(dates, coefs, label=fac)
            ax.fill_between(dates, coefs - std, coefs + std, alpha=0.2)
        step = max(1, len(dates) // 8)
        ax.set_xticks(dates[::step])
        ax.set_xticklabels(dates[::step], rotation=45, ha="right", fontproperties=font)
        ax.set_ylabel("Coefficient", fontproperties=font)
        ax.set_title("Rolling OLS 계수 안정성 (36개월 창)", fontproperties=font)
        ax.legend(prop=font)
        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"rolling_coef_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: rolling_coef failed: {e}")
        return ""


def generate_all(analysis: dict = None, X_df=None, y_series=None) -> dict:
    """Generate all 4 charts; load analysis from latest JSON if None."""
    if analysis is None:
        files = sorted(glob.glob("outputs/context/analysis_*.json"))
        if not files:
            raise FileNotFoundError("No analysis files found")
        with open(files[-1]) as f:
            analysis = json.load(f)

    date_str = datetime.now().strftime("%Y%m%d")
    return {
        "correlation_heatmap": correlation_heatmap(X_df, analysis, date_str) if X_df is not None else "",
        "lasso_path": lasso_path_chart(X_df, y_series, analysis, date_str) if X_df is not None else "",
        "importance_bar": importance_bar(analysis, date_str),
        "rolling_coef": rolling_coef(analysis, date_str),
    }


if __name__ == "__main__":
    result = generate_all()
    print(result)
