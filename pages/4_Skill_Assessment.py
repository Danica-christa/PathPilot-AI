
import streamlit as st
from collections import defaultdict

from pathpilot_extra import (
    student_input,
    save_result,
    load_results,
    ai_panel
)

st.set_page_config(
    page_title="Skill Assessment | PathPilot AI",
    page_icon="📊",
    layout="wide"
)

BANK = [
    ("Python", "Which Python type is mutable?",
     ["tuple", "list", "str", "int"], "list",
     "A list can be changed after creation."),

    ("Python", "What is len([2, 4, 6])?",
     ["2", "3", "6", "12"], "3",
     "The list contains three elements."),

    ("Python", "What does a set remove?",
     ["All numbers", "Duplicates", "Strings", "Indexes"],
     "Duplicates",
     "A set stores unique elements."),

    ("Java", "Which keyword creates an object?",
     ["class", "new", "static", "void"], "new",
     "The new keyword creates a class instance."),

    ("Java", "Method overriding is associated with?",
     ["Polymorphism", "Encapsulation", "Sorting", "Indexing"],
     "Polymorphism",
     "Overriding is an example of runtime polymorphism."),

    ("OOP", "Which concept hides implementation details?",
     ["Inheritance", "Abstraction", "Iteration", "Compilation"],
     "Abstraction",
     "Abstraction exposes essential behavior while hiding details."),

    ("SQL", "Which command retrieves rows?",
     ["INSERT", "UPDATE", "SELECT", "DELETE"], "SELECT",
     "SELECT retrieves records from database tables."),

    ("DBMS", "Which key uniquely identifies a row?",
     ["Foreign Key", "Primary Key", "Index", "View"],
     "Primary Key",
     "A primary key uniquely identifies each record."),

    ("Machine Learning", "Which is a classification algorithm?",
     ["K-Means", "PCA", "Decision Tree Classifier", "SVD"],
     "Decision Tree Classifier",
     "Decision Tree Classifier predicts discrete class labels."),

    ("Machine Learning", "What is overfitting?",
     ["Learning training noise too closely",
      "Removing all features",
      "Perfect generalization",
      "Increasing dataset size"],
     "Learning training noise too closely",
     "An overfit model learns training-specific patterns and may generalize poorly."),

    ("Data Structures", "Which structure uses FIFO?",
     ["Stack", "Queue", "Tree", "Graph"], "Queue",
     "FIFO means first in, first out."),

    ("Data Structures", "Binary search has which time complexity?",
     ["O(n)", "O(n²)", "O(log n)", "O(2^n)"],
     "O(log n)",
     "Binary search halves the search interval each step.")
]

st.title("📊 PathPilot AI | Skill Assessment")
st.write(
    "Evaluate your technical knowledge, identify weak "
    "topics and receive personalized recommendations."
)

student = student_input()

if "skill_test" not in st.session_state:
    st.session_state.skill_test = False

if "skill_done" not in st.session_state:
    st.session_state.skill_done = False

if "skill_answers" not in st.session_state:
    st.session_state.skill_answers = {}

if "skill_test_id" not in st.session_state:
    st.session_state.skill_test_id = 0

history = load_results(student, "technical_assessment")

st.subheader("📈 Previous Performance")

if history:
    total_correct = sum(r[1] for r in history)
    total_questions = sum(r[2] for r in history)

    accuracy = (
        total_correct / total_questions * 100
        if total_questions else 0
    )

    a, b, c = st.columns(3)

    a.metric("Tests Completed", len(history))
    b.metric("Questions Answered", total_questions)
    c.metric("Overall Accuracy", f"{accuracy:.1f}%")
else:
    st.info("Complete your first technical assessment.")

if st.button("🚀 Start New Assessment", type="primary"):
    st.session_state.skill_test = True
    st.session_state.skill_done = False
    st.session_state.skill_answers = {}
    st.session_state.skill_test_id += 1
    st.session_state.skill_student = student
    st.rerun()

