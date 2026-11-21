"""R1: the learner's starting Japanese level."""

LEVELS = ("beginner", "N5", "N4", "N3", "N2", "N1")


def validate_level(level):
    """Return ``level`` if it is one of LEVELS, otherwise raise ValueError."""
    if not isinstance(level, str) or level not in LEVELS:
        raise ValueError("level must be one of " + ", ".join(LEVELS))
    return level


def grammar_level(level):
    """JLPT level used for grammar. Beginners start with N5 points."""
    validate_level(level)
    return "N5" if level == "beginner" else level
