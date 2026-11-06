
import sqlite3
import hashlib
import json
import os
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent
DB = ROOT / "pathpilot_coding.db"
MODEL = "gemini-3.1-flash-lite"


def connection():
    con = sqlite3.connect(DB, timeout=20)
    con.execute("PRAGMA busy_timeout=20000")

    con.execute("""
        CREATE TABLE IF NOT EXISTS pp_progress (
            student TEXT NOT NULL,
            module TEXT NOT NULL,
            item TEXT NOT NULL,
            value INTEGER NOT NULL DEFAULT 0,
            updated TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(student, module, item)
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS pp_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            module TEXT NOT NULL,
            topic TEXT NOT NULL,
            correct INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS pp_ai_cache (
            prompt_hash TEXT PRIMARY KEY,
            response TEXT NOT NULL,
            created TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()
    return con


def save_progress(student, module, item, value):
    with connection() as con:
        con.execute("""
            INSERT INTO pp_progress(student,module,item,value)
            VALUES(?,?,?,?)
            ON CONFLICT(student,module,item)
            DO UPDATE SET
                value=excluded.value,
                updated=CURRENT_TIMESTAMP
        """, (student, module, item, int(value)))


def load_progress(student, module):
    with connection() as con:
        rows = con.execute("""
            SELECT item,value FROM pp_progress
            WHERE student=? AND module=?
        """, (student, module)).fetchall()

    return {k: v for k, v in rows}


def save_result(student, module, topic, correct, total):
    with connection() as con:
        con.execute("""
            INSERT INTO pp_results
            (student,module,topic,correct,total)
            VALUES(?,?,?,?,?)
        """, (student, module, topic, correct, total))


def load_results(student, module=None):
    with connection() as con:
        if module:
            rows = con.execute("""
                SELECT topic,correct,total,created
                FROM pp_results
                WHERE student=? AND module=?
                ORDER BY id DESC
            """, (student, module)).fetchall()
        else:
            rows = con.execute("""
                SELECT topic,correct,total,created
                FROM pp_results
                WHERE student=?
                ORDER BY id DESC
            """, (student,)).fetchall()

    return rows


def gemini_key():
    key = os.getenv("GEMINI_API_KEY", "")

    if key:
        return key.strip()

    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return ""


def ask_gemini(prompt, max_tokens=700):
    prompt = str(prompt)[:7000]

    prompt_hash = hashlib.sha256(
        (MODEL + prompt).encode("utf-8")
    ).hexdigest()

    with connection() as con:
        cached = con.execute("""
            SELECT response FROM pp_ai_cache
            WHERE prompt_hash=?
        """, (prompt_hash,)).fetchone()

    if cached:
        return cached[0], "cached"

    key = gemini_key()

    if not key:
        return None, "Gemini API key is not configured."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent"
    )

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens
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
            timeout=35
        )

        if response.status_code == 429:
            return None, (
                "Gemini quota exhausted. "
                "Saved practice features remain available."
            )

        if response.status_code != 200:
            return None, (
                f"Gemini unavailable (HTTP {response.status_code}). "
                "Try again later."
            )

        data = response.json()
        candidates = data.get("candidates", [])

        if not candidates:
            return None, "Gemini returned no response."

        parts = candidates[0].get(
            "content", {}
        ).get("parts", [])

        answer = "\n".join(
            p.get("text", "") for p in parts
        ).strip()

        if not answer:
            return None, "Gemini returned an empty response."

        with connection() as con:
            con.execute("""
                INSERT OR REPLACE INTO pp_ai_cache
                (prompt_hash,response)
                VALUES(?,?)
            """, (prompt_hash, answer))

        return answer, "generated"

    except requests.RequestException:
        return None, "Gemini connection failed."


def student_input():
    student = st.text_input(
        "Student ID",
        value="demo_student"
    ).strip()

    if not student:
        st.warning("Enter a Student ID.")
        st.stop()

    return student


def ai_panel(prompt, button_label, key):
    if st.button(button_label, key=key):
        with st.spinner("Gemini is preparing your response..."):
            answer, status = ask_gemini(prompt)

        st.session_state["ai_" + key] = (
            answer, status
        )

    if "ai_" + key in st.session_state:
        answer, status = st.session_state["ai_" + key]

        if answer:
            st.markdown(answer)
            if status == "cached":
                st.caption("Loaded from saved AI response.")
        else:
            st.warning(status)
