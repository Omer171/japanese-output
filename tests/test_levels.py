from datetime import date

import pytest

from japanese_output import levels, state


def test_r1_levels_are_the_six_in_order():
    assert levels.LEVELS == ("beginner", "N5", "N4", "N3", "N2", "N1")


@pytest.mark.parametrize("level", ["beginner", "N5", "N4", "N3", "N2", "N1"])
def test_r1_valid_levels_are_accepted(level):
    assert levels.validate_level(level) == level


@pytest.mark.parametrize("bad", ["", "N6", "n5", "expert", None, 3])
def test_r1_invalid_levels_are_rejected(bad):
    with pytest.raises(ValueError):
        levels.validate_level(bad)


def test_r1_beginner_uses_n5_grammar():
    assert levels.grammar_level("beginner") == "N5"
    assert levels.grammar_level("N3") == "N3"


def test_r1_new_state_has_no_level_yet():
    s = state.new_state()
    assert s["level"] is None
    assert s["start_date"] is None


def test_r1_setting_level_saves_it_and_start_date():
    s = state.new_state()
    state.set_level(s, "N4", date(2026, 1, 10))
    assert s["level"] == "N4"
    assert s["start_date"] == "2026-01-10"


def test_r1_changing_level_keeps_start_date_and_never_relocks():
    s = state.new_state()
    state.set_level(s, "N3", date(2026, 1, 10))
    before = set(s["unlocked"])
    state.set_level(s, "beginner", date(2026, 2, 1))
    assert s["level"] == "beginner"
    assert s["start_date"] == "2026-01-10"
    assert before <= set(s["unlocked"])


def test_r1_raising_level_unlocks_extra_start_topics():
    s = state.new_state()
    state.set_level(s, "beginner", date(2026, 1, 10))
    state.set_level(s, "N3", date(2026, 1, 11))
    assert "work" in s["unlocked"]


def test_r1_set_level_rejects_invalid_level():
    s = state.new_state()
    with pytest.raises(ValueError):
        state.set_level(s, "N7", date(2026, 1, 10))
    assert s["level"] is None
