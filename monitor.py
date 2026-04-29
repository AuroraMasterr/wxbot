from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional, Union


class Monitor:
    def __init__(
        self,
        job: Callable[[], None],
        interval: Optional[Union[int, float, timedelta]] = None,
        start_at: Optional[Union[str, datetime]] = None,
        check_interval_seconds: float = 1.0,
    ):
        self.job = job
        # 默认至少10分钟检查一次，避免频繁检查导致资源浪费
        self.check_interval_seconds = max(600, check_interval_seconds)

        self.interval_seconds = self._parse_interval_seconds(interval)
        self.next_run = self._parse_start_time(start_at)

        print(f"[Monitor] initialized with interval={self.interval_seconds} seconds, start_at={self.next_run}")

    @staticmethod
    def _parse_interval_seconds(interval: Optional[Union[int, float, timedelta]]) -> float:
        if isinstance(interval, timedelta):
            return interval.total_seconds()
        return float(interval)

    @staticmethod
    def _parse_start_time(start_at: Optional[Union[str, datetime]]) -> datetime:
        if start_at is None:
            return datetime.now()
        if isinstance(start_at, datetime):
            return start_at
        return datetime.fromisoformat(start_at)

    
    def get_next_run(self):
        now = datetime.now()
        while self.next_run <= now:
            self.next_run += timedelta(seconds=self.interval_seconds)
        print(f"[Monitor] next run scheduled at {self.next_run}")


    # 定期执行任务
    def start_interval(self):
        while True:
            wait_seconds = (self.next_run - datetime.now()).total_seconds()
            print(f"[Monitor] waiting for {wait_seconds:.2f} seconds until next run at {self.next_run}")
            if wait_seconds > 0:
                time.sleep(min(wait_seconds, self.check_interval_seconds))
                continue
            try:
                self.job()
            except Exception as exc:  # pragma: no cover
                print(f"[Monitor] job error: {exc}")
            self.get_next_run()



def _add_trade_to_path() -> Path:
    wxbot_dir = Path(__file__).resolve().parent
    trade_dir = wxbot_dir.parent / "Trade"
    if str(trade_dir) not in sys.path:
        sys.path.insert(0, str(trade_dir))
    return trade_dir


def send_hourly_trade_chart(
    wx,
    who: str = "fzx",
    symbol: str = "BTCUSDT",
    anchor_hour: Optional[datetime] = None,
    min_amplitude_pct: float = 0.5,
) -> str:
    trade_dir = _add_trade_to_path()
    from draw.candlestick_drawer import CandlestickDrawer

    anchor = (anchor_hour or datetime.now()).replace(minute=0, second=0, microsecond=0)
    drawer = CandlestickDrawer(symbol=symbol, interval="1h")
    # chart_path = drawer.plot_hourly_dual_timeframe(
    #     anchor_hour=anchor,
    #     save_path=trade_dir / "draw" / "output" / f"{symbol}_dual_hourly.png",
    #     show=False,
    #     y_mode="price",
    # )
    chart_path = drawer.plot_hourly_triple_timeframe_split(
        anchor_hour=anchor,
        save_path=trade_dir / "draw" / "output" / f"{symbol}_triple_hourly.png",
        show=False,
        y_mode="price",
    )
    stats = drawer.get_last_1h_stats(anchor_hour=anchor)
    if float(stats["amplitude_pct"]) <= min_amplitude_pct:
        print(
            f"[{datetime.now():%Y-%m-%d %H:%M:%S}] skip send: "
            f"{symbol} 振幅 {stats['amplitude_pct']:.2f}% <= {min_amplitude_pct:.2f}%"
        )
        return ""

    summary = (
        f"{symbol} 最近1小时K线（{stats['start']:%H:%M}-{stats['end']:%H:%M}）\n"
        f"振幅: {stats['amplitude_pct']:.2f}%\n"
        f"涨跌幅: {stats['change_pct']:.2f}%\n"
        f"收盘价: {stats['close']:.4f}"
    )
    wx.SendMsg(summary, who=who)
    wx.SendFiles(chart_path, who=who)
    return chart_path


if __name__ == "__main__":
    from wxauto import WeChat

    wx = WeChat(debug=True)

    def send_interval_message() -> None:
        chart_path = send_hourly_trade_chart(wx=wx, who="币圈战神", symbol="BTCUSDT", min_amplitude_pct=0.5)
        # chart_path = send_hourly_trade_chart(wx=wx, who="fzx", symbol="BTCUSDT", min_amplitude_pct=0.5)
        if chart_path:
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] sent chart: {chart_path}")

    now = datetime.now()
    this_hour = now.replace(minute=0, second=0, microsecond=0)
    first_run = this_hour if now == this_hour else this_hour + timedelta(hours=1)
    send_interval_message()  # 先执行一次
    Monitor(job=send_interval_message, interval=60 * 60, start_at=first_run).start_interval()
