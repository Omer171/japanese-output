"""R5: session length rules: the level-based minimum, the 60-min cap, bonus minutes."""

from .levels import validate_level

MAX_DAILY_MINUTES = 60
_MIN_BY_LEVEL = {"beginner": 10, "N5": 10, "N4": 10, "N3": 15, "N2": 15, "N1": 15}


def min_minutes(level):
    return _MIN_BY_LEVEL[validate_level(level)]


def split_minutes(level, seconds, minutes_before):
    """Split one session's minutes into base and bonus, given minutes already spoken today.

    Only whole minutes count. The day total is capped at MAX_DAILY_MINUTES.
    """
    if seconds < 0 or minutes_before < 0:
        raise ValueError("time cannot be negative")
    minimum = min_minutes(level)
    before = min(minutes_before, MAX_DAILY_MINUTES)
    counted = min(int(seconds) // 60, MAX_DAILY_MINUTES - before)
    day_total = before + counted
    base = max(0, min(day_total, minimum) - min(before, minimum))
    return {
        "counted": counted,
        "base": base,
        "bonus": counted - base,
        "day_total": day_total,
        "qualifies": day_total >= minimum,
    }
