import pytest

from japanese_output import content, tree

SMALL = [
    {"id": "root", "title": "Root", "tier": 0, "requires": []},
    {"id": "a", "title": "A", "tier": 1, "requires": ["root"]},
    {"id": "b", "title": "B", "tier": 1, "requires": ["root"]},
    {"id": "a2", "title": "A2", "tier": 2, "requires": ["a"]},
    {"id": "ab", "title": "AB", "tier": 2, "requires": ["a", "b"]},
]


def _by_id(topics):
    return {t["id"]: t for t in topics}


def test_r2_builtin_tree_is_valid():
    ids = [t["id"] for t in content.TOPICS]
    assert len(ids) == len(set(ids)), "topic ids must be unique"
    nodes = _by_id(content.TOPICS)
    roots = [t for t in content.TOPICS if not t["requires"]]
    assert len(roots) == 1 and roots[0]["tier"] == 0
    for t in content.TOPICS:
        for parent in t["requires"]:
            assert parent in nodes, f"{t['id']} requires unknown {parent}"
            assert nodes[parent]["tier"] < t["tier"], "parents must be easier"


def test_r2_builtin_tree_branches_after_daily_life():
    nodes = _by_id(content.TOPICS)
    assert nodes["self_intro"]["tier"] == 0
    assert nodes["daily_life"]["requires"] == ["self_intro"]
    children = [t["id"] for t in content.TOPICS if "daily_life" in t["requires"]]
    assert {"work", "travel", "anime_manga"} <= set(children)
    assert len(children) >= 3


def test_r2_builtin_tree_reaches_abstract_topics():
    tiers = {t["tier"] for t in content.TOPICS}
    assert tiers == {0, 1, 2, 3, 4, 5}


@pytest.mark.parametrize(
    "level,tier", [("beginner", 0), ("N5", 1), ("N4", 2), ("N3", 3), ("N2", 4), ("N1", 4)]
)
def test_r2_start_tier_by_level(level, tier):
    assert tree.START_TIER[level] == tier


def test_r2_beginner_starts_at_root_only():
    assert tree.start_unlocked(content.TOPICS, "beginner") == {"self_intro"}


def test_r2_n5_starts_with_daily_life():
    assert tree.start_unlocked(content.TOPICS, "N5") == {"self_intro", "daily_life"}


def test_r2_higher_level_starts_further_up_the_tree():
    n4 = tree.start_unlocked(content.TOPICS, "N4")
    n3 = tree.start_unlocked(content.TOPICS, "N3")
    assert {"work", "travel", "anime_manga"} <= n4
    assert n4 < n3
    assert all(_by_id(content.TOPICS)[i]["tier"] <= 3 for i in n3)


def test_r2_n1_still_has_branches_to_choose():
    unlocked = tree.start_unlocked(content.TOPICS, "N1")
    assert tree.unlockable(content.TOPICS, unlocked)


def test_r2_unlockable_needs_any_parent_unlocked():
    assert tree.unlockable(SMALL, {"root"}) == ["a", "b"]
    assert tree.unlockable(SMALL, {"root", "b"}) == ["a", "ab"]
    assert tree.unlockable(SMALL, {"root", "a"}) == ["a2", "ab", "b"]


def test_r2_unlock_spends_a_credit_on_the_chosen_branch():
    unlocked, credits = tree.unlock(SMALL, {"root"}, 2, "b")
    assert unlocked == {"root", "b"}
    assert credits == 1


def test_r2_unlock_without_credit_is_rejected():
    with pytest.raises(ValueError):
        tree.unlock(SMALL, {"root"}, 0, "a")


def test_r2_unlock_of_locked_away_node_is_rejected():
    with pytest.raises(ValueError):
        tree.unlock(SMALL, {"root"}, 1, "a2")


def test_r2_unlock_of_unknown_or_already_unlocked_node_is_rejected():
    with pytest.raises(ValueError):
        tree.unlock(SMALL, {"root"}, 1, "nope")
    with pytest.raises(ValueError):
        tree.unlock(SMALL, {"root", "a"}, 1, "a")


def test_r2_unlock_does_not_mutate_input():
    unlocked = {"root"}
    tree.unlock(SMALL, unlocked, 1, "a")
    assert unlocked == {"root"}
