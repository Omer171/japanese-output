"""Joins the rule modules into actions on the saved user state (a JSON-safe dict).

Every function takes ``today`` as a parameter so tests can control the date.
"""

from datetime import date

from . import content, daily, grammar, levels, progress, session, tree


def new_state():
    return {
        "version": 1,
        "level": None,          # R1 JLPT level
        "start_date": None,     # first day, for retelling-day rhythm
        "xp": 0,
        "unlocked": [],
        "unlock_credits": 0,
        "streak": {"count": 0, "last_day": None},
        "day_minutes": {},      # "YYYY-MM-DD" -> minutes counted that day
        "topic_counts": {},     # topic id -> sessions completed
        "srs": {},              # grammar id -> {"box", "due"}
        "words": [],            # {"word", "meaning", "added"}
        "plan": None,           # today's plan, fixed once made
        "sessions": [],
    }


def _require_level(state):
    if not state["level"]:
        raise ValueError("choose your Japanese level first")


# --- R1 / R2 -------------------------------------------------------------

def set_level(state, level, today):
    levels.validate_level(level)
    changed = state["level"] != level
    state["level"] = level
    if state["start_date"] is None:
        state["start_date"] = today.isoformat()
    unlocked = set(state["unlocked"]) | tree.start_unlocked(content.TOPICS, level)
    state["unlocked"] = sorted(unlocked)
    plan = state["plan"]
    if changed and plan and not plan["graded"]:
        state["plan"] = None  # rebuild with the new level's grammar
    return state


def unlock_topic(state, topic_id):
    unlocked, credits = tree.unlock(
        content.TOPICS, set(state["unlocked"]), state["unlock_credits"], topic_id
    )
    state["unlocked"] = sorted(unlocked)
    state["unlock_credits"] = credits
    return state


# --- R3 / R4 -------------------------------------------------------------

def get_plan(state, today):
    """Today's plan. It is made once per date and saved so it stays the same all day."""
    _require_level(state)
    key = today.isoformat()
    plan = state["plan"]
    if plan and plan["date"] == key:
        return plan

    start = date.fromisoformat(state["start_date"])
    if daily.is_retelling_day(start, today):
        kind, topic_id, title, prompts = "retelling", None, "再話 Retelling", daily.retelling_chain()
    else:
        topic = daily.pick_topic(content.TOPICS, set(state["unlocked"]), state["topic_counts"])
        kind, topic_id, title, prompts = "topic", topic["id"], topic["title"], daily.prompt_chain(topic)

    plan = {
        "date": key,
        "kind": kind,
        "topic_id": topic_id,
        "title": title,
        "prompts": prompts,
        "new_grammar": [g["id"] for g in grammar.new_points(content.GRAMMAR, state["level"], state["srs"])],
        "review_grammar": grammar.due_reviews(state["srs"], today),
        "graded": [],
    }
    state["plan"] = plan
    return plan


# --- R5 / R6 -------------------------------------------------------------

def finish_session(state, today, seconds, grammar_used, words, recording=None, source=None):
    """Score a finished speaking session and update the state. Returns what the learner earned."""
    plan = get_plan(state, today)
    key = today.isoformat()

    minutes = session.split_minutes(state["level"], seconds, state["day_minutes"].get(key, 0))
    state["day_minutes"][key] = minutes["day_total"]

    # R4: grade each of today's points once per day. Ticks for other points are ignored.
    used = set(grammar_used)
    to_grade = [g for g in plan["new_grammar"] + plan["review_grammar"] if g not in plan["graded"]]
    passed = []
    for gid in to_grade:
        card = state["srs"].get(gid) or grammar.new_card(today)
        ok = gid in used
        state["srs"][gid] = grammar.review(card, ok, today)
        if ok:
            passed.append(gid)
    plan["graded"].extend(to_grade)

    fresh = progress.new_unique_words(state["words"], words)
    saved_words = [
        {"word": w["word"].strip(), "meaning": (w.get("meaning") or "").strip(), "added": key}
        for w in fresh
    ]
    state["words"].extend(saved_words)

    xp = progress.session_xp(minutes["base"], minutes["bonus"], len(passed), len(saved_words))
    level_before = progress.level_for_xp(state["xp"])
    state["xp"] += xp["total"]
    level_after = progress.level_for_xp(state["xp"])
    credits = level_after - level_before
    state["unlock_credits"] += credits

    state["streak"] = progress.update_streak(state["streak"], today, minutes["qualifies"])

    if plan["kind"] == "topic":
        tid = plan["topic_id"]
        state["topic_counts"][tid] = state["topic_counts"].get(tid, 0) + 1

    state["sessions"].append({
        "date": key,
        "kind": plan["kind"],
        "topic_id": plan["topic_id"],
        "title": plan["title"],
        "seconds": int(seconds),
        "minutes": minutes["counted"],
        "xp": xp["total"],
        "grammar_used": passed,
        "words": [w["word"] for w in saved_words],
        "recording": recording,
        "source": source,
    })

    return {
        "xp": xp,
        "minutes": minutes,
        "qualified": minutes["qualifies"],
        "streak": progress.current_streak(state["streak"], today),
        "level_before": level_before,
        "level_after": level_after,
        "credits_gained": credits,
        "new_words": [w["word"] for w in saved_words],
    }


def summary(state, today):
    """Everything the page needs to draw the dashboard."""
    unlocked = set(state["unlocked"])
    can_unlock = tree.unlockable(content.TOPICS, unlocked)
    nodes = []
    for t in content.TOPICS:
        status = "unlocked" if t["id"] in unlocked else (
            "unlockable" if t["id"] in can_unlock else "locked")
        nodes.append({"id": t["id"], "title": t["title"], "tier": t["tier"],
                      "requires": t["requires"], "status": status,
                      "count": state["topic_counts"].get(t["id"], 0)})

    has_level = bool(state["level"])
    plan = get_plan(state, today) if has_level else None
    grammar_by_id = {g["id"]: g for g in content.GRAMMAR}
    lp = progress.level_progress(state["xp"])
    return {
        "jlpt": state["level"],
        "levels": list(levels.LEVELS),
        "xp": state["xp"],
        "level": lp["level"],
        "level_into": lp["into"],
        "level_needed": lp["needed"],
        "streak": progress.current_streak(state["streak"], today),
        "minutes_today": state["day_minutes"].get(today.isoformat(), 0),
        "min_minutes": session.min_minutes(state["level"]) if has_level else None,
        "max_minutes": session.MAX_DAILY_MINUTES,
        "unlock_credits": state["unlock_credits"],
        "unlockable": can_unlock,
        "tree": nodes,
        "plan": plan,
        "grammar": {gid: grammar_by_id[gid] for gid in
                    (plan["new_grammar"] + plan["review_grammar"] if plan else [])
                    if gid in grammar_by_id},
        "word_count": len(state["words"]),
    }
