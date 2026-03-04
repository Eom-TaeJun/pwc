"""Company Event × 매크로 레짐 오버레이 차트 — 2-panel.

Reddit(RDDT)      : 이벤트 선행 / break 후행 패턴 (매크로 비연동)
Samsung(005930.KS): 이벤트 ≈ break, Expansion 국면 (매크로 연동)

출력: outputs/charts/company_regime_overlay_YYYYMMDD.png
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import pandas as pd
from company_events.event_study import get_monthly_returns

OUTPUT_DIR = "outputs/charts"
REGIME_COLORS = {
    "Expansion": "#d4edda",
    "Neutral":   "#fff3cd",
    "Contraction": "#f8d7da",
}
CASES = [
    {
        "ticker": "RDDT", "label": "Reddit (RDDT)",
        "start": "2024-03-21", "event_date": "2024-05-16",
        "event_label": "OpenAI 계약", "surge_date": "2024-10-29",
        "breaks": ["2025-01", "2025-09"],
        "note": "모든 break → Neutral 국면\n매크로 비연동: AI 데이터 수익화는\n경기 사이클을 초월한 구조 변화",
    },
    {
        "ticker": "005930.KS", "label": "Samsung Electronics (005930.KS)",
        "start": "2020-01-01", "event_date": "2025-07-28",
        "event_label": "Tesla 2nm 계약", "surge_date": None,
        "breaks": ["2021-01", "2024-07", "2025-01", "2025-08"],
        "note": "Tesla 계약 → Expansion 국면 (2025-07)\n매크로 연동: AI 제조 수요 확장과\n파운드리 피벗 타이밍 정합",
    },
]


def _load_regime() -> pd.Series:
    files = sorted(glob.glob("outputs/context/analysis_*.json"))
    if not files:
        return pd.Series(dtype=str)
    with open(files[-1]) as f:
        rows = json.load(f).get("regime", {}).get("regime_series", [])
    return pd.Series({pd.Timestamp(r["date"]): r["regime"] for r in rows})


def _get_font():
    for name in fm.findSystemFonts(fontpaths=None, fontext="ttf"):
        if "NanumGothic" in name:
            return fm.FontProperties(fname=name)
    return fm.FontProperties(family="DejaVu Sans")


def _draw_bg(ax, returns: pd.Series, regime: pd.Series):
    """정수 x축 기준으로 GMM 레짐 배경 구간 칠하기."""
    seg_r, seg_start = None, 0
    for i, dt in enumerate(returns.index):
        r = regime.get(dt)
        if r != seg_r:
            if seg_r is not None:
                ax.axvspan(seg_start, i, alpha=0.45,
                           color=REGIME_COLORS.get(seg_r, "white"), linewidth=0)
            seg_r, seg_start = r, i
    if seg_r is not None:
        ax.axvspan(seg_start, len(returns), alpha=0.45,
                   color=REGIME_COLORS.get(seg_r, "white"), linewidth=0)


def _idx(returns: pd.Series, date_str: str) -> int:
    ts = pd.Timestamp(date_str)
    diffs = [(abs((dt - ts).days), i) for i, dt in enumerate(returns.index)]
    return min(diffs)[1]


def draw(date_str: str = None) -> str:
    from datetime import datetime
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    regime = _load_regime()
    font = _get_font()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(
        "Company Event × 매크로 레짐 연동 분석\n"
        "(GMM 배경: Expansion=녹 / Neutral=황 / Contraction=적)",
        fontproperties=font, fontsize=13,
    )

    for ax, case in zip(axes, CASES):
        ret = get_monthly_returns(case["ticker"], start=case["start"])
        if ret.empty:
            ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center",
                    transform=ax.transAxes)
            continue
        ret.index = pd.to_datetime(ret.index).to_period("M").to_timestamp()

        _draw_bg(ax, ret, regime)
        xs = range(len(ret))
        ax.plot(xs, ret.values, color="black", linewidth=1.5, label="월간 수익률(%)")
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")

        ax.axvline(_idx(ret, case["event_date"]), color="red",
                   linewidth=1.8, label=case["event_label"])
        if case.get("surge_date"):
            ax.axvline(_idx(ret, case["surge_date"]), color="blue",
                       linewidth=1.5, linestyle="--", label="주가 급등")
        for b in case["breaks"]:
            ax.axvline(_idx(ret, b), color="purple",
                       linewidth=1.0, linestyle=":", label=f"break {b}")

        step = max(1, len(ret) // 8)
        ax.set_xticks(list(xs)[::step])
        ax.set_xticklabels(
            [str(ret.index[i])[:7] for i in range(0, len(ret), step)],
            rotation=45, ha="right", fontsize=8,
        )
        ax.set_title(case["label"], fontproperties=font, fontsize=11)
        ax.set_ylabel("MoM 수익률 (%)", fontproperties=font)
        ax.legend(prop=font, fontsize=7, loc="upper left")
        ax.text(0.02, 0.02, case["note"], transform=ax.transAxes,
                fontsize=8, color="navy", va="bottom", style="italic",
                fontproperties=font)

    patches = [mpatches.Patch(facecolor=REGIME_COLORS[r], alpha=0.5, label=r)
               for r in ["Expansion", "Neutral", "Contraction"]]
    fig.legend(handles=patches, loc="lower center", ncol=3, prop=font,
               bbox_to_anchor=(0.5, -0.01))
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"company_regime_overlay_{date_str}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


if __name__ == "__main__":
    p = draw()
    print(f"저장: {p}")
