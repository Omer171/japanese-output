"""R2: the branching topic tree, where the learner starts on it, and unlocking branches."""

# Every node with tier <= START_TIER[level] starts unlocked. N1 stops at tier 4 so
# the learner still chooses the last branches.
START_TIER = {"beginner": 0, "N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 4}


def start_unlocked(topics, level):
    limit = START_TIER[level]
    return {t["id"] for t in topics if t["tier"] <= limit}


def unlockable(topics, unlocked):
    """Locked node ids with at least one unlocked parent, sorted by id."""
    return sorted(
        t["id"]
        for t in topics
        if t["id"] not in unlocked and any(p in unlocked for p in t["requires"])
    )


def unlock(topics, unlocked, credits, node_id):
    """Spend one credit to unlock ``node_id``. Returns (new_unlocked, new_credits)."""
    if credits < 1:
        raise ValueError("no unlock credits left: level up to earn one")
    if node_id not in {t["id"] for t in topics}:
        raise ValueError("unknown topic: %s" % node_id)
    if node_id in unlocked:
        raise ValueError("already unlocked: %s" % node_id)
    if node_id not in unlockable(topics, unlocked):
        raise ValueError("unlock a parent topic first: %s" % node_id)
    return set(unlocked) | {node_id}, credits - 1
