"""
Causal Impact Analysis — 레짐 조건부 초과수익률 + 단기 유의성 판단
v2: 섹터 피어 벤치마크 + 이벤트 유형별 창 + 효과 타이밍 분류

이벤트:
  1. Samsung Electronics — Tesla 2nm 파운드리 계약 (2025-07-28, Expansion)
     벤치마크: SK Hynix (000660.KS) — 동일 섹터 피어, 동일 통화(KRW)
     창: 이전 6개월 / 이후 6개월 — 전략적 계약은 중장기 재평가가 본질

  2. Reddit (RDDT) — Q3 어닝 발표 (2024-10-29, Neutral)
     벤치마크: S&P500 (^GSPC)
     창: 이전 6개월 / 이후 30거래일 — 어닝 서프라이즈는 즉각 반영

단기 유의성 판단:
  hit_rate = Post 기간 중 효과 95% CI 하한 > 0인 날의 비율
  front_load_ratio = 초기 20일 평균 효과 / 전체 평균 효과
  → 즉각 반응(Event-Driven) / 지속 효과(Sustained) / 지연 효과(Strategic) 분류

사용: python scripts/causal_impact_analysis.py
"""
import io
import json
import sys
import contextlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.family"] = "NanumGothic"
matplotlib.rcParams["axes.unicode_minus"] = False

import numpy as np
import pandas as pd

# pandas 2.x 호환 패치
import pandas.core.dtypes.common as _dtypes
if not hasattr(_dtypes, "is_datetime_or_timedelta_dtype"):
    _dtypes.is_datetime_or_timedelta_dtype = pd.api.types.is_datetime64_any_dtype

try:
    import yfinance as yf
    from causalimpact import CausalImpact
except ImportError as e:
    print(f"ERROR: {e}\npip install yfinance causalimpact")
    sys.exit(1)

OUTPUT_DIR = Path("outputs/causal_impact")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_SAMSUNG_BASE = dict(
    ticker="005930.KS",
    benchmark="000660.KS",
    benchmark_name="SK Hynix (반도체 섹터 피어)",
    benchmark_note="KOSPI 전체 시장 대신 동일 섹터 피어를 사용. "
                   "반도체 업황(HBM 이슈 등) 공통 요인을 통제해 Samsung 특유의 계약 효과를 분리한다.",
    event_date="2025-07-28",
    pre_start="2025-01-27",
    post_end="2026-01-28",
    regime="Expansion",
)

EVENTS = [
    {
        **_SAMSUNG_BASE,
        "name":              "Samsung_Tesla2nm_Long",
        "label":             "Samsung — Tesla 2nm 계약 (전략적 효과, 6개월)",
        "post_trading_days": None,   # 전체 6개월
        "hypothesis":        "반도체 섹터 피어 대비 계약이 중장기 포지셔닝 변화를 만들었는가?",
        "window_type":       "long",
    },
    {
        **_SAMSUNG_BASE,
        "name":              "Samsung_Tesla2nm_Short",
        "label":             "Samsung — Tesla 2nm 계약 (즉각 반응, 20거래일)",
        "post_trading_days": 20,     # 공시 직후 20거래일만
        "hypothesis":        "계약 발표에 시장이 반도체 섹터 대비 즉각적으로 반응했는가?",
        "window_type":       "short",
    },
    {
        "name":              "Reddit_Q3Earnings",
        "label":             "Reddit (RDDT) — Q3 어닝 발표 (30거래일)",
        "ticker":            "RDDT",
        "benchmark":         "^GSPC",
        "benchmark_name":    "S&P500",
        "benchmark_note":    "어닝 이벤트는 전체 시장 대비 초과 반응이 표준 기준. S&P500으로 시장 전체 상승분을 통제한다.",
        "event_date":        "2024-10-29",
        "pre_start":         "2024-04-29",
        "post_end":          "2025-04-29",
        "post_trading_days": 30,
        "regime":            "Neutral",
        "hypothesis":        "거시 Neutral 레짐에서 어닝 서프라이즈가 S&P500 대비 유의한 단기 초과 상승을 만들었는가?",
        "window_type":       "short",
    },
]


