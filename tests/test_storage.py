from datetime import date

from japanese_output import state, storage


def test_r1_level_survives_save_and_load(tmp_path):
    path = tmp_path / "user.json"
    s = state.new_state()
    state.set_level(s, "N3", date(2026, 6, 1))
    storage.save(path, s)
    loaded = storage.load(path)
    assert loaded["level"] == "N3"
    assert loaded == s


def test_r1_missing_file_gives_fresh_state(tmp_path):
    assert storage.load(tmp_path / "nope.json") == state.new_state()


def test_r1_save_creates_folder_and_keeps_japanese_readable(tmp_path):
    path = tmp_path / "sub" / "user.json"
    s = state.new_state()
    s["words"].append({"word": "勉強", "meaning": "", "added": "2026-06-01"})
    storage.save(path, s)
    assert "勉強" in path.read_text(encoding="utf-8")


def test_r1_old_file_gets_new_default_keys(tmp_path):
    path = tmp_path / "user.json"
    path.write_text('{"level": "N5"}', encoding="utf-8")
    loaded = storage.load(path)
    assert loaded["level"] == "N5"
    assert loaded["xp"] == 0 and loaded["srs"] == {}
