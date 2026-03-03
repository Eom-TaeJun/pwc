"""이벤트 기반 구조 변화 분석 프레임워크 — yfinance + ruptures Dynp.

사용법:
    from event_study import EventStudy
    es = EventStudy("006400.KS", event_date="2022-05-24",
                    event_label="Samsung SDI + Stellantis JV")
    result = es.run()

알고리즘 선택 근거:
    Dynp(l2) 채택 이유:
    - Pelt(rbf): 주식 수익률(고변동성 ~14% std)에서 스케일 불호환 → 0 breaks 반환
    - Pelt(l2): penalty 민감도 과도 — 조금만 낮춰도 9~11개 분절
    - Dynp(l2): n_bkps를 시계열 길이 기반으로 자동 결정 → 안정적 분절
    n_bkps = max(2, n_obs // 18)  # 18개월당 구조 변화 1개
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import yfinance as yf

try:
    import ruptures as rpt
    _HAS_RUPTURES = True
except ImportError:
    _HAS_RUPTURES = False

MIN_SIZE = 6   # Bry-Boschan 최소 국면 (개월)


def get_monthly_returns(ticker: str, start: str, end: str = None) -> pd.Series:
    """yfinance → 월간 수익률(%) 시계열."""
    data = yf.download(ticker, start=start, end=end, interval="1mo",
                       auto_adjust=True, progress=False)
    if data.empty:
        return pd.Series(dtype=float, name=ticker)
    prices = data["Close"].squeeze()
    if isinstance(prices, pd.DataFrame):
        prices = prices.iloc[:, 0]
    return (prices.pct_change().dropna() * 100).rename(ticker)


def detect_breaks_in_returns(returns: pd.Series) -> list:
    """Dynp(l2)로 월간 수익률 시계열 구조 변화 탐지.

    n_bkps = max(2, n_obs // 18): 18개월당 구조 변화 1개 가정
    예) 86개월 → 4개 break, 24개월 → 2개 break
    """
    if not _HAS_RUPTURES or len(returns) < MIN_SIZE * 2:
        return []
    try:
        n_bkps = max(2, len(returns) // 18)
        algo = rpt.Dynp(model="l2", min_size=MIN_SIZE, jump=1)
        raw = algo.fit(returns.values.reshape(-1, 1)).predict(n_bkps=n_bkps)
        bkps = [b for b in raw if b < len(returns)]
        return [str(returns.index[b - 1])[:7] for b in bkps]
    except Exception:
        return []


def period_stats(returns: pd.Series, start: str, end: str = None) -> dict:
    """기간별 수익률 통계 (평균·표준편차·샤프)."""
    s = returns.loc[start:end] if end else returns.loc[start:]
    if len(s) == 0:
        return {"n": 0}
    mu, sig = s.mean(), s.std()
    return {
        "n": len(s), "start": str(s.index[0])[:7], "end": str(s.index[-1])[:7],
        "mean_mom_pct": round(mu, 3), "std_mom_pct": round(sig, 3),
        "sharpe_monthly": round(mu / sig, 3) if sig > 0 else None,
    }


class EventStudy:
    """단일 종목 이벤트 전후 구조 변화 분석."""

    def __init__(self, ticker: str, event_date: str, event_label: str,
                 before_start: str = "2019-01-01"):
        self.ticker = ticker
        self.event_date = event_date    # YYYY-MM-DD
        self.event_label = event_label
        self.before_start = before_start

    def run(self) -> dict:
        returns = get_monthly_returns(self.ticker, start=self.before_start)
        if returns.empty:
            return {"error": f"{self.ticker} 데이터 없음"}

        evt_ym = self.event_date[:7]   # YYYY-MM
        detected = detect_breaks_in_returns(returns)

        before = period_stats(returns, self.before_start, evt_ym)
        after  = period_stats(returns, evt_ym)

        # 감지된 break가 이벤트 날짜와 얼마나 가까운지 (개월 단위)
        proximity = None
        if detected:
            evt_ts = pd.Timestamp(evt_ym)
            diffs = [abs((pd.Timestamp(d) - evt_ts).days / 30) for d in detected]
            proximity = round(min(diffs), 1)

        return {
            "ticker": self.ticker,
            "event": {"date": self.event_date, "label": self.event_label},
            "data_period": {"start": str(returns.index[0])[:7],
                            "end": str(returns.index[-1])[:7],
                            "n_obs": len(returns)},
            "pelt_breaks": detected,
            "event_proximity_months": proximity,
            "before_event": before,
            "after_event": after,
        }
