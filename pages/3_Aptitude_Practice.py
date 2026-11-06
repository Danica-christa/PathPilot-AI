
import streamlit as st
import sqlite3
import random
import time
import json
import os
import re
import ast
import uuid
import requests

from decimal import Decimal
from pathlib import Path
from collections import defaultdict
from skill_profile import update_skill_scores

st.set_page_config(
    page_title="PathPilot AI - Adaptive Aptitude",
    page_icon="🧠",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parent.parent / "pathpilot_coding.db"
GEMINI_MODEL = "gemini-3.1-flash-lite"

SECTIONS = [
    "Quantitative Aptitude",
    "Logical Reasoning",
    "Verbal Ability"
]

QUANT_TOPICS = [
    "Percentages",
    "Profit and Loss",
    "Ratio and Proportion",
    "Averages",
    "Time and Work",
    "Speed, Time and Distance",
    "Simple and Compound Interest",
    "Probability",
    "Permutations and Combinations",
    "Number System",
    "Data Interpretation",
    "Mixtures"
]


# ==================================================
# DATABASE
# ==================================================

def connect():
    con = sqlite3.connect(DB_PATH, timeout=15)

    con.execute("""
        CREATE TABLE IF NOT EXISTS aptitude_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            section TEXT NOT NULL,
            subtopic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            correct INTEGER NOT NULL,
            answered INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS aptitude_generated (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            question_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    return con


def get_history(student_id):
    with connect() as con:
        rows = con.execute("""
            SELECT question_id, section, subtopic,
                   difficulty, correct, answered, created_at
            FROM aptitude_attempts
            WHERE student_id = ?
            ORDER BY id DESC
        """, (student_id,)).fetchall()

    return [
        {
            "id": r[0],
            "section": r[1],
            "subtopic": r[2],
            "level": r[3],
            "correct": bool(r[4]),
            "answered": bool(r[5]),
            "date": r[6]
        }
        for r in rows
    ]


def save_results(student_id, questions, answers):
    with connect() as con:
        for i, q in enumerate(questions):
            answer = answers.get(str(i))
            answered = answer in q["options"]
            correct = answered and answer == q["answer"]

            con.execute("""
                INSERT INTO aptitude_attempts
                (student_id, question_id, section, subtopic,
                 difficulty, correct, answered)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                q["id"],
                q["topic"],
                q["subtopic"],
                q["level"],
                int(correct),
                int(answered)
            ))

        con.commit()


def save_generated(student_id, questions):
    with connect() as con:
        for q in questions:
            con.execute("""
                INSERT INTO aptitude_generated
                (id, student_id, question_json)
                VALUES (?, ?, ?)
            """, (
                q["id"],
                student_id,
                json.dumps(q, ensure_ascii=False)
            ))

        con.commit()


def get_generated(student_id):
    with connect() as con:
        rows = con.execute("""
            SELECT question_json
            FROM aptitude_generated
            WHERE student_id = ?
            ORDER BY created_at DESC
        """, (student_id,)).fetchall()

    questions = []

    for row in rows:
        try:
            questions.append(json.loads(row[0]))
        except (ValueError, TypeError):
            pass

    return questions


# ==================================================
# ORIGINAL VERIFIED QUESTION BANK
# ==================================================

# Each row contains:
# Section, Subtopic, Difficulty, Question,
# Options, Correct Answer, Explanation

