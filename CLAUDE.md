# CLAUDE.md

Local Flask app for daily Japanese speaking practice. Requirements: `problem.md` (R1-R6).
Detailed rules: `spec.md`.

## Stack and constraints
- Python 3.9, Flask, plain HTML/CSS/JS in `static/` (no Node, no build step).
- Must run with one command (`python app.py`). No API keys, logins, network or paid services.
- User data goes in `data/user.json`. Recordings go in `recordings/`. Both are gitignored.

## Layout
- `japanese_output/`: all rules, as plain Python. Never import Flask here.
  - `levels.py` (R1), `tree.py` (R2), `daily.py` (R3), `grammar.py` (R4),
    `session.py` (R5), `progress.py` (R6), `state.py` (ties them together),
    `content.py` (built-in topics and grammar), `storage.py` (JSON file).
- `app.py`: thin Flask layer. `static/`: the page.
- `tests/`: pytest. Each test name contains its requirement ID, e.g. `test_r4_...`.

## Commands
- Setup: `py -3.9 -m venv .venv` then `.venv\Scripts\pip install -r requirements-dev.txt`
- Run: `.venv\Scripts\python app.py` (http://127.0.0.1:5000)
- Test: `.venv\Scripts\python -m pytest`

## Rules
- Write or update the tests before changing logic. Don't test the HTML or the browser recording.
- Pass "today" in as a `date` parameter. Never call `date.today()` inside `japanese_output/`.
- Make small commits that say what changed and why. Never amend or undo a commit.
