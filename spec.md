# Spec: japanese-output (round 1)

A local web app that makes a Japanese learner speak every day. It picks a topic, gives a
chain of prompts, sets grammar points to use, records the session, and rewards the learner
with XP, a streak and levels.

## Constraints

- Python 3.9, Flask server, plain HTML/CSS/JS page (no Node, no build step).
- Runs with one command (`python app.py`). No API key, login, network service or paid service.
- User data: one local JSON file, `data/user.json`. Recordings: local folder `recordings/`.
- All rules live in plain Python modules in `japanese_output/` and do not import Flask.
  `app.py` only parses requests, calls those modules, and saves the state.
- Every function that depends on "today" takes the date as a parameter, so the tests can
  set the date.

## Answers to open questions (confirmed with the user before coding)

| Question | Decision |
|---|---|
| R5 minimum "10-15 min" | Depends on level: 10 min for beginner, N5 and N4; 15 min for N3, N2 and N1. |
| R4/R6 how "grammar used" is counted | Self-check after the session: the user ticks the points they used. A ticked point earns XP and counts as an SRS pass. An unticked point counts as a fail. |
| R6 how words are added | After the session the user types words (word, optional meaning). Each word not already in the list earns XP. |
| R3 retelling days | Every 4th day counted from the user's start date (days 4, 8, 12, ...). The user retells their own material and enters its title or link. |

## R1 Level

- Levels in order: `beginner, N5, N4, N3, N2, N1`. Any other value is rejected.
- The level is saved in the user file. Setting it the first time also sets `start_date`
  and the starting tree (R2).
- Changing the level later updates it and unlocks any extra start topics. It never
  re-locks topics.

## R2 Topic tree

- Each node has an `id`, a `title`, a `tier` from 0 to 5, and `requires`: a list of parent ids.
  A node can be unlocked when at least one of its parents is unlocked.
- Built-in tree:
  - tier 0: self introduction
  - tier 1: daily life
  - tier 2: work, travel, anime/manga, food, hobbies
  - tier 3: one deeper topic under each tier-2 branch
  - tier 4: opinions & society, culture comparison, technology & the future
  - tier 5: happiness, work & meaning
- Starting tier by level: beginner 0, N5 1, N4 2, N3 3, N2 4, N1 4. Every node with
  `tier <= start tier` starts unlocked. N1 also starts at 4 so it still has branches to choose.
- The learner picks the next branch: each app level-up (R6) gives one **unlock credit**.
  Spending a credit unlocks one node the learner chooses. The node must be unlockable.

## R3 Daily topic and prompt chain

- The plan for a date is made once and saved, so it does not change later that day.
- Retelling day: `(today - start_date).days % 4 == 3`.
- Topic day: pick the unlocked topic with the fewest completed sessions. On a tie, pick the
  higher tier first (newer, harder topics), then the lower id.
- Topic prompt chain, always 4 steps in this order: **describe -> story -> opinion ->
  other side**. Each topic has its own text for each step.
- Retelling chain: **summarize -> details -> reaction -> other side**. The learner enters
  the title or link of what they are retelling.

## R4 Grammar and SRS

- Built-in grammar list, each point tagged N5 to N1. Beginners get N5 points.
- New points each day: 2. These are the first points in list order that have not been
  learned yet, starting at the learner's level. When that level runs out, the next harder
  level is used.
- A point is "learned" once it has an SRS card. A card is created when the session that
  introduced the point is submitted.
- Leitner SRS: box intervals are `[1, 2, 4, 7, 15, 30, 60]` days.
  - Pass: `box = min(box + 1, 6)`, `due = today + intervals[box]`.
  - Fail: `box = 0`, `due = today + 1`.
  - A new card starts at box 0. Its first review is the self-check of the day it was introduced.
- Reviews each day: due cards (`due <= today`), oldest due date first, at most 3.
- Each of the day's points is graded (and earns grammar XP) only in the first session that
  day. Later sessions the same day don't grade it again. Ticks for points that are not in
  today's plan are ignored.

## R5 Session timing and recording

- The browser records with `MediaRecorder` and shows a timer with the minimum and the 60-min cap.
  Recording stops by itself at 60 minutes.
- Minutes count per day and are capped at 60 per day in total, across all sessions that day.
- The streak counts a day once that day's total minutes reach the minimum.
- Minutes above the minimum (up to 60) are **bonus minutes**.
- The server saves each recording in `recordings/` and lists past sessions so the learner
  can listen to them again.

## R6 XP, streak, levels

- XP per base minute (up to the minimum): 10. XP per bonus minute: 15.
- XP per grammar point ticked as used: 20.
- XP per new unique word (trimmed, case-insensitive): 5.
- Streak: the first qualifying session on a day continues the streak if the last qualifying
  day was yesterday, or else starts it again at 1. Later sessions the same day don't change it.
  The displayed streak is 0 if the last qualifying day is before yesterday.
- Levels: reaching level `L` takes `50 * L * (L - 1)` total XP (L2 = 100, L3 = 300, L4 = 600, ...).
  Each level gained gives 1 unlock credit (R2).
- After each session the app shows the XP for each part, any level-up, and the streak.

## Out of scope for round 1

- Speech recognition or automatic grammar detection.
- Multiple users, accounts, syncing.
- Tests for the HTML page and the browser recording.
