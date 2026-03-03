"""Samsung Electronics (005930.KS) — Tesla 2나노 파운드리 계약 전후 분석.

이벤트 기준 (criteria.md 참조):
  날짜:  2025-07-28 (이재용-머스크 계약 확정 공식 보도)
  내용:  Tesla AI6 칩 2나노 파운드리 위탁생산 (22.8조원, 2025~2033)
  변화:  메모리 반도체 중심 → AI 파운드리 전략 거점 (비메모리 피벗)
  공장:  텍사스 테일러 공장 (2나노 공정)

실행:
    cd /home/tj/projects/pwc
    python company_events/samsung_electronics.py
"""
import json, os
from event_study import EventStudy

TICKER       = "005930.KS"
EVENT_DATE   = "2025-07-28"
EVENT_LABEL  = "삼성전자 + Tesla 2나노 파운드리 계약 (22.8조원, AI6 칩, 테일러 공장)"
BEFORE_START = "2020-01-01"
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "outputs", "samsung_electronics")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[Samsung Electronics] {TICKER} 이벤트 분석 시작")
    print(f"  이벤트: {EVENT_LABEL}")
    print(f"  기준일: {EVENT_DATE}\n")

    es = EventStudy(TICKER, EVENT_DATE, EVENT_LABEL, BEFORE_START)
    result = es.run()

    if "error" in result:
        print(f"  오류: {result['error']}")
        return

    dp = result["data_period"]
    print(f"  데이터: {dp['start']} ~ {dp['end']} ({dp['n_obs']}개월)")
    print(f"  Dynp 감지 break: {result['pelt_breaks'] or '없음'}")
    if result["event_proximity_months"] is not None:
        print(f"  이벤트 날짜와 가장 가까운 break: {result['event_proximity_months']:.1f}개월 차이")

    print("\n  [이벤트 전 — 메모리 반도체 사이클]")
    _print_stats(result["before_event"])
    print("\n  [이벤트 후 — AI 파운드리 피벗 초기]")
    _print_stats(result["after_event"])
    print("\n  ※ 데이터 제약: After 기간(~8개월) 짧아 통계적 유의성 낮음 — 방향성 참고용")

    out = os.path.join(OUTPUT_DIR, "analysis.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  저장: {out}")


def _print_stats(s: dict):
    if s.get("n", 0) == 0:
        print("    데이터 없음")
        return
    print(f"    기간: {s['start']} ~ {s['end']} ({s['n']}개월)")
    print(f"    평균 수익률: {s['mean_mom_pct']:+.2f}% / 월")
    print(f"    변동성(std): {s['std_mom_pct']:.2f}% / 월")
    print(f"    월간 Sharpe: {s['sharpe_monthly']}")


if __name__ == "__main__":
    main()
