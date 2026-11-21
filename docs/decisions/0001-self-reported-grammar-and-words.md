# 0001: Count grammar use and new words by self-report, not speech recognition

- Status: accepted
- Date: 2026-11-21
- Requirements: R4, R6 (and the round-1 constraint: one command, no API key, login or paid service)

## Y-statement

In the context of **awarding XP for grammar points used and new words added (R6), and grading
grammar for SRS review (R4)**,
facing **the requirement that the app runs offline with one command and no API key, login or
paid service, so there is no cloud speech-to-text or language model to check what was said**,
we decided for **a self-check after each session: the learner ticks which of the day's
grammar points they used (a tick is an SRS pass, no tick is a fail) and types the new words
they used or looked up**,
and neglected **on-device speech recognition (e.g. Vosk/Whisper models), browser
`SpeechRecognition` (sends audio to a cloud service in most browsers and is not supported
in Firefox), and cloud speech APIs**,
to achieve **zero setup beyond `pip install flask`, full offline use, private audio that
never leaves the machine, and simple rule logic that is easy to test**,
accepting that **XP and SRS grades depend on the learner being honest. A learner can
over-tick, and nothing checks that a grammar point was used correctly. The recording sits
next to the checklist so the learner can confirm by listening back.**

## Notes

- The user confirmed this choice before coding began.
- If automatic checking is added later, it can feed the same `grammar_used` and `words`
  inputs of `japanese_output.state.finish_session`, so the rule logic would not change.
