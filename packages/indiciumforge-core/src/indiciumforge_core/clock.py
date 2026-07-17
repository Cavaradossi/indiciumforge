from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso(timespec: str = "seconds") -> str:
    """Return the current UTC time as a timezone-aware ISO-8601 string.

    Use this instead of ``datetime.now()`` for artifact timestamps so that
    outputs are reproducible and comparable across machines and timezones.
    """
    return datetime.now(timezone.utc).isoformat(timespec=timespec)