BANK = [
    (
        "Quantitative Aptitude", "Percentages", "Easy",
        "A number is increased by 20% and then decreased by 20%. What is the net change?",
        ["No change", "4% decrease", "4% increase", "2% decrease"],
        "4% decrease",
        "Assume 100. After increasing, it becomes 120. After decreasing, it becomes 96. Net decrease is 4%."
    ),
    (
        "Quantitative Aptitude", "Percentages", "Medium",
        "A student's marks increase from 400 to 460. What is the percentage increase?",
        ["12%", "15%", "20%", "60%"],
        "15%",
        "Increase = 60. Percentage increase = 60/400 × 100 = 15%."
    ),
    (
        "Quantitative Aptitude", "Profit and Loss", "Medium",
        "An article marked at ₹1,500 is sold at a 20% discount. If its cost price is ₹1,000, find the profit percentage.",
        ["10%", "15%", "20%", "25%"],
        "20%",
        "Selling price = 1200. Profit = 200. Profit percentage = 200/1000 × 100 = 20%."
    ),
    (
        "Quantitative Aptitude", "Ratio and Proportion", "Medium",
        "The ratio of A's and B's salaries is 5:7. If each salary increases by ₹4,000, the ratio becomes 3:4. Find A's original salary.",
        ["₹20,000", "₹24,000", "₹28,000", "₹32,000"],
        "₹20,000",
        "Let salaries be 5x and 7x. Then (5x+4000)/(7x+4000)=3/4. So x=4000 and A's salary is ₹20,000."
    ),
    (
        "Quantitative Aptitude", "Averages", "Medium",
        "The average of 8 numbers is 24. If 18 is replaced by 34, what is the new average?",
        ["24", "25", "26", "27"],
        "26",
        "Original total = 192. New total = 192-18+34=208. New average = 208/8 = 26."
    ),
    (
        "Quantitative Aptitude", "Time and Work", "Medium",
        "A can finish a job in 12 days and B in 18 days. How many days will they take together?",
        ["6 days", "7.2 days", "8 days", "9 days"],
        "7.2 days",
        "Combined daily work = 1/12+1/18=5/36. Time = 36/5 = 7.2 days."
    ),
    (
        "Quantitative Aptitude", "Time and Work", "Hard",
        "A and B together complete a job in 10 days. A alone takes 15 days. How long does B alone take?",
        ["20 days", "25 days", "30 days", "35 days"],
        "30 days",
        "B's daily work = 1/10-1/15=1/30. Therefore B needs 30 days."
    ),
    (
        "Quantitative Aptitude", "Speed, Time and Distance", "Medium",
        "A train 180 metres long crosses a pole in 9 seconds. Find its speed in km/h.",
        ["60", "64", "72", "80"],
        "72",
        "Speed = 180/9 = 20 m/s. Convert to km/h: 20 × 18/5 = 72."
    ),
    (
        "Quantitative Aptitude", "Simple and Compound Interest", "Medium",
        "Find the compound interest on ₹10,000 for 2 years at 10% per annum, compounded annually.",
        ["₹2,000", "₹2,100", "₹2,200", "₹1,900"],
        "₹2,100",
        "Amount = 10000 × 1.1 × 1.1 = 12100. Compound interest = ₹2100."
    ),
    (
        "Quantitative Aptitude", "Probability", "Medium",
        "Two fair dice are rolled. What is the probability that their sum is 7?",
        ["1/12", "1/6", "1/9", "1/4"],
        "1/6",
        "Six of the 36 equally likely outcomes have a sum of 7. Probability = 6/36 = 1/6."
    ),
    (
        "Quantitative Aptitude", "Permutations and Combinations", "Medium",
        "How many different arrangements can be made using all letters of CAT?",
        ["3", "6", "9", "12"],
        "6",
        "Three distinct letters can be arranged in 3! = 6 ways."
    ),
    (
        "Quantitative Aptitude", "Number System", "Medium",
        "What is the smallest number greater than 3 that leaves remainder 3 when divided by 5, 6 and 8?",
        ["63", "83", "123", "243"],
        "123",
        "LCM of 5, 6 and 8 is 120. Required number = 120+3 = 123."
    ),
    (
        "Quantitative Aptitude", "Data Interpretation", "Medium",
        "A company hires 120 students in January and 150 in February. What is the percentage increase?",
        ["20%", "25%", "30%", "35%"],
        "25%",
        "Increase = 30. Percentage increase = 30/120 × 100 = 25%."
    ),
    (
        "Quantitative Aptitude", "Mixtures", "Hard",
        "A 30-litre mixture contains milk and water in the ratio 4:1. How much water must be added to make the ratio 2:1?",
        ["3 litres", "5 litres", "6 litres", "10 litres"],
        "6 litres",
        "Milk = 24 litres and water = 6 litres. New water needed = 12 litres. Add 6 litres."
    ),
    (
        "Logical Reasoning", "Number Series", "Medium",
        "Find the next number: 2, 6, 12, 20, 30, __",
        ["40", "42", "44", "46"],
        "42",
        "Differences are 4, 6, 8, 10. Next difference is 12, giving 42."
    ),
    (
        "Logical Reasoning", "Number Series", "Hard",
        "Find the next number: 3, 8, 18, 38, 78, __",
        ["148", "156", "158", "160"],
        "158",
        "Each number is multiplied by 2 and then 2 is added."
    ),
    (
        "Logical Reasoning", "Coding-Decoding", "Medium",
        "If TABLE is coded as UBCMF by moving every letter one step forward, how is CHAIR coded?",
        ["DIBJS", "DIBIR", "DHBJS", "EIBJS"],
        "DIBJS",
        "C becomes D, H becomes I, A becomes B, I becomes J, and R becomes S."
    ),
    (
        "Logical Reasoning", "Blood Relations", "Medium",
        "Pointing to a woman, Ravi says, 'She is the daughter of my mother's only son.' How is the woman related to Ravi?",
        ["Sister", "Daughter", "Mother", "Niece"],
        "Daughter",
        "Ravi's mother's only son is Ravi himself. Therefore the woman is his daughter."
    ),
    (
        "Logical Reasoning", "Directions", "Medium",
        "A person walks 5 km north, 3 km east and 5 km south. Where are they relative to the starting point?",
        ["3 km east", "3 km west", "5 km north", "8 km east"],
        "3 km east",
        "The north and south movements cancel. The person is 3 km east."
    ),
    (
        "Logical Reasoning", "Syllogisms", "Medium",
        "All engineers are graduates. Some graduates are artists. Which conclusion definitely follows?",
        [
            "All engineers are artists",
            "Some engineers are artists",
            "All engineers are graduates",
            "No graduate is an engineer"
        ],
        "All engineers are graduates",
        "This conclusion is directly stated. The other conclusions do not necessarily follow."
    ),
    (
        "Logical Reasoning", "Seating Arrangement", "Hard",
        "Five people P, Q, R, S and T sit in a row. P is left of Q, Q is left of R, S is right of R, and T is right of S. Who sits in the middle?",
        ["P", "Q", "R", "S"],
        "R",
        "The order is P, Q, R, S, T. R is in the middle."
    ),
    (
        "Logical Reasoning", "Odd One Out", "Easy",
        "Choose the odd one out.",
        ["9", "16", "25", "30"],
        "30",
        "9, 16 and 25 are perfect squares. 30 is not."
    ),
    (
        "Logical Reasoning", "Analogy", "Easy",
        "Book is to Reading as Fork is to __.",
        ["Writing", "Eating", "Drawing", "Walking"],
        "Eating",
        "A book is used for reading and a fork is used for eating."
    ),
    (
        "Verbal Ability", "Grammar", "Medium",
        "Choose the grammatically correct sentence.",
        [
            "Neither of the answers are correct.",
            "Neither of the answers is correct.",
            "Neither answers is correct.",
            "Neither of answers are correct."
        ],
        "Neither of the answers is correct.",
        "Neither takes the singular verb 'is' in this sentence."
    ),
    (
        "Verbal Ability", "Vocabulary", "Medium",
        "Choose the closest meaning of 'Meticulous'.",
        ["Careless", "Very careful", "Impatient", "Confused"],
        "Very careful",
        "Meticulous means extremely careful and attentive to detail."
    ),
    (
        "Verbal Ability", "Antonyms", "Easy",
        "Choose the antonym of 'Scarce'.",
        ["Rare", "Limited", "Abundant", "Insufficient"],
        "Abundant",
        "Scarce means limited or in short supply. Abundant means plentiful."
    ),
    (
        "Verbal Ability", "Sentence Correction", "Medium",
        "Choose the correct replacement: 'He has been working here since five years.'",
        [
            "He has been working here for five years.",
            "He is working here since five years.",
            "He has working here for five years.",
            "No correction is needed."
        ],
        "He has been working here for five years.",
        "Use 'for' with a duration and 'since' with a starting point."
    ),
    (
        "Verbal Ability", "Prepositions", "Easy",
        "She is interested ___ learning machine learning.",
        ["on", "at", "in", "for"],
        "in",
        "The correct expression is 'interested in'."
    ),
    (
        "Verbal Ability", "Reading Comprehension", "Medium",
        "Passage: 'Regular practice improves accuracy because learners identify mistakes and correct them.' What is the main idea?",
        [
            "Practice guarantees success.",
            "Practice helps improve accuracy through feedback.",
            "Mistakes should be ignored.",
            "Accuracy is not important."
        ],
        "Practice helps improve accuracy through feedback.",
        "Practice helps learners improve accuracy by identifying and correcting mistakes."
    )
]

