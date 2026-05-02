"""Number, duration, and time-series helpers used across commands and tasks."""

from collections.abc import Iterable
from datetime import UTC, datetime
from math import floor, log10


def display_short(num: float) -> str:
    """Render a number with short suffix: 1.23k, 45.6M, etc."""
    return _display(num, ["", "k", "M", "B", "T"])


def display_full(num: float) -> str:
    """Render a number with spelled-out suffix: 1.23 Thousand, 45.6 Million, etc."""
    return _display(num, ["", " Thousand", " Million", " Billion", " Trillion"])


def _display(num: float, names: list[str]) -> str:
    if num < 10_000:
        return str(int(num)) if num == int(num) else f"{num:g}"
    exp = 0 if num == 0 else int(floor(log10(abs(num)) / 3))
    pos = max(0, min(len(names) - 1, exp))
    return f"{round(num / 10 ** (3 * pos), 2):g}{names[pos]}"


def format_time_since(dt: datetime) -> tuple[float, str]:
    """Return (days-since-dt, human-readable label) for a past timestamp."""
    now = datetime.now(UTC)
    diff = now - dt
    days = diff.days + diff.seconds / 86400
    value = days
    unit = "day"
    if value < 1:
        value *= 24
        unit = "hour"
        if value < 1:
            value *= 60
            unit = "minute"
    if round(value) != 1:
        unit += "s"
    return days, f"{round(value)} {unit}"


def format_last_seen(online: bool, last_online: datetime | None) -> tuple[float, str]:
    """Return (days-offline, label); treats <30 s of downtime as still Online."""
    if online:
        return 0.0, "Online"
    if last_online is None:
        return float("inf"), "unknown"
    days, text = format_time_since(last_online)
    if days * 86400 < 30:
        return 0.0, "Online"
    return days, text


def smooth_series(values: Iterable[float], window: int | None = None) -> list[float]:
    """Centered rolling mean; window defaults to ~N/50, floor 6, edges shorter."""
    series = [float(v) for v in values]
    n = len(series)
    if n <= 1:
        return series
    effective = window if window is not None else max(6, n // 50)
    if effective <= 1:
        return series
    half = effective // 2
    return [
        sum(series[max(0, i - half) : min(n, i + half + 1)])
        / len(series[max(0, i - half) : min(n, i + half + 1)])
        for i in range(n)
    ]
