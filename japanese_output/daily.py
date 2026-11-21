"""R3: choosing the day's topic, its prompt chain, and retelling days."""

from .content import RETELLING_PROMPTS

TOPIC_STEPS = ("describe", "story", "opinion", "other_side")
RETELLING_STEPS = ("summarize", "details", "reaction", "other_side")
RETELL_EVERY = 4


def is_retelling_day(start_date, today):
    """Every 4th day from the start date (day 4, 8, ...) is a retelling day."""
    return (today - start_date).days % RETELL_EVERY == RETELL_EVERY - 1


def pick_topic(topics, unlocked, topic_counts):
    """Least practiced unlocked topic. On a tie, the higher tier wins, then the lower id."""
    candidates = [t for t in topics if t["id"] in unlocked]
    if not candidates:
        raise ValueError("no unlocked topics")
    return min(candidates, key=lambda t: (topic_counts.get(t["id"], 0), -t["tier"], t["id"]))


def _chain(steps, prompts):
    return [{"step": s, "prompt": prompts[s][0], "en": prompts[s][1]} for s in steps]


def prompt_chain(topic):
    return _chain(TOPIC_STEPS, topic["prompts"])


def retelling_chain():
    return _chain(RETELLING_STEPS, RETELLING_PROMPTS)