QUESTIONS = []

for i, item in enumerate(BANK):
    QUESTIONS.append({
        "id": f"APT_{i + 1:03d}",
        "topic": item[0],
        "subtopic": item[1],
        "level": item[2],
        "q": item[3],
        "options": item[4],
        "answer": item[5],
        "explanation": item[6],
        "source": "Original Bank"
    })


# ==================================================
# SKILL ANALYSIS
# ==================================================

def calculate_skills(attempts):
    grouped = defaultdict(list)

    for a in attempts:
        grouped[(a["section"], a["subtopic"])].append(a)

    skills = {}

    for key, records in grouped.items():
        total = len(records)
        correct = sum(a["correct"] for a in records)

        unique = len(set(a["id"] for a in records))
        score = round(correct / total * 100) if total else 0

        if unique < 3:
            level = "Easy"
            confidence = "Early Estimate"
        elif score >= 85 and unique >= 5:
            level = "Hard"
            confidence = "Established"
        elif score >= 70:
            level = "Medium"
            confidence = "Developing"
        else:
            level = "Easy"
            confidence = "Developing"

        skills[key] = {
            "score": score,
            "level": level,
            "attempts": total,
            "correct": correct,
            "unique": unique,
            "confidence": confidence
        }

    return skills


def get_skill_key(section, subtopic):
    if section == "Quantitative Aptitude":
        return "Aptitude - " + subtopic

    return section + " - " + subtopic


