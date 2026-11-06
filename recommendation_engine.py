
import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).resolve().parent / "pathpilot_coding.db"


def connect():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.execute("""
        CREATE TABLE IF NOT EXISTS coding_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            question_name TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            correct INTEGER NOT NULL,
            used_hint INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    return con


def history(student_id):
    with connect() as con:
        rows = con.execute("""
            SELECT question_name, topic, difficulty,
                   correct, used_hint, created_at
            FROM coding_attempts
            WHERE student_id = ?
            ORDER BY id DESC
        """, (student_id,)).fetchall()

    return [
        {
            "question": r[0],
            "topic": r[1],
            "difficulty": r[2],
            "correct": bool(r[3]),
            "used_hint": bool(r[4]),
            "date": r[5]
        }
        for r in rows
    ]


def save_lab_attempt(
    student_id,
    question_name,
    question,
    success,
    used_hint=False
):
    if not student_id.strip():
        raise ValueError("Student ID is required.")

    with connect() as con:
        con.execute("""
            INSERT INTO coding_attempts
            (student_id, question_name, topic, difficulty,
             correct, used_hint)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            question_name,
            question["topic"],
            question["difficulty"],
            int(success),
            int(used_hint)
        ))
        con.commit()


def get_skill_states(student_id, questions, initial_scores=None):
    attempts = history(student_id)
    initial_scores = initial_scores or {}

    topics = sorted({
        q["topic"] for q in questions.values()
    })

    states = {}

    for topic in topics:
        topic_attempts = [
            a for a in attempts
            if a["topic"] == topic
        ]

        total = len(topic_attempts)
        correct = sum(a["correct"] for a in topic_attempts)

        by_question = defaultdict(list)

        for attempt in topic_attempts:
            by_question[attempt["question"]].append(attempt)

        question_results = []

        for question_name, records in by_question.items():
            passed = any(a["correct"] for a in records)

            question_results.append({
                "name": question_name,
                "passed": passed,
                "attempts": len(records),
                "difficulty": records[0]["difficulty"],
                "used_hint": any(a["used_hint"] for a in records)
            })

        unique_questions = len(question_results)

        solved = sum(
            1 for q in question_results if q["passed"]
        )

        if unique_questions > 0:
            score = round(
                100 * solved / unique_questions
            )
        else:
            score = initial_scores.get(topic)

        if score is not None:
            score = max(0, min(100, float(score)))

        if unique_questions == 0:
            if score is None:
                level = "Not Assessed"
            else:
                level = "Easy"

        elif unique_questions < 3:
            level = "Easy"

        elif score >= 85 and solved >= 5:
            level = "Hard"

        elif score >= 70 and solved >= 3:
            level = "Medium"

        else:
            level = "Easy"

        states[topic] = {
            "score": score,
            "level": level,
            "attempts": total,
            "correct": correct,
            "unique_questions": unique_questions,
            "solved": solved,
            "failed_questions": unique_questions - solved
        }

    return states


def recommend_from_bank(
    student_id,
    questions,
    initial_scores=None
):
    if not questions:
        return None, "No questions available.", {}

    states = get_skill_states(
        student_id,
        questions,
        initial_scores
    )

    attempts = history(student_id)

    by_question = defaultdict(list)

    for attempt in attempts:
        by_question[attempt["question"]].append(attempt)

    def topic_priority(topic):
        state = states[topic]

        if state["unique_questions"] == 0:
            return (1, 0, topic)

        return (
            0,
            state["score"] if state["score"] is not None else 0,
            state["unique_questions"],
            topic
        )

    topics = sorted(states, key=topic_priority)

    for topic in topics:
        preferred = states[topic]["level"]

        difficulty_order = {
            "Easy": ["Easy", "Medium", "Hard"],
            "Medium": ["Medium", "Easy", "Hard"],
            "Hard": ["Hard", "Medium", "Easy"],
            "Not Assessed": ["Easy", "Medium", "Hard"]
        }[preferred]

        for difficulty in difficulty_order:
            candidates = []

            for name, question in questions.items():
                if question["topic"] != topic:
                    continue

                if question["difficulty"] != difficulty:
                    continue

                previous = by_question[name]

                if any(a["correct"] for a in previous):
                    continue

                candidates.append((
                    len(previous),
                    name
                ))

            if candidates:
                candidates.sort()

                name = candidates[0][1]
                state = states[topic]
                score = state["score"]

                if state["unique_questions"] == 0:
                    reason = (
                        f"Let's assess your {topic} skills "
                        f"with an {difficulty} question."
                    )
                else:
                    reason = (
                        f"Your {topic} score is {score:.0f}%. "
                        f"You have solved "
                        f"{state['solved']} out of "
                        f"{state['unique_questions']} "
                        f"attempted questions. "
                        f"Recommended difficulty: {difficulty}."
                    )

                return name, reason, states

    return (
        None,
        "You've completed all 34 coding questions. "
        "AI-generated personalized practice will be "
        "available after we connect Gemini question generation.",
        states
    )
