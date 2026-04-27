from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Callable, Optional, Union


class Monitor:
    """
    Run a callback by either:
    1) daily fixed time: run_at="HH:MM[:SS]"
    2) interval schedule: start_at + interval (seconds or timedelta)
    """

    def __init__(
        self,
        job: Callable[[], None],
        run_at: Optional[str] = None,
        interval: Optional[Union[int, float, timedelta]] = None,
        start_at: Optional[Union[str, datetime]] = None,
        check_interval_seconds: float = 1.0,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        if (run_at is None) and (interval is None):
            raise ValueError("Exactly one mode is required: run_at OR interval")

        self.job = job
        self.check_interval_seconds = max(0.2, check_interval_seconds)
        self.on_error = on_error

        self.run_at = run_at
        self.interval_seconds: Optional[float] = None
        self.next_run: Optional[datetime] = None

        if run_at is not None:
            self.target_hour, self.target_minute, self.target_second = self._parse_clock_time(run_at)
        else:
            self.interval_seconds = self._parse_interval_seconds(interval)
            self.next_run = self._parse_start_time(start_at)

    @staticmethod
    def _parse_clock_time(value: str) -> tuple[int, int, int]:
        parts = value.split(":")
        if len(parts) not in (2, 3):
            raise ValueError("run_at must be 'HH:MM' or 'HH:MM:SS'")

        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) == 3 else 0

        if not (0 <= hour <= 23):
            raise ValueError("hour must be in [0, 23]")
        if not (0 <= minute <= 59):
            raise ValueError("minute must be in [0, 59]")
        if not (0 <= second <= 59):
            raise ValueError("second must be in [0, 59]")

        return hour, minute, second

    @staticmethod
    def _parse_interval_seconds(interval: Optional[Union[int, float, timedelta]]) -> float:
        if interval is None:
            raise ValueError("interval is required in interval mode")
        if isinstance(interval, timedelta):
            seconds = interval.total_seconds()
        else:
            seconds = float(interval)
        if seconds <= 0:
            raise ValueError("interval must be > 0")
        return seconds

    @staticmethod
    def _parse_start_time(start_at: Optional[Union[str, datetime]]) -> datetime:
        if start_at is None:
            return datetime.now()
        if isinstance(start_at, datetime):
            return start_at
        return datetime.fromisoformat(start_at)

    def _next_daily_run_time(self, now: Optional[datetime] = None) -> datetime:
        now = now or datetime.now()
        target_today = now.replace(
            hour=self.target_hour,
            minute=self.target_minute,
            second=self.target_second,
            microsecond=0,
        )
        if now < target_today:
            return target_today
        return target_today + timedelta(days=1)

    def _advance_interval_next_run(self) -> None:
        assert self.interval_seconds is not None
        assert self.next_run is not None
        now = datetime.now()

        # Catch up if process wakes up late.
        while self.next_run <= now:
            self.next_run += timedelta(seconds=self.interval_seconds)

    def start(self) -> None:
        """Blocking loop. Call in main thread or a background thread."""
        while True:
            if self.run_at is not None:
                next_run = self._next_daily_run_time()
            else:
                assert self.next_run is not None
                next_run = self.next_run

            wait_seconds = (next_run - datetime.now()).total_seconds()
            if wait_seconds > 0:
                time.sleep(min(wait_seconds, self.check_interval_seconds))
                continue

            try:
                self.job()
            except Exception as exc:  # pragma: no cover
                if self.on_error:
                    self.on_error(exc)
                else:
                    print(f"[Monitor] job error: {exc}")

            if self.run_at is None:
                self._advance_interval_next_run()
            else:
                # Avoid duplicate execution inside the same second.
                time.sleep(1.0)


def run_daily(run_at: str, job: Callable[[], None]) -> None:
    Monitor(run_at=run_at, job=job).start()


def run_interval(interval, job, start_at):
    Monitor(interval=interval, start_at=start_at, job=job).start()


if __name__ == "__main__":
    from wxauto import WeChat

    wx = WeChat(debug=True)

    def send_interval_message() -> None:
        wx.SendMsg("定时提醒：每5s发送一次。", who="wyk")
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] sent")

    # Example: from now, run every 5 minutes.
    run_interval(interval=5, job=send_interval_message, start_at=datetime.now())
    # run_interval(interval=5 * 60, job=send_interval_message, start_at=datetime.now())
