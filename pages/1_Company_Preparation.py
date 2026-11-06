
import streamlit as st

from pathpilot_extra import (
    student_input,
    load_progress,
    save_progress,
    ai_panel
)

st.set_page_config(
    page_title="Company Preparation | PathPilot AI",
    page_icon="🏢",
    layout="wide"
)

COMPANIES = {
    "Tech Mahindra": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Verbal Ability",
        "Arrays and Strings",
        "Java / Python",
        "OOP and DBMS",
        "Project Explanation"
    ],
    "TCS": [
        "Number System",
        "Percentages",
        "Time and Work",
        "Logical Reasoning",
        "Programming Fundamentals",
        "Arrays and Strings",
        "Interview Preparation"
    ],
    "Infosys": [
        "Quantitative Aptitude",
        "Logical Puzzles",
        "Pseudocode",
        "Arrays",
        "Strings",
        "Programming Fundamentals",
        "Communication"
    ],
    "Cognizant": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Verbal Ability",
        "Java / Python",
        "SQL",
        "OOP",
        "Project Discussion"
    ],
    "HCLTech": [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Verbal Ability",
        "Arrays and Strings",
        "OOP",
        "DBMS",
        "Interview Preparation"
    ],
    "KPIT": [
        "Arrays and Strings",
        "OOP",
        "Operating Systems",
        "Computer Networks",
        "DBMS",
        "Aptitude",
        "Project Explanation"
    ],
    "General Placement": [
        "Arrays",
        "Strings",
        "Searching and Sorting",
        "Quantitative Aptitude",
        "Logical Reasoning",
        "SQL",
        "Mock Interviews"
    ]
}

st.title("🏢 Company Preparation")
st.write(
    "Build a structured preparation plan for your "
    "target placement company."
)

student = student_input()

company = st.selectbox(
    "Select Target Company",
    list(COMPANIES)
)

st.caption(
    "Topics are suggested preparation areas, "
    "not verified official recruitment patterns."
)

topics = COMPANIES[company]
module = "company_" + company

progress = load_progress(student, module)

completed = sum(
    progress.get(topic, 0) for topic in topics
)

total = len(topics)
percentage = completed / total * 100

c1, c2, c3 = st.columns(3)

c1.metric("Preparation Topics", total)
c2.metric("Completed", completed)
c3.metric("Progress", f"{percentage:.0f}%")

st.progress(percentage / 100)

st.divider()
st.subheader("📚 Company Preparation Checklist")

for topic in topics:
    checked = st.checkbox(
        topic,
        value=bool(progress.get(topic, 0)),
        key=f"{student}_{company}_{topic}"
    )

    if checked != bool(progress.get(topic, 0)):
        save_progress(
            student, module, topic, checked
        )
        st.rerun()

st.divider()
st.subheader("📅 Your 7-Day Study Plan")

remaining = [
    topic for topic in topics
    if not progress.get(topic, 0)
]

if remaining:
    for i in range(7):
        topic = remaining[i % len(remaining)]

        with st.container(border=True):
            st.markdown(f"**Day {i + 1}**")
            st.write(topic)
            st.caption(
                "Study the concept, solve practice "
                "questions, and review mistakes."
            )
else:
    st.success(
        "All preparation topics are marked completed!"
    )

st.divider()
st.subheader("✨ Gemini AI Preparation Coach")

weak_topics = ", ".join(remaining[:5])

if not weak_topics:
    weak_topics = "Advanced practice and interview revision"

prompt = f"""
Act as an AI placement preparation mentor.

Target company: {company}
Student preparation topics: {topics}
Topics still incomplete: {weak_topics}

Create a concise, realistic seven-day preparation plan.

Include:
1. Daily topics and activities
2. Coding and aptitude practice
3. Revision priorities
4. Interview preparation
5. A short final-day mock test

Do not claim knowledge of official current exam patterns.
Do not invent company recruitment details.
Keep the plan suitable for a fresher.
"""

ai_panel(
    prompt,
    "✨ Generate AI Study Plan",
    f"company_{student}_{company}_{weak_topics}"
)

st.divider()
st.subheader("🚀 Start Practising")

left, right = st.columns(2)

with left:
    if st.button(
        "💻 Coding Practice",
        use_container_width=True
    ):
        st.switch_page(
            "pages/2_Coding_Practice.py"
        )

with right:
    if st.button(
        "🧠 Aptitude Practice",
        use_container_width=True
    ):
        st.switch_page(
            "pages/3_Aptitude_Practice.py"
        )
