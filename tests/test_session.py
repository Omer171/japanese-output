import pytest

from japanese_output import session


@pytest.mark.parametrize(
    "level,minimum",
    [("beginner", 10), ("N5", 10), ("N4", 10), ("N3", 15), ("N2", 15), ("N1", 15)],
)
def test_r5_minimum_minutes_scale_with_level(level, minimum):
    assert session.min_minutes(level) == minimum


def test_r5_cap_is_one_hour():
    assert session.MAX_DAILY_MINUTES == 60


def test_r5_short_session_does_not_qualify():
    r = session.split_minutes("N5", seconds=9 * 60 + 59, minutes_before=0)
    assert r == {"counted": 9, "base": 9, "bonus": 0, "day_total": 9, "qualifies": False}


def test_r5_reaching_minimum_qualifies():
    r = session.split_minutes("N5", seconds=600, minutes_before=0)
    assert r["qualifies"] is True
    assert r["base"] == 10 and r["bonus"] == 0


def test_r5_n3_needs_fifteen_minutes():
    assert not session.split_minutes("N3", seconds=14 * 60, minutes_before=0)["qualifies"]
    assert session.split_minutes("N3", seconds=15 * 60, minutes_before=0)["qualifies"]


def test_r5_minutes_past_minimum_are_bonus():
    r = session.split_minutes("N5", seconds=25 * 60, minutes_before=0)
    assert r["base"] == 10 and r["bonus"] == 15


def test_r5_session_capped_at_sixty_minutes():
    r = session.split_minutes("N5", seconds=90 * 60, minutes_before=0)
    assert r["counted"] == 60 and r["base"] == 10 and r["bonus"] == 50


def test_r5_minutes_add_up_across_sessions_in_a_day():
    r = session.split_minutes("N5", seconds=6 * 60, minutes_before=6)
    assert r == {"counted": 6, "base": 4, "bonus": 2, "day_total": 12, "qualifies": True}


def test_r5_daily_cap_applies_across_sessions():
    r = session.split_minutes("N5", seconds=30 * 60, minutes_before=50)
    assert r["counted"] == 10 and r["bonus"] == 10 and r["day_total"] == 60


def test_r5_nothing_counts_after_cap_reached():
    r = session.split_minutes("N5", seconds=30 * 60, minutes_before=60)
    assert r["counted"] == 0 and r["base"] == 0 and r["bonus"] == 0
    assert r["qualifies"] is True


def test_r5_negative_seconds_rejected():
    with pytest.raises(ValueError):
        session.split_minutes("N5", seconds=-1, minutes_before=0)
