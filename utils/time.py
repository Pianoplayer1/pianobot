"""Time helpers: rounded snapshot ticks and Eden award-cycle math."""

from datetime import UTC, datetime, timedelta


def get_rounded_time(minutes: int = 5) -> datetime:
    """Round the current UTC time to the nearest N-minute mark."""
    now = datetime.now(UTC)
    interval = minutes * 60
    seconds = (now - datetime.min.replace(tzinfo=UTC)).seconds
    difference = (seconds + interval / 2) // interval * interval - seconds
    return now + timedelta(seconds=difference, microseconds=-now.microsecond)


def get_cycle(dt: datetime) -> str:
    """Eden promotion cycle code, e.g. '2604A' for April 1–14 2026."""
    return f"{dt.year % 100:02}{dt.month:02}{'A' if dt.day < 15 else 'B'}"


def get_cycle_window(dt: datetime) -> tuple[datetime, datetime]:
    """Start (inclusive) and end (exclusive) of the cycle that contains dt."""
    year, month = dt.year, dt.month
    if dt.day < 15:
        start = datetime(year, month, 1, tzinfo=UTC)
        end = datetime(year, month, 15, tzinfo=UTC)
    else:
        start = datetime(year, month, 15, tzinfo=UTC)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=UTC)
        else:
            end = datetime(year, month + 1, 1, tzinfo=UTC)
    return start, end


def get_prev_cycle(dt: datetime) -> str:
    """Cycle code of the cycle immediately preceding the one that contains dt."""
    start, _ = get_cycle_window(dt)
    prev_end = start - timedelta(seconds=1)
    return get_cycle(prev_end)
