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


def regime_timeline(y_series, analysis: dict, date_str: str) -> str:
    """INDPRO 시계열 + Expansion/Neutral/Contraction 배경색 타임라인."""
    try:
        from matplotlib.patches import Patch
        font = get_font()
        regime_data = analysis.get("regime", {}).get("regime_series", [])
        if not regime_data:
            return ""

        dates  = [r["date"] for r in regime_data]
        regimes = [r["regime"] for r in regime_data]
        y_vals  = y_series.reindex(dates).values

        colors = {"Expansion": "#d4edda", "Neutral": "#fff3cd", "Contraction": "#f8d7da"}
        fig, ax = plt.subplots(figsize=(13, 5))

        # 배경 색상 (연속 구간 묶어서)
        prev, start = regimes[0], 0
        for i, r in enumerate(regimes + [None]):
            if r != prev:
                ax.axvspan(start, i, alpha=0.45,
                           color=colors.get(prev, "#ffffff"), linewidth=0)
                prev, start = r, i

        ax.plot(range(len(dates)), y_vals, color="black", linewidth=1.2, label="INDPRO MoM%")
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")

        step = max(1, len(dates) // 10)
        ax.set_xticks(range(0, len(dates), step))
        ax.set_xticklabels(dates[::step], rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("MoM%", fontproperties=font)

        reg_label = analysis.get("regime", {}).get("regime", "?")
        conf      = analysis.get("regime", {}).get("confidence", 0)
        ax.set_title(f"산업생산 레짐 타임라인 — 현재: {reg_label} (신뢰도 {conf}%)", fontproperties=font)

        legend_els = [Patch(facecolor=colors[r], alpha=0.5, label=r)
                      for r in ["Expansion", "Neutral", "Contraction"]]
        ax.legend(handles=legend_els + ax.get_lines()[:1], prop=font)

        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"regime_timeline_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: regime_timeline failed: {e}")
        return ""


def signal_chart(X_df, y_series, analysis: dict, date_str: str) -> str:
    """The Signal: Top Granger Factor (시프트) vs INDPRO 시계열 비교."""
    try:
        font = get_font()
        granger   = analysis.get("granger", [])
        lead_lag  = analysis.get("lead_lag", [])

        # 선행 + Granger significant Factor 선택
        ll_map = {r["factor"]: r for r in lead_lag}
        top_factor = top_label = None
        top_lag = 3
        for g in granger:
            if g.get("strength") in ("STRONG", "MODERATE"):
                ll = ll_map.get(g["factor"], {})
                if ll.get("is_leading") or g["optimal_lag"] > 0:
                    top_factor = g["factor"]
                    top_lag    = g["optimal_lag"]
                    top_label  = g["label"]
                    break

        if top_factor is None:
            leading = [r for r in lead_lag if r.get("is_leading")]
            if not leading or leading[0]["factor"] not in X_df.columns:
                print("Warning: signal_chart - no leading factor found")
                return ""
            top_factor = leading[0]["factor"]
            top_lag    = leading[0]["optimal_lag"]
            top_label  = leading[0]["label"]

        df = pd.DataFrame({
            "factor": X_df[top_factor].shift(top_lag),
            "target": y_series,
        }).dropna()
        if len(df) < 24:
            return ""

        xs = range(len(df))
        date_labels = df.index.tolist()
        step = max(1, len(date_labels) // 10)

        fig, ax1 = plt.subplots(figsize=(13, 5))
        ax2 = ax1.twinx()

        bar_colors = ["#dc3545" if v < 0 else "#198754" for v in df["target"]]
        ax1.bar(xs, df["target"], color=bar_colors, alpha=0.55, label="INDPRO MoM%")
        ax1.axhline(0, color="gray", linewidth=0.5)
        ax1.set_ylabel("INDPRO MoM%", fontproperties=font)
        ax1.set_xticks(list(xs)[::step])
        ax1.set_xticklabels(date_labels[::step], rotation=45, ha="right", fontsize=8)

        ax2.plot(xs, df["factor"], color="navy", linewidth=1.8,
                 label=f"{top_label} (+{top_lag}m 선행)")
        ax2.set_ylabel(top_label, fontproperties=font, color="navy")
        ax2.tick_params(axis="y", labelcolor="navy")

        ax1.set_title(f"The Signal: {top_label} (+{top_lag}개월) → INDPRO", fontproperties=font)
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, prop=font, loc="upper left")

        plt.tight_layout()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"signal_chart_{date_str}.png")
        plt.savefig(path, dpi=150)
        plt.close()
        return path
    except Exception as e:
        print(f"Warning: signal_chart failed: {e}")
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
    has_X = X_df is not None
    has_y = y_series is not None
    return {
        "regime_timeline":    regime_timeline(y_series, analysis, date_str) if has_y else "",
        "signal_chart":       signal_chart(X_df, y_series, analysis, date_str) if has_X and has_y else "",
        "importance_bar":     importance_bar(analysis, date_str),
        "rolling_coef":       rolling_coef(analysis, date_str),
        "correlation_heatmap": correlation_heatmap(X_df, analysis, date_str) if has_X else "",
        "lasso_path":         lasso_path_chart(X_df, y_series, analysis, date_str) if has_X and has_y else "",
    }


if __name__ == "__main__":
    result = generate_all()
    print(result)
