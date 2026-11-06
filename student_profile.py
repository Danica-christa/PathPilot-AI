
import streamlit as st
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "pathpilot_coding.db"


def connect():
    con = sqlite3.connect(DB, timeout=20)

    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            department TEXT,
            target_company TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    return con


def save_student(student_id, name, department, company):
    with connect() as con:
        con.execute("""
            INSERT INTO students (
                student_id,
                student_name,
                department,
                target_company
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id)
            DO UPDATE SET
                student_name=excluded.student_name,
                department=excluded.department,
                target_company=excluded.target_company
        """, (
            student_id,
            name,
            department,
            company
        ))


def get_student(student_id):
    with connect() as con:
        row = con.execute("""
            SELECT
                student_id,
                student_name,
                department,
                target_company
            FROM students
            WHERE student_id=?
        """, (student_id,)).fetchone()

    return row


def student_login():
    st.sidebar.divider()
    st.sidebar.subheader("👤 Student Profile")

    student_id = st.sidebar.text_input(
        "Student ID",
        key="pathpilot_student_id"
    ).strip()

    if not student_id:
        st.sidebar.info("Enter your Student ID.")
        return None

    student = get_student(student_id)

    if student:
        st.sidebar.success(
            f"Welcome, {student[1]}!"
        )

        st.session_state["active_student_id"] = student_id

        return student_id

    st.sidebar.write("New Student Registration")

    with st.sidebar.form("student_registration"):
        name = st.text_input("Student Name")

        department = st.selectbox(
            "Department",
            [
                "AIML",
                "CSE",
                "IT",
                "ECE",
                "EEE",
                "Mechanical",
                "Other"
            ]
        )

        company = st.selectbox(
            "Target Company",
            [
                "General Placement",
                "Tech Mahindra",
                "TCS",
                "Infosys",
                "Cognizant",
                "HCLTech",
                "KPIT"
            ]
        )

        register = st.form_submit_button(
            "Create Student Profile"
        )

    if register:
        if not name.strip():
            st.sidebar.error("Enter your name.")
        else:
            save_student(
                student_id,
                name.strip(),
                department,
                company
            )

            st.session_state["active_student_id"] = student_id

            st.rerun()

    return None
