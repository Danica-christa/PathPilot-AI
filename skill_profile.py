
import json
import os

PROFILE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data",
    "skill_profile.json"
)


def save_skill_profile(topic_scores, weak_topics=None):
    os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)

    if weak_topics is None:
        weak_topics = [
            topic for topic, score in topic_scores.items()
            if score < 50
        ]

    profile = {
        "topic_scores": topic_scores,
        "weak_topics": weak_topics
    }

    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)


def load_skill_profile():
    if not os.path.exists(PROFILE_FILE):
        return {
            "topic_scores": {},
            "weak_topics": []
        }

    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as file:
            profile = json.load(file)

        return {
            "topic_scores": profile.get("topic_scores", {}),
            "weak_topics": profile.get("weak_topics", [])
        }

    except (json.JSONDecodeError, OSError):
        return {
            "topic_scores": {},
            "weak_topics": []
        }


def get_recommended_topics(section=None):
    profile = load_skill_profile()
    topic_scores = profile["topic_scores"]

    weak_topics = [
        topic for topic, score in topic_scores.items()
        if score < 50
    ]

    if section == "Coding":
        weak_topics = [
            topic for topic in weak_topics
            if topic.startswith("Coding -")
        ]

    elif section == "Aptitude":
        weak_topics = [
            topic for topic in weak_topics
            if topic.startswith("Aptitude -")
        ]

    elif section in ("Logical Reasoning", "Verbal Ability"):
        weak_topics = [
            topic for topic in weak_topics
            if topic.startswith(section + " -")
        ]

    return weak_topics


def update_skill_scores(new_scores):
    """
    Update selected topic scores without deleting other saved scores.
    """
    profile = load_skill_profile()

    topic_scores = profile["topic_scores"].copy()
    topic_scores.update(new_scores)

    weak_topics = [
        topic for topic, score in topic_scores.items()
        if score < 50
    ]

    save_skill_profile(topic_scores, weak_topics)