if st.session_state.skill_test:
    if st.session_state.get("skill_student") != student:
        st.warning("Start a new test for this Student ID.")
        st.stop()

    st.divider()
    st.subheader("📝 Technical Knowledge Test")

    with st.form(
        f"skill_form_{st.session_state.skill_test_id}"
    ):
        answers = {}

        for i, q in enumerate(BANK):
            topic, question, options, correct, explanation = q

            st.markdown(f"**Q{i + 1}. {question}**")
            st.caption(topic)

            answers[i] = st.radio(
                "Choose one",
                options,
                index=None,
                key=f"skill_{st.session_state.skill_test_id}_{i}"
            )

        submitted = st.form_submit_button(
            "📊 Submit Assessment",
            disabled=st.session_state.skill_done
        )

    if submitted and not st.session_state.skill_done:
        st.session_state.skill_answers = answers
        st.session_state.skill_done = True

        grouped = defaultdict(
            lambda: {"correct": 0, "total": 0}
        )

        for i, q in enumerate(BANK):
            topic = q[0]
            correct_answer = q[3]

            grouped[topic]["total"] += 1

            if answers[i] == correct_answer:
                grouped[topic]["correct"] += 1

        for topic, data in grouped.items():
            save_result(
                student,
                "technical_assessment",
                topic,
                data["correct"],
                data["total"]
            )

        st.rerun()

    if st.session_state.skill_done:
        answers = st.session_state.skill_answers

        correct = sum(
            answers.get(i) == q[3]
            for i, q in enumerate(BANK)
        )

        total = len(BANK)
        score = correct / total * 100

        st.subheader("🎯 Your Assessment Results")

        a, b, c = st.columns(3)
        a.metric("Score", f"{score:.1f}%")
        b.metric("Correct", correct)
        c.metric("Incorrect / Unanswered", total - correct)

        st.progress(score / 100)

        grouped = defaultdict(
            lambda: {"correct": 0, "total": 0}
        )

        for i, q in enumerate(BANK):
            topic = q[0]
            grouped[topic]["total"] += 1

            if answers.get(i) == q[3]:
                grouped[topic]["correct"] += 1

        st.subheader("📚 Topic-wise Performance")

        weak_topics = []

        for topic, data in sorted(grouped.items()):
            accuracy = (
                data["correct"] / data["total"] * 100
            )

            st.write(
                f"**{topic}:** "
                f"{data['correct']}/{data['total']} "
                f"({accuracy:.0f}%)"
            )

            st.progress(accuracy / 100)

            if accuracy < 70:
                weak_topics.append(topic)

        st.subheader("📖 Answer Review")

        for i, q in enumerate(BANK):
            with st.expander(
                f"Q{i + 1}: {q[1]}"
            ):
                st.write(
                    "Your answer:",
                    answers.get(i) or "Not answered"
                )
                st.write("Correct answer:", q[3])
                st.write("Explanation:", q[4])

        st.divider()
        st.subheader("✨ Gemini Skill Improvement Coach")

        weak = ", ".join(weak_topics)

        if not weak:
            weak = "Advanced technical interview preparation"

        prompt = f"""
You are a technical placement interview mentor.

A fresher completed a technical assessment.
Score: {correct}/{total}
Weak topics: {weak}

Create:
1. A simple explanation of what to revise
2. A five-day learning roadmap
3. Two practice activities for each weak topic
4. Common technical interview questions
5. A short revision checklist

Do not invent assessment results.
Keep explanations beginner-friendly.
"""

        ai_panel(
            prompt,
            "✨ Generate My AI Learning Plan",
            f"skill_ai_{student}_{correct}_{weak}"
        )

st.divider()
st.caption(
    "Assessment results are saved locally. "
    "This short diagnostic is not a comprehensive "
    "measure of technical proficiency."
)
