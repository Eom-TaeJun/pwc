"""Reddit (RDDT) — Google AI 데이터 라이선싱 계약 전후 분석.

이벤트 기준 (criteria.md 참조):
  날짜:  2024-02-22 (Reuters/Fortune 확정 보도)
  내용:  Google과 AI 학습 데이터 라이선싱 계약 ($60M/년)
  변화:  광고 기반 커뮤니티 플랫폼 → AI 데이터 공급자
  참고:  Reddit IPO = 2024-03-21 → 주가는 IPO 이후만 존재

전략:
  - IPO 이후 주가(RDDT)로 PELT 구조 변화 탐지
  - 감지된 break 날짜가 알려진 이벤트(분기 어닝, AI 계약 이슈 등)와 얼마나 가까운지 검증
  - 이벤트 전(pre-IPO) 비교는 공개 분기별 매출 데이터를 별도 활용 (S-1 기반)

실행:
    cd /home/tj/projects/pwc
    python company_events/reddit.py
"""
import json, os
from event_study import EventStudy, get_monthly_returns, detect_breaks_in_returns, period_stats

TICKER       = "RDDT"
EVENT_DATE   = "2024-02-22"   # Google 계약 확정 보도
EVENT_LABEL  = "Reddit-Google AI 데이터 라이선싱 ($60M/년) — 커뮤니티→AI 데이터 공급자"
IPO_DATE     = "2024-03-21"   # 주가 데이터 시작점
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
    print(f"  기준일: {EVENT_DATE} | IPO: {IPO_DATE}\n")

    # A. IPO 이후 주가 PELT 분석
    returns = get_monthly_returns(TICKER, start=IPO_DATE)
    result = {"ticker": TICKER, "event": {"date": EVENT_DATE, "label": EVENT_LABEL}}

    if returns.empty:
        print("  주가 데이터 없음 — S-1 매출 데이터만 출력")
    else:
        dp = {"start": str(returns.index[0])[:7],
              "end": str(returns.index[-1])[:7], "n_obs": len(returns)}
        breaks = detect_breaks_in_returns(returns)
        print(f"  주가 데이터: {dp['start']} ~ {dp['end']} ({dp['n_obs']}개월, IPO 이후)")
        print(f"  PELT 감지 break: {breaks or '없음 (데이터 부족 가능)'}")
        print(f"  전체 기간 통계: {period_stats(returns, IPO_DATE)}")
        result.update({"data_period": dp, "pelt_breaks_post_ipo": breaks,
                       "post_ipo_stats": period_stats(returns, IPO_DATE)})

    # B. S-1 매출 추이 (이벤트 전/후 성장률)
    rev = REDDIT_QUARTERLY_REVENUE
    pre_revs  = {k: v for k, v in rev.items() if k < "2024-Q1"}
    post_revs = {k: v for k, v in rev.items() if k >= "2024-Q1"}
    pre_vals  = list(pre_revs.values())
    yoy_2023  = round((rev["2023-Q4"] / rev["2022-Q4"] - 1) * 100, 1)
    print(f"\n  [S-1 매출 데이터]")
    print(f"  Google 계약 전 마지막 분기 (2023-Q4): ${rev['2023-Q4']}M")
    print(f"  2023 Q4 YoY 성장률: +{yoy_2023}%")
    result["s1_revenue"] = {"quarterly": rev, "yoy_2023q4_pct": yoy_2023}

    out = os.path.join(OUTPUT_DIR, "analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  저장: {out}")
    print("\n  ※ 데이터 제약: Reddit IPO(2024-03)가 Google 계약(2024-02)보다 늦어")
    print("     주가 기반 이벤트 전/후 비교 불가. S-1 매출 데이터로 방향성만 검토.")


if __name__ == "__main__":
    main()
