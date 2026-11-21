"""R6: XP, streak and app levels."""

from datetime import date, timedelta

XP_PER_MINUTE = 10
XP_PER_BONUS_MINUTE = 15
XP_PER_GRAMMAR = 20
XP_PER_WORD = 5


def session_xp(base_minutes, bonus_minutes, grammar_used, new_words):
    xp = {
        "minutes": base_minutes * XP_PER_MINUTE,
        "bonus": bonus_minutes * XP_PER_BONUS_MINUTE,
        "grammar": grammar_used * XP_PER_GRAMMAR,
        "words": new_words * XP_PER_WORD,
    }
    xp["total"] = sum(xp.values())
    return xp


def _norm(word):
    return word.strip().casefold()


def new_unique_words(existing, words):
    """Words not already in ``existing`` (trimmed, case-insensitive), with no repeats."""
    seen = {_norm(w["word"]) for w in existing}
    out = []
    for w in words:
        key = _norm(w.get("word", ""))
        if key and key not in seen:
            seen.add(key)
            out.append(w)
    return out


def update_streak(streak, today, qualified):
    if not qualified or streak["last_day"] == today.isoformat():
        return dict(streak)
    yesterday = (today - timedelta(days=1)).isoformat()
    count = streak["count"] + 1 if streak["last_day"] == yesterday else 1
    return {"count": count, "last_day": today.isoformat()}


def current_streak(streak, today):
    """Streak to show today: still alive if the last qualifying day was today or yesterday."""
    if not streak["last_day"]:
        return 0
    gap = (today - date.fromisoformat(streak["last_day"])).days
    return streak["count"] if gap <= 1 else 0


def xp_for_level(level):
    """Total XP needed to reach ``level`` (level 1 needs 0)."""
    return 50 * level * (level - 1)


def level_for_xp(xp):
    level = 1
    while xp_for_level(level + 1) <= xp:
        level += 1
    return level


def level_progress(xp):
    level = level_for_xp(xp)
    floor = xp_for_level(level)
    return {"level": level, "into": xp - floor, "needed": xp_for_level(level + 1) - floor}