def get_weak_topics(skills):
    return sorted(
        skills.items(),
        key=lambda x: (
            x[1]["score"],
            -x[1]["attempts"]
        )
    )


# ==================================================
# SAFE MATHEMATICAL VERIFICATION
# ==================================================

def evaluate_math(expression):
    if not isinstance(expression, str):
        raise ValueError("Invalid expression")

    if len(expression) > 120:
        raise ValueError("Expression too long")

    tree = ast.parse(expression, mode="eval")

    def solve(node):
        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return Decimal(str(node.value))

        if isinstance(node, ast.UnaryOp):
            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        if isinstance(node, ast.BinOp):
            a = solve(node.left)
            b = solve(node.right)

            if isinstance(node.op, ast.Add):
                return a + b

            if isinstance(node.op, ast.Sub):
                return a - b

            if isinstance(node.op, ast.Mult):
                return a * b

            if isinstance(node.op, ast.Div):
                if b == 0:
                    raise ValueError("Division by zero")
                return a / b

        raise ValueError("Unsupported mathematical expression")

    value = solve(tree.body)

    if not value.is_finite() or abs(value) > Decimal("1000000000000"):
        raise ValueError("Result outside allowed range")

    return value


def parse_number(value):
    if not isinstance(value, str):
        raise ValueError("Answer must be text")

    value = value.strip().replace(",", "")

    if not re.fullmatch(r"-?\d+(\.\d+)?", value):
        raise ValueError("Answer is not a plain number")

    return Decimal(value)


def validate_ai_question(q):
    required = [
        "subtopic",
        "level",
        "q",
        "options",
        "answer",
        "explanation",
        "verification_expression"
    ]

    if not isinstance(q, dict):
        return None

    if any(field not in q for field in required):
        return None

    if q["subtopic"] not in QUANT_TOPICS:
        return None

    if q["level"] not in ["Easy", "Medium", "Hard"]:
        return None

    if not isinstance(q["q"], str) or len(q["q"]) < 20:
        return None

    if not isinstance(q["explanation"], str) or len(q["explanation"]) < 15:
        return None

    options = q["options"]

    if not isinstance(options, list) or len(options) != 4:
        return None

    if any(not isinstance(x, str) for x in options):
        return None

    if len(set(options)) != 4:
        return None

    if q["answer"] not in options:
        return None

    try:
        expected = evaluate_math(q["verification_expression"])
        answer = parse_number(q["answer"])

        if abs(expected - answer) > Decimal("0.000001"):
            return None

        for option in options:
            parse_number(option)

    except (ValueError, ArithmeticError, SyntaxError, TypeError):
        return None

    return {
        "id": "AI_" + uuid.uuid4().hex,
        "topic": "Quantitative Aptitude",
        "subtopic": q["subtopic"],
        "level": q["level"],
        "q": q["q"],
        "options": options,
        "answer": q["answer"],
        "explanation": q["explanation"],
        "source": "Gemini AI - Numerically Verified"
    }


