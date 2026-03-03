"""Reddit (RDDT) — OpenAI 파트너십 계약 전후 분석.

이벤트 기준 (criteria.md 참조):
  날짜:  2024-05-16 (OpenAI 공식 발표)
  내용:  OpenAI와 AI 학습 데이터 파트너십 (Data API 실시간 접근 + 광고 파트너)
  변화:  광고 기반 커뮤니티 플랫폼 → AI 데이터 인프라 공급자
  참고:  Reddit IPO = 2024-03-21 → 주가는 IPO 이후만 존재
         Google 계약 2024-02-22 → OpenAI 계약 2024-05-16 (3개월 간격)

핵심 발견 가설:
  - 이벤트(2024-05-16) vs 주가 급등(2024-10월말) → 약 5개월 lag
  - Dynp break가 2024-10월 부근에서 탐지되면 가설 지지:
    "시장은 계약 발표(5월)보다 Q3 실적 확인(10월 어닝) 후 구조적 재평가"
  - 삼성전자 케이스와 반대 방향: SDI는 이벤트 후행(선반영), Reddit은 이벤트 선행(후반영)

실행:
    cd /home/tj/projects/pwc
    python company_events/reddit.py
"""
import json, os
from event_study import EventStudy, get_monthly_returns, detect_breaks_in_returns, period_stats

TICKER       = "RDDT"
EVENT_DATE   = "2024-05-16"   # OpenAI 파트너십 공식 발표
EVENT_LABEL  = "Reddit-OpenAI 파트너십 (Data API + 광고) — 커뮤니티→AI 데이터 인프라"
IPO_DATE     = "2024-03-21"   # 주가 데이터 시작점 (NYSE 상장)
PRICE_SURGE  = "2024-10-29"   # 실제 주가 급등 시점 (Q3 어닝 발표일)
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "outputs", "reddit")

# Reddit S-1 공개 분기별 매출 (USD M) — 2021 Q4 ~ 2023 Q4
# 출처: Reddit S-1 Filing (2024-03-12, SEC EDGAR)
REDDIT_QUARTERLY_REVENUE = {
    "2021-Q4": 186.5, "2022-Q1": 186.0, "2022-Q2": 185.9,
    "2022-Q3": 174.2, "2022-Q4": 166.7, "2023-Q1": 170.0,
    "2023-Q2": 188.9, "2023-Q3": 207.2, "2023-Q4": 249.8,
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[Reddit] {TICKER} 이벤트 분석")
    print(f"  이벤트: {EVENT_LABEL}")
    print(f"  기준일: {EVENT_DATE} | IPO: {IPO_DATE} | 주가 급등: {PRICE_SURGE}\n")

    # A. IPO 이후 주가 Dynp 분석
    returns = get_monthly_returns(TICKER, start=IPO_DATE)
    result = {"ticker": TICKER, "event": {"date": EVENT_DATE, "label": EVENT_LABEL},
              "price_surge_date": PRICE_SURGE}

    if returns.empty:
        print("  주가 데이터 없음 — S-1 매출 데이터만 출력")
    else:
        dp = {"start": str(returns.index[0])[:10],
              "end": str(returns.index[-1])[:10], "n_obs": len(returns)}
        breaks = detect_breaks_in_returns(returns)
        print(f"  주가 데이터: {dp['start']} ~ {dp['end']} ({dp['n_obs']}개월, IPO 이후)")
        print(f"  Dynp 감지 break: {breaks or '없음 (데이터 부족 가능)'}")

        # 이벤트(5월) vs break vs 주가 급등(10월) 삼각 비교
        if breaks:
            import pandas as pd
            evt_ts   = pd.Timestamp(EVENT_DATE)
            surge_ts = pd.Timestamp(PRICE_SURGE)
            for b in breaks:
                b_ts = pd.Timestamp(b)
                d_evt   = round(abs((b_ts - evt_ts).days / 30), 1)
                d_surge = round(abs((b_ts - surge_ts).days / 30), 1)
                print(f"    break {b}: 이벤트(5/16)까지 {d_evt}개월, 주가급등(10/29)까지 {d_surge}개월")

        print(f"  이벤트 전 통계 (IPO~이벤트): {period_stats(returns, IPO_DATE, EVENT_DATE)}")
        print(f"  이벤트 후 통계 (이벤트~현재): {period_stats(returns, EVENT_DATE)}")
        result.update({
            "data_period": dp,
            "dynp_breaks_post_ipo": breaks,
            "before_event_stats": period_stats(returns, IPO_DATE, EVENT_DATE),
            "after_event_stats":  period_stats(returns, EVENT_DATE),
        })

    # B. S-1 매출 추이
    rev      = REDDIT_QUARTERLY_REVENUE
    yoy_2023 = round((rev["2023-Q4"] / rev["2022-Q4"] - 1) * 100, 1)
    print(f"\n  [S-1 매출 데이터]")
    print(f"  OpenAI 계약 직전 분기 (2023-Q4): ${rev['2023-Q4']}M")
    print(f"  2023 Q4 YoY 성장률: +{yoy_2023}%")
    result["s1_revenue"] = {"quarterly": rev, "yoy_2023q4_pct": yoy_2023}

    out = os.path.join(OUTPUT_DIR, "analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  저장: {out}")
    print("\n  ※ 데이터 제약: IPO(2024-03-21)가 Google 계약(2024-02-22)보다 늦어")
    print("     주가 기반 Google 계약 전후 비교 불가. OpenAI 계약(2024-05-16) 기준으로 분석.")


if __name__ == "__main__":
    main()
