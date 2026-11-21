from datetime import date, timedelta

import pytest

from japanese_output import progress, state

DAY = date(2026, 5, 10)


# --- XP -----------------------------------------------------------------

def test_r6_xp_for_minutes_grammar_and_words():
    xp = progress.session_xp(base_minutes=10, bonus_minutes=5, grammar_used=2, new_words=3)
    assert xp == {"minutes": 100, "bonus": 75, "grammar": 40, "words": 15, "total": 230}


def test_r6_bonus_minutes_worth_more_than_base():
    assert progress.XP_PER_BONUS_MINUTE > progress.XP_PER_MINUTE


def test_r6_new_unique_words_trimmed_and_case_insensitive():
    existing = [{"word": "Taberu"}]
    words = [{"word": " taberu "}, {"word": "nomu"}, {"word": "NOMU"}, {"word": "  "}]
    assert [w["word"] for w in progress.new_unique_words(existing, words)] == ["nomu"]


# --- streak -------------------------------------------------------------

def test_r6_first_qualifying_day_starts_streak():
    s = progress.update_streak({"count": 0, "last_day": None}, DAY, qualified=True)
    assert s == {"count": 1, "last_day": "2026-05-10"}


def test_r6_consecutive_days_extend_streak():
    s = {"count": 3, "last_day": "2026-05-09"}
    assert progress.update_streak(s, DAY, True) == {"count": 4, "last_day": "2026-05-10"}


def test_r6_same_day_does_not_double_count():
    s = {"count": 4, "last_day": "2026-05-10"}
    assert progress.update_streak(s, DAY, True) == s


def test_r6_missed_day_restarts_streak():
    s = {"count": 9, "last_day": "2026-05-07"}
    assert progress.update_streak(s, DAY, True) == {"count": 1, "last_day": "2026-05-10"}


def test_r6_non_qualifying_session_leaves_streak():
    s = {"count": 2, "last_day": "2026-05-09"}
    assert progress.update_streak(s, DAY, False) == s


def test_r6_displayed_streak_drops_to_zero_after_missed_day():
    s = {"count": 5, "last_day": "2026-05-08"}
    assert progress.current_streak(s, DAY) == 0
    assert progress.current_streak(s, DAY - timedelta(days=1)) == 5
    assert progress.current_streak({"count": 0, "last_day": None}, DAY) == 0


# --- levels -------------------------------------------------------------

@pytest.mark.parametrize("lvl,xp", [(1, 0), (2, 100), (3, 300), (4, 600), (5, 1000)])
def test_r6_xp_needed_per_level(lvl, xp):
    assert progress.xp_for_level(lvl) == xp


@pytest.mark.parametrize("xp,lvl", [(0, 1), (99, 1), (100, 2), (299, 2), (300, 3), (1000, 5)])
def test_r6_level_for_xp(xp, lvl):
    assert progress.level_for_xp(xp) == lvl


def test_r6_level_progress():
    assert progress.level_progress(150) == {"level": 2, "into": 50, "needed": 200}


# --- full session through state ------------------------------------------

def _ready_state(level="N5"):
    s = state.new_state()
    state.set_level(s, level, DAY)
    return s


def test_r6_finish_session_awards_xp_and_saves_words():
    s = _ready_state()
    plan = state.get_plan(s, DAY)
    g = plan["new_grammar"][0]
    words = [{"word": "散歩", "meaning": "walk"}, {"word": "散歩"}]
    r = state.finish_session(s, DAY, seconds=12 * 60, grammar_used=[g], words=words)
    assert r["xp"] == {"minutes": 100, "bonus": 30, "grammar": 20, "words": 5, "total": 155}
    assert s["xp"] == 155
    assert [w["word"] for w in s["words"]] == ["散歩"]
    assert s["words"][0] == {"word": "散歩", "meaning": "walk", "added": "2026-05-10"}


def test_r6_level_up_gives_unlock_credit_to_choose_branch():
    s = _ready_state()
    r = state.finish_session(s, DAY, seconds=10 * 60, grammar_used=[], words=[])
    assert r["level_before"] == 1 and r["level_after"] == 2
    assert r["credits_gained"] == 1
    assert s["unlock_credits"] == 1
    choice = state.summary(s, DAY)["unlockable"][0]
    state.unlock_topic(s, choice)
    assert choice in s["unlocked"] and s["unlock_credits"] == 0


def test_r6_multi_level_jump_gives_multiple_credits():
    s = _ready_state()
    s["xp"] = 90
    r = state.finish_session(s, DAY, seconds=60 * 60, grammar_used=[], words=[])
    assert r["level_after"] - r["level_before"] == r["credits_gained"] >= 2


def test_r6_streak_counts_through_finish_session():
    s = _ready_state()
    state.finish_session(s, DAY, seconds=600, grammar_used=[], words=[])
    state.finish_session(s, DAY + timedelta(days=1), seconds=600, grammar_used=[], words=[])
    r = state.finish_session(s, DAY + timedelta(days=2), seconds=300, grammar_used=[], words=[])
    assert r["streak"] == 2 and r["qualified"] is False
    r = state.finish_session(s, DAY + timedelta(days=2), seconds=300, grammar_used=[], words=[])
    assert r["streak"] == 3 and r["qualified"] is True


def test_r6_topic_count_and_session_log_recorded():
    s = _ready_state()
    plan = state.get_plan(s, DAY)
    state.finish_session(s, DAY, seconds=600, grammar_used=[], words=[], recording="a.webm")
    assert s["topic_counts"][plan["topic_id"]] == 1
    log = s["sessions"][-1]
    assert log["date"] == "2026-05-10" and log["recording"] == "a.webm"
    assert log["minutes"] == 10 and log["kind"] == "topic"


def test_r6_retelling_session_saves_source():
    s = _ready_state()
    day4 = DAY + timedelta(days=3)
    state.finish_session(s, day4, seconds=600, grammar_used=[], words=[], source="NHK article")
    assert s["sessions"][-1]["kind"] == "retelling"
    assert s["sessions"][-1]["source"] == "NHK article"


def test_r6_summary_shows_game_status():
    s = _ready_state()
    state.finish_session(s, DAY, seconds=600, grammar_used=[], words=[])
    summ = state.summary(s, DAY)
    assert summ["streak"] == 1
    assert summ["level"] == 2
    assert summ["xp"] == 100
    assert summ["minutes_today"] == 10
    assert summ["min_minutes"] == 10
    assert summ["unlock_credits"] == 1
    statuses = {t["id"]: t["status"] for t in summ["tree"]}
    assert statuses["daily_life"] == "unlocked"
    assert "unlockable" in statuses.values() and "locked" in statuses.values()


def test_r6_finish_session_requires_level():
    with pytest.raises(ValueError):
        state.finish_session(state.new_state(), DAY, seconds=600, grammar_used=[], words=[])