# ==================================================
# GEMINI API
# ==================================================

def get_gemini_key():
    key = os.getenv("GEMINI_API_KEY", "")

    if key:
        return key.strip()

    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except (KeyError, FileNotFoundError):
        return ""


def generate_gemini_questions(subtopic, level, existing):
    key = get_gemini_key()

    if not key:
        return [], "Gemini API key not found in Streamlit secrets."

    examples = [
        q["q"][:120]
        for q in existing
        if q["subtopic"] == subtopic
    ][:8]

    prompt = f"""
You are creating original placement aptitude MCQs.

Generate 5 different quantitative aptitude questions.

Subtopic: {subtopic}
Difficulty: {level}

The questions must be mathematically well-defined,
with exactly one correct numerical answer.

Use four DISTINCT numeric options.
Every option must be a plain numeric string.
Do not include units, commas, currency signs or percent symbols
inside the options.

The question text may describe the required units.

For each question, supply verification_expression.
This expression must independently compute the correct
numerical answer using only numeric constants,
parentheses, +, -, * and /.

The expression must be directly justified by the question.
Do not use variables, functions, powers, factorials,
or Python imports.

Use integer or terminating-decimal answers.
Avoid rounding ambiguity and division by zero.

For example:
Question: What is 20% of 250?
Options: ["40", "50", "60", "70"]
Answer: "50"
verification_expression: "250*20/100"

Avoid these existing questions:
{json.dumps(examples, ensure_ascii=False)}

Return ONLY a JSON array.

Each object must contain:
subtopic
level
q
options
answer
explanation
verification_expression

Use the exact requested subtopic and level.
Do not include markdown or code fences.
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 3000,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(
            url,
            headers={
                "x-goog-api-key": key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            try:
                message = response.json().get(
                    "error", {}
                ).get("message", "Unknown API error")
            except ValueError:
                message = "Unknown API error"

            return [], (
                f"Gemini API returned HTTP "
                f"{response.status_code}: {message}"
            )

        result = response.json()

        parts = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [])
        )

        text = "".join(
            p.get("text", "") for p in parts
        )

        text = text.strip()

        if text.startswith("```"):
            text = re.sub(
                r"^```(?:json)?\s*",
                "",
                text
            )
            text = re.sub(r"\s*```$", "", text)

        generated = json.loads(text)

        if not isinstance(generated, list):
            return [], "Gemini returned an unexpected format."

        valid = []
        seen = set()

        existing_texts = {
            q["q"].strip().lower() for q in existing
        }

        for item in generated:
            q = validate_ai_question(item)

            if q is None:
                continue

            if q["subtopic"] != subtopic:
                continue

            if q["level"] != level:
                continue

            normalized = q["q"].strip().lower()

            if normalized in existing_texts:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            valid.append(q)

        if not valid:
            return [], (
                "Gemini responded, but none of the questions "
                "passed numerical validation. Try again."
            )

        return valid, None

    except requests.RequestException as e:
        return [], f"Gemini connection error: {e}"

    except (ValueError, KeyError, IndexError, TypeError):
        return [], (
            "Gemini returned an incomplete or invalid response. "
            "Please try again."
        )


# ==================================================
# ADAPTIVE QUESTION SELECTION
# ==================================================

def select_questions(bank, count, skills, attempts, adaptive):
    if not adaptive:
        return random.sample(bank, min(count, len(bank)))

    counts = defaultdict(int)
    solved = set()

    for a in attempts:
        counts[a["id"]] += 1

        if a["correct"]:
            solved.add(a["id"])

    def priority(q):
        state = skills.get((q["topic"], q["subtopic"]))

        if state is None:
            topic_rank = 1
            score = 50
            desired = "Easy"
        else:
            score = state["score"]
            desired = state["level"]
            topic_rank = 0 if score < 70 else 2

        if q["id"] in solved:
            repeat_rank = 2
        elif counts[q["id"]] == 0:
            repeat_rank = 0
        else:
            repeat_rank = 1

        difficulty_rank = (
            0 if q["level"] == desired else 1
        )

        return (
            topic_rank,
            repeat_rank,
            score,
            difficulty_rank,
            counts[q["id"]],
            random.random()
        )

    return sorted(bank, key=priority)[:count]


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "apt_started": False,
    "apt_submitted": False,
    "apt_questions": [],
    "apt_answers": {},
    "apt_start": None,
    "apt_duration": 0,
    "apt_saved": False,
    "apt_student": "",
    "apt_mode": "",
    "apt_test_id": "",
    "apt_filter_section": "All"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# PAGE
# ==================================================

st.title("🧠 PathPilot AI | Adaptive Aptitude Practice")

st.write(
    "Personalized aptitude preparation with skill-gap analysis, "
    "Gemini-generated numerical questions and progress tracking."
)

student_id = st.text_input(
    "Enter Student ID",
    value="demo_student"
).strip()

if not student_id:
    st.warning("Please enter a Student ID.")
    st.stop()

if (
    st.session_state.apt_started
    and st.session_state.apt_student != student_id
):
    st.session_state.apt_started = False
    st.session_state.apt_submitted = False
    st.session_state.apt_questions = []
    st.session_state.apt_answers = {}

attempts = get_history(student_id)
skills = calculate_skills(attempts)

generated_questions = get_generated(student_id)
all_questions = QUESTIONS + generated_questions


# ==================================================
# DASHBOARD
# ==================================================

st.subheader("📊 Your Aptitude Dashboard")

total = len(attempts)
correct = sum(a["correct"] for a in attempts)
accuracy = correct / total * 100 if total else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Attempts", total)
c2.metric("Correct", correct)
c3.metric("Accuracy", f"{accuracy:.1f}%")
c4.metric("AI Questions", len(generated_questions))

st.subheader("🎯 Personalized Skill Gaps")

if skills:
    for (section_name, subtopic), data in get_weak_topics(skills):
        st.write(
            f"**{subtopic}** ({section_name}) — "
            f"{data['score']}% | "
            f"Difficulty: {data['level']} | "
            f"Attempts: {data['attempts']} | "
            f"{data['confidence']}"
        )
else:
    st.info(
        "No aptitude attempts saved yet. "
        "Complete an initial assessment to identify skill gaps."
    )


# ==================================================
# GEMINI QUESTION GENERATION
# ==================================================

st.divider()
st.subheader("✨ Gemini Personalized Question Generator")

st.write(
    "Generate additional numerical aptitude questions "
    "for your weak topics. Generated answers are checked "
    "mathematically before being added to your practice bank."
)

quant_skills = [
    (key, data)
    for key, data in get_weak_topics(skills)
    if key[0] == "Quantitative Aptitude"
]

if quant_skills:
    suggested_topic = quant_skills[0][0][1]
else:
    suggested_topic = "Percentages"

topic_index = QUANT_TOPICS.index(suggested_topic)

ai_topic = st.selectbox(
    "Aptitude topic",
    QUANT_TOPICS,
    index=topic_index
)

suggested_level = skills.get(
    ("Quantitative Aptitude", ai_topic),
    {}
).get("level", "Easy")

ai_level = st.selectbox(
    "Question difficulty",
    ["Easy", "Medium", "Hard"],
    index=["Easy", "Medium", "Hard"].index(suggested_level)
)

if st.button("✨ Generate Personalized Questions"):
    with st.spinner("Gemini is generating and validating questions..."):
        new_questions, error = generate_gemini_questions(
            ai_topic,
            ai_level,
            all_questions
        )

    if error:
        st.warning(error)

    if new_questions:
        save_generated(student_id, new_questions)

        st.success(
            f"{len(new_questions)} new validated questions "
            f"added to your aptitude bank!"
        )

        st.rerun()

st.caption(
    "AI-generated numerical answers are verified against a "
    "calculation expression. This does not independently prove "
    "that every question's wording or explanation is correct."
)


# ==================================================
# TEST SETTINGS
# ==================================================

st.divider()
st.subheader("📝 Start Aptitude Test")

st.sidebar.header("Aptitude Test Settings")

company = st.sidebar.selectbox(
    "Preparation goal",
    [
        "General Placement",
        "TCS-style Practice",
        "Cognizant-style Practice",
        "Infosys-style Practice",
        "KPIT-style Practice",
        "Tech Mahindra-style Practice",
        "HCLTech-style Practice"
    ]
)

section = st.sidebar.selectbox(
    "Section",
    ["All"] + SECTIONS
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["All", "Easy", "Medium", "Hard"]
)

mode = st.sidebar.selectbox(
    "Mode",
    ["Personalized Practice", "Timed Mock Test"]
)

source = st.sidebar.selectbox(
    "Question source",
    [
        "All Questions",
        "Original Bank",
        "Gemini AI"
    ]
)

filtered = []

for q in all_questions:
    if section != "All" and q["topic"] != section:
        continue

    if difficulty != "All" and q["level"] != difficulty:
        continue

    if source == "Original Bank" and q["source"] != "Original Bank":
        continue

    if source == "Gemini AI" and q["source"] == "Original Bank":
        continue

    filtered.append(q)

st.caption(
    f"Preparation goal: {company}. "
    "Company labels are practice goals, not verified official questions."
)

if not filtered:
    st.warning(
        "No questions match these filters. "
        "Change the filters or generate new Gemini questions."
    )
    st.stop()

count = st.select_slider(
    "Number of questions",
    options=[5, 10, 15, 20, 25],
    value=10
)

count = min(count, len(filtered))
duration = count * 60

x, y, z = st.columns(3)

x.metric("Available Questions", len(filtered))
y.metric("Selected Questions", count)
z.metric("Time Limit", f"{duration // 60} min")

if st.button("🚀 Start / Restart Test", type="primary"):
    selected = select_questions(
        filtered,
        count,
        skills,
        attempts,
        mode == "Personalized Practice"
    )

    st.session_state.apt_questions = selected
    st.session_state.apt_answers = {}
    st.session_state.apt_started = True
    st.session_state.apt_submitted = False
    st.session_state.apt_start = time.time()
    st.session_state.apt_duration = duration
    st.session_state.apt_saved = False
    st.session_state.apt_student = student_id
    st.session_state.apt_mode = mode
    st.session_state.apt_test_id = uuid.uuid4().hex

    st.rerun()

if not st.session_state.apt_started:
    st.info("Choose your settings and start a test.")
    st.stop()


# ==================================================
# TEST QUESTIONS
# ==================================================

questions = st.session_state.apt_questions
active_mode = st.session_state.apt_mode

st.divider()
st.header("📚 Your Aptitude Test")

if active_mode == "Timed Mock Test":
    elapsed = int(time.time() - st.session_state.apt_start)

    remaining = max(
        0,
        st.session_state.apt_duration - elapsed
    )

    if not st.session_state.apt_submitted:
        st.subheader(
            f"⏱️ Remaining: "
            f"{remaining // 60:02d}:{remaining % 60:02d}"
        )

        if remaining == 0:
            st.session_state.apt_submitted = True
            st.warning("Time is up. Your test has ended.")

for i, q in enumerate(questions):
    st.markdown(f"### Question {i + 1}")

    st.caption(
        f"{q['topic']} · {q['subtopic']} · "
        f"{q['level']} · {q['source']}"
    )

    st.write(q["q"])

    key = f"apt_choice_{st.session_state.apt_test_id}_{i}"

    saved_answer = st.session_state.apt_answers.get(str(i))

    if key not in st.session_state:
        st.session_state[key] = saved_answer

    selected = st.radio(
        "Choose your answer",
        q["options"],
        index=None,
        key=key,
        disabled=st.session_state.apt_submitted
    )

    if not st.session_state.apt_submitted:
        st.session_state.apt_answers[str(i)] = selected

    if st.session_state.apt_submitted:
        answer = st.session_state.apt_answers.get(str(i))

        if answer == q["answer"]:
            st.success("Correct answer!")
        else:
            st.error(f"Correct answer: {q['answer']}")

        st.info("Explanation: " + q["explanation"])

    st.divider()


# ==================================================
# SUBMIT TEST
# ==================================================

if not st.session_state.apt_submitted:
    if st.button("📊 Submit Test", type="primary"):
        st.session_state.apt_submitted = True
        st.rerun()

else:
    total = len(questions)

    correct = sum(
        st.session_state.apt_answers.get(str(i)) == q["answer"]
        for i, q in enumerate(questions)
    )

    attempted = sum(
        st.session_state.apt_answers.get(str(i)) in q["options"]
        for i, q in enumerate(questions)
    )

    wrong = attempted - correct
    unanswered = total - attempted
    score = correct / total * 100 if total else 0

    if not st.session_state.apt_saved:
        save_results(
            student_id,
            questions,
            st.session_state.apt_answers
        )

        new_history = get_history(student_id)
        new_skills = calculate_skills(new_history)

        scores = {}

        for (section_name, subtopic), data in new_skills.items():
            scores[get_skill_key(section_name, subtopic)] = data["score"]

        if scores:
            update_skill_scores(scores)

        st.session_state.apt_saved = True

        st.success("Your aptitude performance has been saved!")

    st.header("📈 Test Results")

    a, b, c, d = st.columns(4)

    a.metric("Score", f"{score:.1f}%")
    b.metric("Correct", f"{correct}/{total}")
    c.metric("Wrong", wrong)
    d.metric("Unanswered", unanswered)

    st.progress(score / 100)

    if score >= 80:
        st.success("Great performance! Try a harder level.")
    elif score >= 60:
        st.info("Good attempt. Review your incorrect answers.")
    else:
        st.warning(
            "Focus on your weak topics and practise again."
        )

    st.subheader("📊 Subtopic Performance")

    grouped = defaultdict(list)

    for i, q in enumerate(questions):
        grouped[(q["topic"], q["subtopic"])].append((i, q))

    for (section_name, subtopic), items in sorted(grouped.items()):
        sub_correct = sum(
            st.session_state.apt_answers.get(str(i)) == q["answer"]
            for i, q in items
        )

        sub_total = len(items)
        sub_score = sub_correct / sub_total * 100

        st.write(
            f"**{subtopic}** — "
            f"{sub_correct}/{sub_total} "
            f"({sub_score:.0f}%)"
        )

        st.progress(sub_score / 100)

    st.subheader("📖 Review Your Answers")

    for i, q in enumerate(questions):
        with st.expander(f"Q{i + 1}: {q['q']}"):
            answer = st.session_state.apt_answers.get(str(i))

            st.write("Your answer:", answer or "Not answered")
            st.write("Correct answer:", q["answer"])
            st.write("Explanation:", q["explanation"])

    if st.button("🔄 Start Another Test"):
        st.session_state.apt_started = False
        st.session_state.apt_submitted = False
        st.session_state.apt_questions = []
        st.session_state.apt_answers = {}
        st.session_state.apt_saved = False
        st.rerun()


# ==================================================
# STUDENT HISTORY
# ==================================================

st.divider()
st.subheader("📜 Your Aptitude History")

history = get_history(student_id)

if history:
    total_attempts = len(history)
    total_correct = sum(a["correct"] for a in history)

    overall = 100 * total_correct / total_attempts

    a, b, c = st.columns(3)

    a.metric("Total Questions", total_attempts)
    b.metric("Correct Answers", total_correct)
    c.metric("Overall Accuracy", f"{overall:.1f}%")

    current_skills = calculate_skills(history)

    st.subheader("🎯 Current Skill Levels")

    for (section_name, subtopic), data in get_weak_topics(current_skills):
        st.write(
            f"**{subtopic}** ({section_name}) — "
            f"{data['score']}% | "
            f"Level: {data['level']} | "
            f"Attempts: {data['attempts']} | "
            f"Confidence: {data['confidence']}"
        )

else:
    st.info("No aptitude history available yet.")

st.caption(
    "PathPilot AI | Adaptive Aptitude Practice | "
    "Original question bank + validated Gemini numerical questions"
)
