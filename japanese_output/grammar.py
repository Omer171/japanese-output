"""R4: daily new grammar points and Leitner-style SRS review."""

from datetime import date, timedelta

from .levels import grammar_level

NEW_PER_DAY = 2
MAX_REVIEWS = 3
INTERVALS = (1, 2, 4, 7, 15, 30, 60)  # days until next review, by box
JLPT_ORDER = ("N5", "N4", "N3", "N2", "N1")


def new_points(points, level, srs, count=NEW_PER_DAY):
    """First ``count`` unlearned points starting at the learner's level, then harder ones."""
    start = JLPT_ORDER.index(grammar_level(level))
    allowed = set(JLPT_ORDER[start:])
    ordered = sorted(
        (p for p in points if p["level"] in allowed and p["id"] not in srs),
        key=lambda p: JLPT_ORDER.index(p["level"]),  # stable sort keeps list order in a level
    )
    return ordered[:count]


def new_card(today):
    return {"box": 0, "due": today.isoformat()}


def review(card, passed, today):
    """Return the updated card after a pass or fail."""
    if passed:
        box = min(card["box"] + 1, len(INTERVALS) - 1)
        return {"box": box, "due": (today + timedelta(days=INTERVALS[box])).isoformat()}
    return {"box": 0, "due": (today + timedelta(days=INTERVALS[0])).isoformat()}


def due_reviews(srs, today, limit=MAX_REVIEWS):
    """Ids of cards due on or before today, oldest due first (ties by id)."""
    due = [
        (card["due"], gid)
        for gid, card in srs.items()
        if date.fromisoformat(card["due"]) <= today
    ]
    return [gid for _, gid in sorted(due)[:limit]]
