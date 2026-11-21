from datetime import date, timedelta

from japanese_output import content, daily, state

START = date(2026, 3, 1)

SMALL = [
    {"id": "root", "title": "Root", "tier": 0, "requires": []},
    {"id": "a", "title": "A", "tier": 1, "requires": ["root"]},
    {"id": "b", "title": "B", "tier": 1, "requires": ["root"]},
]


def test_r3_every_builtin_topic_has_the_four_step_chain():
    for t in content.TOPICS:
        chain = daily.prompt_chain(t)
        assert [p["step"] for p in chain] == ["describe", "story", "opinion", "other_side"]
        assert all(p["prompt"].strip() for p in chain), t["id"]


def test_r3_retelling_chain_builds_up():
    chain = daily.retelling_chain()
    assert [p["step"] for p in chain] == ["summarize", "details", "reaction", "other_side"]
    assert all(p["prompt"].strip() for p in chain)


def test_r3_every_fourth_day_is_retelling():
    flags = [daily.is_retelling_day(START, START + timedelta(days=i)) for i in range(12)]
    assert flags == [False, False, False, True] * 3


def test_r3_first_day_is_never_retelling():
    assert not daily.is_retelling_day(START, START)


def test_r3_pick_topic_prefers_least_practiced():
    picked = daily.pick_topic(SMALL, {"root", "a", "b"}, {"root": 0, "a": 2, "b": 1})
    assert picked["id"] == "root"


def test_r3_pick_topic_ties_go_to_harder_then_lower_id():
    picked = daily.pick_topic(SMALL, {"root", "a", "b"}, {})
    assert picked["id"] == "a"


def test_r3_pick_topic_only_from_unlocked():
    picked = daily.pick_topic(SMALL, {"root"}, {"root": 5})
    assert picked["id"] == "root"


def _ready_state(level="N5"):
    s = state.new_state()
    state.set_level(s, level, START)
    return s


def test_r3_topic_day_plan_has_topic_and_chain():
    plan = state.get_plan(_ready_state(), START)
    assert plan["kind"] == "topic"
    assert plan["topic_id"] in {"self_intro", "daily_life"}
    assert len(plan["prompts"]) == 4


def test_r3_retelling_day_plan_has_retelling_chain():
    plan = state.get_plan(_ready_state(), START + timedelta(days=3))
    assert plan["kind"] == "retelling"
    assert plan["topic_id"] is None
    assert [p["step"] for p in plan["prompts"]][0] == "summarize"


def test_r3_plan_is_stable_within_a_day():
    s = _ready_state()
    first = state.get_plan(s, START)
    s["unlock_credits"] = 1
    state.unlock_topic(s, "work")
    s["topic_counts"][first["topic_id"]] = 99
    assert state.get_plan(s, START) == first


def test_r3_new_day_gets_new_plan():
    s = _ready_state()
    first = state.get_plan(s, START)
    state.finish_session(s, START, seconds=600, grammar_used=[], words=[])
    second = state.get_plan(s, START + timedelta(days=1))
    assert second["date"] == "2026-03-02"
    assert second["topic_id"] != first["topic_id"]


def test_r3_get_plan_requires_level():
    import pytest

    with pytest.raises(ValueError):
        state.get_plan(state.new_state(), START)