def _get_close(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.DatetimeIndex(close.index).tz_localize(None)
    return close.dropna().rename(ticker)


def classify_effect_timing(post_inf: pd.DataFrame) -> dict:
    """
    단기 유의성 판단 — 효과 타이밍 분류

    지표:
      hit_rate    : 효과 95% CI 하한 > 0인 날의 비율 (양방향 효과 고려)
      front_load  : 초기 N일 평균 효과 / 전체 평균 효과 비율
                    > 1.3 → 이벤트 발표에 즉각 반응
                    0.7~1.3 → 지속적 효과
                    < 0.7 → 효과가 뒤에 누적 (전략적)

    분류:
      즉각 반응 (Event-Driven) : short_hit ≥ 0.5 AND front_load ≥ 1.3
      지연 효과 (Strategic)    : full_hit ≥ 0.4 AND front_load ≤ 0.7
      지속 효과 (Sustained)    : full_hit ≥ 0.4 AND 0.7 < front_load < 1.3
      효과 불명확              : full_hit < 0.4
    """
    n_short = min(20, max(5, len(post_inf) // 4))
    direction = 1 if post_inf["point_effect"].mean() >= 0 else -1

    if direction > 0:
        short_hit = float((post_inf.iloc[:n_short]["point_effect_lower"] > 0).mean())
        full_hit  = float((post_inf["point_effect_lower"] > 0).mean())
    else:
        short_hit = float((post_inf.iloc[:n_short]["point_effect_upper"] < 0).mean())
        full_hit  = float((post_inf["point_effect_upper"] < 0).mean())

    short_avg = float(post_inf.iloc[:n_short]["point_effect"].mean())
    full_avg  = float(post_inf["point_effect"].mean())
    front_load = (short_avg / full_avg) if abs(full_avg) > 1e-8 else 1.0

    if short_hit >= 0.5 and front_load >= 1.3:
        label = "즉각 반응 (Event-Driven)"
        desc  = f"이벤트 후 {n_short}일 내 효과 집중 — 공시 정보가 신속히 반영됨"
    elif full_hit >= 0.4 and front_load <= 0.7:
        label = "지연 효과 (Strategic)"
        desc  = f"효과가 시간 경과 후 누적 — 전략적 이벤트 특성, 시장 재평가에 시간 소요"
    elif full_hit >= 0.4:
        label = "지속 효과 (Sustained)"
        desc  = f"Post 기간 전반에 걸쳐 일관된 초과 효과 유지"
    else:
        label = "효과 불명확"
        desc  = f"신뢰구간 내 변동 우세 — 벤치마크 대비 유의한 차별화 없음"

    return {
        "timing_label": label,
        "timing_desc": desc,
        "short_hit_rate": round(short_hit, 3),
        "full_hit_rate": round(full_hit, 3),
        "front_load_ratio": round(front_load, 2),
        "n_short_days": n_short,
    }


def _parse_relative_effect(summary_text: str):
    avg_rel, cum_rel = 0.0, 0.0
    for line in summary_text.splitlines():
        s = line.strip()
        if s.startswith("Relative Effect") and "CI" not in s:
            parts = s.split()
            try:
                avg_rel = float(parts[-2].replace("%", ""))
                cum_rel = float(parts[-1].replace("%", ""))
            except (ValueError, IndexError):
                pass
            break
    return avg_rel, cum_rel


def _parse_pvalue(summary_text: str) -> float:
    for line in summary_text.splitlines():
        if line.strip().startswith("P-value"):
            try:
                return float(line.split()[-1].replace("%", "")) / 100
            except (ValueError, IndexError):
                pass
    return 0.5


def run_causal_impact(event: dict) -> dict:
    print(f"\n{'='*60}")
    print(f"[{event['regime']}] {event['label']}")
    print(f"  벤치마크: {event['benchmark_name']}")
    print(f"  {event['benchmark_note']}")

    stock = _get_close(event["ticker"],    event["pre_start"], event["post_end"])
    bench = _get_close(event["benchmark"], event["pre_start"], event["post_end"])

    common = stock.index.intersection(bench.index)
    df = pd.DataFrame({"y": np.log(stock[common]), "x": np.log(bench[common])})

    event_dt   = pd.Timestamp(event["event_date"])
    pre_idx    = df.index[df.index < event_dt]
    post_idx   = df.index[df.index >= event_dt]

    if len(pre_idx) < 30:
        raise ValueError(f"Pre 기간 부족: {len(pre_idx)}일")

    # post_trading_days 지정 시 post 기간 단축
    n_post = event.get("post_trading_days")
    if n_post:
        post_idx = post_idx[:n_post]

    pre_period  = [df.index[0],   pre_idx[-1]]
    post_period = [post_idx[0],   post_idx[-1]]

    print(f"  Pre:  {pre_period[0].date()} ~ {pre_period[1].date()} ({len(pre_idx)}거래일)")
    print(f"  Post: {post_period[0].date()} ~ {post_period[1].date()} ({len(post_idx)}거래일)")

    # CausalImpact 실행 (post 기간 한정 데이터만 전달)
    df_ci = df.loc[:post_period[1]]
    ci = CausalImpact(df_ci, pre_period, post_period)
    ci.run()

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ci.summary()
    summary_text = buf.getvalue()

    p_value         = _parse_pvalue(summary_text)
    avg_rel, cum_rel = _parse_relative_effect(summary_text)

    post_inf = ci.inferences.loc[post_period[0]:post_period[1]]
    timing   = classify_effect_timing(post_inf)

    print(f"\n  벤치마크 대비 상대 효과: {avg_rel:+.1f}% (Post 전체 평균)")
    print(f"  p-value: {p_value:.4f} → {'✓ 유의 (p<0.05)' if p_value < 0.05 else '✗ 비유의'}")
    print(f"\n  단기 유의성 판단:")
    print(f"    분류:           {timing['timing_label']}")
    print(f"    설명:           {timing['timing_desc']}")
    print(f"    단기 hit rate:  {timing['short_hit_rate']:.0%} ({timing['n_short_days']}일 기준)")
    print(f"    전체 hit rate:  {timing['full_hit_rate']:.0%}")
    print(f"    front-load 비:  {timing['front_load_ratio']:.2f}x")

    # 차트 저장
    fig = ci.plot(figsize=(12, 8))
    chart_path = OUTPUT_DIR / f"causal_impact_{event['name']}.png"
    plt.suptitle(
        f"[{event['regime']}] {event['label']}\n"
        f"벤치마크: {event['benchmark_name']} | "
        f"p={p_value:.3f} | 상대 효과 {avg_rel:+.1f}% | {timing['timing_label']}",
        fontsize=9, y=1.01,
    )
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  차트 저장: {chart_path}")

    return {
        "name":           event["name"],
        "label":          event["label"],
        "regime":         event["regime"],
        "benchmark":      event["benchmark_name"],
        "hypothesis":     event["hypothesis"],
        "event_date":     event["event_date"],
        "pre_period":     [str(pre_period[0].date()),  str(pre_period[1].date())],
        "post_period":    [str(post_period[0].date()), str(post_period[1].date())],
        "avg_rel_pct":    round(avg_rel, 2),
        "cum_rel_pct":    round(cum_rel, 2),
        "p_value":        round(p_value, 4),
        "significant":    p_value < 0.05,
        "timing":         timing,
        "summary":        summary_text,
        "chart":          str(chart_path),
    }


def main():
    results = []
    for event in EVENTS:
        try:
            results.append(run_causal_impact(event))
        except Exception as e:
            import traceback
            print(f"\nERROR [{event['name']}]: {e}")
            traceback.print_exc()

    out_json = OUTPUT_DIR / "causal_impact_results.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nJSON 저장: {out_json}")

    print("\n" + "=" * 80)
    print("최종 비교 — 레짐 조건부 초과수익률 + 효과 타이밍")
    print("=" * 80)
    fmt = "{:<35} {:<10} {:>8} {:>8}  {:<24}"
    print(fmt.format("분석", "레짐", "상대효과", "p-value", "타이밍"))
    print("-" * 80)
    for r in results:
        sig = "✓" if r["significant"] else "✗"
        t   = r["timing"]
        print(fmt.format(
            r["label"][:33], r["regime"],
            f"{r['avg_rel_pct']:+.1f}%",
            f"{r['p_value']:.3f}{sig}",
            t["timing_label"],
        ))
        print(f"   └ hit rate: 단기 {t['short_hit_rate']:.0%} / 전체 {t['full_hit_rate']:.0%}"
              f" | front-load: {t['front_load_ratio']:.2f}x")

    # Samsung 장단기 비교 요약
    long_r  = next((r for r in results if r.get("name") == "Samsung_Tesla2nm_Long"),  None)
    short_r = next((r for r in results if r.get("name") == "Samsung_Tesla2nm_Short"), None)
    if long_r and short_r:
        print("\n[Samsung 단기 vs 장기 비교]")
        print(f"  즉각 반응 (20일): {short_r['avg_rel_pct']:+.1f}% | {short_r['timing']['timing_label']}")
        print(f"  전략적 효과 (6M): {long_r['avg_rel_pct']:+.1f}% | {long_r['timing']['timing_label']}")
        if short_r["avg_rel_pct"] > 0 and long_r["avg_rel_pct"] > 0:
            print("  → 즉각 반응 후 중장기 효과도 유지 (이벤트 + 전략 복합)")
        elif short_r["avg_rel_pct"] > long_r["avg_rel_pct"] > 0:
            print("  → 초기 반응이 크고 이후 수렴 (공시 반응형)")
        elif long_r["avg_rel_pct"] > short_r["avg_rel_pct"]:
            print("  → 초기 반응 약하고 장기 효과 누적 (전략적 재평가형)")


if __name__ == "__main__":
    main()
