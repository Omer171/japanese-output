from datetime import date, timedelta

from japanese_output import content, grammar, state

TODAY = date(2026, 4, 1)

POINTS = [
    {"id": "n5a", "level": "N5"},
    {"id": "n5b", "level": "N5"},
    {"id": "n5c", "level": "N5"},
    {"id": "n4a", "level": "N4"},
    {"id": "n4b", "level": "N4"},
    {"id": "n3a", "level": "N3"},
]


def test_r4_builtin_grammar_list_is_valid():
    ids = [g["id"] for g in content.GRAMMAR]
    assert len(ids) == len(set(ids))
    levels = {g["level"] for g in content.GRAMMAR}
    assert levels == {"N5", "N4", "N3", "N2", "N1"}
    for g in content.GRAMMAR:
        assert g["pattern"] and g["meaning"] and g["example"], g["id"]


def test_r4_two_new_points_per_day_at_user_level():
    picked = grammar.new_points(POINTS, "N4", srs={})
    assert [p["id"] for p in picked] == ["n4a", "n4b"]
    assert grammar.NEW_PER_DAY == 2


def test_r4_beginner_gets_n5_points():
    picked = grammar.new_points(POINTS, "beginner", srs={})
    assert [p["id"] for p in picked] == ["n5a", "n5b"]


def test_r4_new_points_skip_learned_and_spill_to_next_level():
    srs = {"n5a": {}, "n5b": {}}
    picked = grammar.new_points(POINTS, "N5", srs=srs)
    assert [p["id"] for p in picked] == ["n5c", "n4a"]


def test_r4_new_points_empty_when_everything_learned():
    srs = {p["id"]: {} for p in POINTS}
    assert grammar.new_points(POINTS, "N5", srs=srs) == []


def test_r4_new_points_do_not_go_below_user_level():
    srs = {"n3a": {}}
    assert grammar.new_points(POINTS, "N3", srs=srs) == []


def test_r4_new_card_is_due_today_in_box_zero():
    assert grammar.new_card(TODAY) == {"box": 0, "due": "2026-04-01"}


def test_r4_pass_moves_up_a_box_with_longer_interval():
    card = grammar.new_card(TODAY)
    expected = [2, 4, 7, 15, 30, 60, 60]
    day = TODAY
    for i, gap in enumerate(expected):
        card = grammar.review(card, True, day)
        assert card["box"] == min(i + 1, 6)
        assert card["due"] == (day + timedelta(days=gap)).isoformat()
        day = day + timedelta(days=gap)


def test_r4_fail_resets_to_box_zero_due_tomorrow():
    card = {"box": 4, "due": TODAY.isoformat()}
    card = grammar.review(card, False, TODAY)
    assert card == {"box": 0, "due": "2026-04-02"}


def test_r4_due_reviews_oldest_first_capped_at_three():
    srs = {
        "a": {"box": 1, "due": "2026-03-30"},
        "b": {"box": 1, "due": "2026-03-28"},
        "c": {"box": 1, "due": "2026-04-01"},
        "d": {"box": 1, "due": "2026-03-29"},
        "e": {"box": 1, "due": "2026-04-02"},
    }
    assert grammar.due_reviews(srs, TODAY) == ["b", "d", "a"]
    assert grammar.MAX_REVIEWS == 3


def test_r4_nothing_due_means_no_reviews():
    assert grammar.due_reviews({"a": {"box": 2, "due": "2026-05-01"}}, TODAY) == []


def _ready_state(level="N5"):
    s = state.new_state()
    state.set_level(s, level, TODAY)
    return s


def test_r4_plan_includes_new_points_and_reviews():
    s = _ready_state()
    plan = state.get_plan(s, TODAY)
    assert len(plan["new_grammar"]) == 2
    assert plan["review_grammar"] == []


def test_r4_session_turns_new_points_into_srs_cards():
    s = _ready_state()
    plan = state.get_plan(s, TODAY)
    used, unused = plan["new_grammar"]
    state.finish_session(s, TODAY, seconds=600, grammar_used=[used], words=[])
    assert s["srs"][used] == {"box": 1, "due": "2026-04-03"}
    assert s["srs"][unused] == {"box": 0, "due": "2026-04-02"}


def test_r4_learned_points_come_back_for_review():
    s = _ready_state()
    plan = state.get_plan(s, TODAY)
    state.finish_session(s, TODAY, seconds=600, grammar_used=[], words=[])
    tomorrow = state.get_plan(s, TODAY + timedelta(days=1))
    assert set(tomorrow["review_grammar"]) == set(plan["new_grammar"])
    assert not set(tomorrow["new_grammar"]) & set(plan["new_grammar"])


def test_r4_second_session_same_day_reviews_once():
    s = _ready_state()
    plan = state.get_plan(s, TODAY)
    g = plan["new_grammar"][0]
    state.finish_session(s, TODAY, seconds=600, grammar_used=[g], words=[])
    state.finish_session(s, TODAY, seconds=600, grammar_used=[g], words=[])
    assert s["srs"][g]["box"] == 1


def test_r4_grammar_used_outside_plan_is_ignored():
    s = _ready_state()
    state.get_plan(s, TODAY)
    result = state.finish_session(s, TODAY, seconds=600, grammar_used=["not_today"], words=[])
    assert result["xp"]["grammar"] == 0
    assert "not_today" not in s["srs"]
