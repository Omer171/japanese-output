# japanese-output

A local web app that gets you **speaking** Japanese every day, not just reading and listening.

## What it does

- **Asks your level** (beginner, N5 to N1) and starts you at the right point on the topic tree,
  so you don't begin from zero. (R1)
- **Topic tree**: self introduction → daily life → branches (work, travel, anime/manga,
  food, hobbies) → deeper topics → abstract topics (society, culture, technology) →
  philosophy. Each level-up gives you a credit to unlock the branch *you* choose. (R2)
- **A topic every day**, with a 4-step prompt chain so you don't run out of things to say:
  describe → tell a story → give your opinion → argue the other side. Every 4th day is a
  **retelling day**: you retell an article, interview or video you read or heard. (R3)
- **Grammar to use**: 2 new points a day, plus the points you've already learned, which come
  back on a spaced-repetition (SRS) schedule. After speaking, you tick the ones you used. (R4)
- **Timer and recorder**: speak for 10 min (beginner to N4) or 15 min (N3 to N1) to keep your
  streak. You can keep going up to 60 min a day for bonus XP. Every session is recorded in the
  browser so you can listen back later. (R5)
- **Game layer**: XP for minutes spoken (bonus minutes are worth more), grammar used and new
  words added. Plus a daily streak, and levels that unlock new branches. (R6)

Everything runs locally and offline: no account, API key or paid service. Your progress is in
`data/user.json` and your recordings are in `recordings/`.

## Setup (once)

Needs Python 3.9.

In Git Bash, from a fresh clone:

```bash
python -m venv .venv
source .venv/Scripts/activate        # on macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Run

```bash
python app.py
```

Then open http://127.0.0.1:5000 and allow microphone access. Recording works in recent
Chrome, Edge and Firefox.

## Test

```bash
python -m pytest
```

(Run these after the `source .venv/Scripts/activate` line from Setup.)

The tests cover all the rule logic in `japanese_output/`. Each test name contains the
requirement it checks (`test_r1_...` to `test_r6_...`). The exact rules are in `spec.md`.
Design decisions are in `docs/decisions/`.
