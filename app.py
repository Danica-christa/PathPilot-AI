
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from skill_profile import load_skill_profile

st.set_page_config(
    page_title="PathPilot AI | Placement Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------
# DESIGN
# -----------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #11182b, #17132c);
    color: #f8fafc;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #101729;
    border-right: 1px solid #293653;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #f8fafc !important;
}

.hero {
    padding: 35px;
    border-radius: 22px;
    background: linear-gradient(120deg, #202044, #32215b, #164e63);
    border: 1px solid #514579;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    color: white;
    margin-bottom: 12px;
}

.hero-text {
    font-size: 16px;
    color: #e2e8f0;
    line-height: 1.7;
}

.feature-card {
    background: #171f35;
    border: 1px solid #293653;
    border-radius: 15px;
    padding: 22px;
    min-height: 150px;
    margin-bottom: 15px;
}

.feature-title {
    font-size: 19px;
    font-weight: 700;
    color: #c4b5fd;
    margin-bottom: 10px;
}

.feature-text {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.6;
}

div[data-testid="stMetric"] {
    background: #171f35;
    border: 1px solid #293653;
    border-radius: 14px;
    padding: 15px;
}

div[data-testid="stMetricValue"] {
    color: #c4b5fd;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}

div[data-testid="stForm"] {
    border: 1px solid #293653;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------
# LOAD MODEL
# -----------------------------------------------

@st.cache_resource
def load_model():
    path = BASE_DIR / "placement_model.pkl"

    if not path.exists():
        return None

    return joblib.load(path)


try:
    model = load_model()
except Exception as e:
    model = None
    st.error(f"Could not load placement model: {e}")


# -----------------------------------------------
# SIDEBAR
# -----------------------------------------------

with st.sidebar:
    st.title("🎓 PathPilot AI")
    st.caption("AI-POWERED PLACEMENT INTELLIGENCE")

    st.divider()

    st.markdown("### Platform Features")

    st.write("🏠 Placement Prediction")
    st.write("🏢 Company Preparation")
    st.write("💻 Coding Practice")
    st.write("🧠 Aptitude Practice")
    st.write("📊 Skill Assessment")
    st.write("🏆 Quest Mode")
    st.write("🚀 Adaptive Coding")

    st.divider()

    st.markdown("### Machine Learning Model")
    st.write("**Algorithm:** Random Forest")
    st.write("**Previously measured accuracy:** 78.34%")
    st.write("**Dataset records:** 7,225")

    st.caption(
        "Academic prototype. Model predictions are "
        "estimates, not guarantees of placement."
    )


# -----------------------------------------------
# HERO
# -----------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-title">
        🎓 PathPilot AI
    </div>
    <div class="hero-text">
        Your AI-powered placement preparation companion.
        Predict placement readiness, identify skill gaps,
        practise coding and aptitude, and track your
        progress towards becoming placement-ready.
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------
# PLATFORM OVERVIEW
# -----------------------------------------------

st.header("🚀 Your Placement Preparation Platform")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🎯 Placement Prediction</div>
        <div class="feature-text">
            Estimate placement readiness using academic
            performance, aptitude and skill-related inputs.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💻 Coding Practice</div>
        <div class="feature-text">
            Practise programming problems, evaluate solutions
            and receive AI-assisted explanations.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 Adaptive Aptitude</div>
        <div class="feature-text">
            Practise aptitude questions, receive Gemini-generated
            questions and track topic-wise performance.
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------
# STUDENT PROFILE
# -----------------------------------------------

st.divider()

st.header("🧑‍🎓 Student Placement Prediction")

st.write(
    "Enter your academic and skill information to "
    "estimate placement readiness."
)

with st.form("placement_form"):

    left, right = st.columns(2)

    with left:
        cgpa = st.number_input(
            "CGPA",
            min_value=0.0,
            max_value=10.0,
            value=8.0,
            step=0.1
        )

        internships = st.number_input(
            "Number of Internships",
            min_value=0,
            max_value=20,
            value=1
        )

        projects = st.number_input(
            "Number of Projects",
            min_value=0,
            max_value=30,
            value=2
        )

        certifications = st.number_input(
            "Workshops / Certifications",
            min_value=0,
            max_value=50,
            value=2
        )

        aptitude = st.slider(
            "Aptitude Test Score",
            0,
            100,
            65
        )

    with right:
        soft_skills = st.slider(
            "Soft Skills Rating",
            0,
            10,
            7
        )

        extracurricular = st.selectbox(
            "Extracurricular Activities",
            ["No", "Yes"]
        )

        training = st.selectbox(
            "Placement Training Completed",
            ["No", "Yes"]
        )

        ssc = st.number_input(
            "10th Percentage",
            min_value=0.0,
            max_value=100.0,
            value=85.0
        )

        hsc = st.number_input(
            "12th Percentage",
            min_value=0.0,
            max_value=100.0,
            value=80.0
        )

    submitted = st.form_submit_button(
        "🔍 Predict Placement Readiness",
        type="primary",
        use_container_width=True
    )


# -----------------------------------------------
# PREDICTION
# -----------------------------------------------

if submitted:

    if model is None:
        st.error(
            "Placement model is unavailable. "
            "Check that placement_model.pkl exists."
        )

    else:
        # Match the original model's 10 input features.
        # Binary values follow the 0/1 dataset convention.

        
        data = pd.DataFrame([{
            "CGPA": cgpa,
            "Internships": internships,
            "Projects": projects,
            "Workshops/Certifications": certifications,
            "AptitudeTestScore": aptitude,
            "SoftSkillsRating": soft_skills,
            "ExtracurricularActivities": extracurricular,
            "PlacementTraining": training,
            "SSC_Marks": ssc,
            "HSC_Marks": hsc
        }])


        try:
            prediction = model.predict(data)[0]

            st.subheader("📊 Placement Prediction Result")

            result = str(prediction).lower()

            if result in ["1", "placed", "yes", "true"]:
                st.success(
                    "🎉 Prediction: Likely to be placed"
                )
            else:
                st.warning(
                    "📚 Prediction: May need further preparation"
                )

            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(data)[0]

                classes = list(model.classes_)

                placed_index = None

                for i, cls in enumerate(classes):
                    if str(cls).lower() in [
                        "1", "placed", "yes", "true"
                    ]:
                        placed_index = i
                        break

                if placed_index is not None:
                    probability = float(
                        probabilities[placed_index]
                    ) * 100

                    st.metric(
                        "Model Estimated Placement Probability",
                        f"{probability:.1f}%"
                    )

                    st.progress(probability / 100)

            st.caption(
                "This estimate reflects the trained model "
                "and its dataset. It is not a guaranteed "
                "placement outcome."
            )

            st.subheader("🎯 Personalized Recommendations")

            recommendations = []

            if aptitude < 70:
                recommendations.append(
                    "Improve aptitude through regular "
                    "quantitative and reasoning practice."
                )

            if projects < 2:
                recommendations.append(
                    "Build additional practical projects "
                    "and practise explaining them."
                )

            if internships == 0:
                recommendations.append(
                    "Gain practical experience through "
                    "internships or real-world projects."
                )

            if soft_skills < 7:
                recommendations.append(
                    "Practise communication, self-introduction "
                    "and mock interview questions."
                )

            if certifications < 2:
                recommendations.append(
                    "Strengthen relevant technical skills "
                    "through focused courses and practice."
                )

            if training == "No":
                recommendations.append(
                    "Complete structured placement preparation "
                    "and practise timed mock assessments."
                )

            if not recommendations:
                recommendations.append(
                    "Continue coding, aptitude practice "
                    "and interview preparation."
                )

            for item in recommendations:
                st.write("✅ " + item)

            st.info(
                "Use Coding Practice and Aptitude Practice "
                "to work on your preparation goals."
            )

        except Exception as e:
            st.error(
                "Prediction could not be completed. "
                "The model's expected feature names or "
                f"input formats may differ: {e}"
            )


# -----------------------------------------------
# SKILL PROFILE
# -----------------------------------------------

st.divider()

st.header("📈 Skill Development Dashboard")

try:
    profile = load_skill_profile()

    if isinstance(profile, dict) and profile:
        numeric_scores = {
            str(k): float(v)
            for k, v in profile.items()
            if isinstance(v, (int, float))
            and not isinstance(v, bool)
        }

        if numeric_scores:
            skill_df = pd.DataFrame(
                {
                    "Skill": list(numeric_scores.keys()),
                    "Score": list(numeric_scores.values())
                }
            )

            st.bar_chart(
                skill_df.set_index("Skill")
            )

            st.caption(
                "These scores come from the saved skill profile."
            )
        else:
            st.info(
                "Complete practice activities to build "
                "your skill profile."
            )
    else:
        st.info(
            "No skill profile data available yet."
        )

except Exception:
    st.info(
        "Skill profile is not available yet. "
        "You can continue using Coding and Aptitude Practice."
    )


# -----------------------------------------------
# QUICK NAVIGATION
# -----------------------------------------------

st.divider()

st.header("🧭 Explore PathPilot AI")

st.write(
    "Select a module to continue your placement preparation."
)

pages = [
    (
        "🏢 Company Preparation",
        "pages/1_Company_Preparation.py"
    ),
    (
        "💻 Coding Practice",
        "pages/2_Coding_Practice.py"
    ),
    (
        "🧠 Aptitude Practice",
        "pages/3_Aptitude_Practice.py"
    ),
    (
        "📊 Skill Assessment",
        "pages/4_Skill_Assessment.py"
    ),
    (
        "🏆 Quest Mode",
        "pages/5_Quest_Mode.py"
    ),
    (
        "🚀 Adaptive Coding",
        "pages/6_Adaptive_Coding.py"
    )
]

for start in range(0, len(pages), 3):
    columns = st.columns(3)

    for col, (label, path) in zip(
        columns,
        pages[start:start + 3]
    ):
        with col:
            if (BASE_DIR / path).exists():
                if st.button(
                    label,
                    key="nav_" + path,
                    use_container_width=True
                ):
                    st.switch_page(path)
            else:
                st.button(
                    label,
                    disabled=True,
                    key="nav_" + path,
                    use_container_width=True
                )


# -----------------------------------------------
# FOOTER
# -----------------------------------------------

st.divider()

st.caption(
    "PathPilot AI | Student Placement Prediction "
    "& Skill-Gap Analysis | "
    "Python • Streamlit • Scikit-learn • Gemini AI"
)

# ==========================================
# PATHPILOT AI - LIGHT THEME FIX
# ==========================================

st.markdown("""
<style>

/* Main application background */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F8FAFF !important;
    color: #172033 !important;
}

/* Main content text */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] span {
    color: #172033;
}

/* Sidebar background */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: #FFFFFF !important;
}

/* Sidebar text */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #172033 !important;
}

/* Sidebar navigation */
[data-testid="stSidebarNav"] a {
    color: #172033 !important;
    border-radius: 9px;
}

/* Sidebar hover */
[data-testid="stSidebarNav"] a:hover {
    background: #EDEBFF !important;
}

/* Input fields */
input,
textarea,
[data-baseweb="input"],
[data-baseweb="select"],
[data-baseweb="textarea"] {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border-color: #D7DEEB !important;
}

/* Input placeholders */
input::placeholder,
textarea::placeholder {
    color: #64748B !important;
}

/* Streamlit form containers */
[data-testid="stForm"] {
    background: #FFFFFF !important;
    border: 1px solid #E1E7F0 !important;
    border-radius: 14px !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E1E7F0 !important;
    border-radius: 12px !important;
    padding: 15px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E1E7F0 !important;
    border-radius: 10px !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #172033 !important;
}

/* Dividers */
hr {
    border-color: #E1E7F0 !important;
}

/* Buttons */
.stButton button[kind="primary"] {
    background: #635BDB !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* Header toolbar */
[data-testid="stHeader"] {
    background: #F8FAFF !important;
}

</style>
""", unsafe_allow_html=True)

