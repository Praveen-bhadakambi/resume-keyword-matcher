import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import requests
import time

from utils.parser import extract_text


# =========================
# 🚀 BACKEND API
# =========================
API_URL = "http://127.0.0.1:8000/match"


# =========================
# 🚀 PAGE CONFIG
# =========================
st.set_page_config(

    page_title="Resume Keyword Matcher",

    page_icon="📄",

    layout="wide"
)


# =========================
# 🚀 TITLE
# =========================
st.title("📄 Resume Keyword Matcher")


# =========================
# 📊 DATABASE FUNCTION
# =========================
def load_history():

    conn = sqlite3.connect("resumes.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM results"
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================
# 📤 INPUT SECTION
# =========================
resumes = st.file_uploader(

    "Upload Resumes",

    type=["pdf", "docx", "txt"],

    accept_multiple_files=True
)

jd = st.text_area(
    "Paste Job Description"
)


# =========================
# 🚀 MAIN PROCESSING
# =========================
if resumes and jd:

    results = []

    st.info(
        "ATS scoring and AI analysis are running..."
    )

    with st.spinner("Processing resumes..."):

        for file in resumes:

            start_time = time.time()

            text = extract_text(file)

            try:

                # =========================
                # 🚀 API REQUEST
                # =========================
                response = requests.post(

                    API_URL,

                    json={
                        "resume": text,
                        "jd": jd
                    },

                    # ✅ FIXED TIMEOUT
                    timeout=300
                )

                processing_time = round(
                    time.time() - start_time,
                    2
                )

                if response.status_code != 200:

                    st.error(
                        f"API error for {file.name}"
                    )

                    continue

                result = response.json()

                # =========================
                # ✅ STORE RESULTS
                # =========================
                results.append({

                    "name": file.name,

                    "tfidf": result.get(
                        "tfidf",
                        0
                    ),

                    "semantic": result.get(
                        "semantic",
                        0
                    ),

                    "ats": result.get(
                        "ats",
                        0
                    ),

                    "matched": result.get(
                        "matched_skills",
                        []
                    ),

                    "missing": result.get(
                        "missing_skills",
                        []
                    ),

                    "role": result.get(
                        "predicted_role",
                        ""
                    ),

                    "feedback": result.get(
                        "ai_feedback",
                        ""
                    ),

                    "rewrite": result.get(
                        "resume_rewrite",
                        ""
                    ),

                    "ats_tips": result.get(
                        "ats_tips",
                        ""
                    ),

                    "time": processing_time
                })

                st.success(
                    f"✅ {file.name} processed in "
                    f"{processing_time}s"
                )

            # =========================
            # ⏰ TIMEOUT ERROR
            # =========================
            except requests.exceptions.Timeout:

                st.error(
                    f"⏰ Timeout processing "
                    f"{file.name}"
                )

            # =========================
            # 🔌 CONNECTION ERROR
            # =========================
            except requests.exceptions.ConnectionError:

                st.error(
                    "🔌 Backend connection failed.\n"
                    "Make sure FastAPI server is running."
                )

            # =========================
            # ❌ GENERAL ERROR
            # =========================
            except Exception as e:

                st.error(
                    f"❌ Error processing "
                    f"{file.name}: {str(e)}"
                )

    # =========================
    # ✅ RESULTS DISPLAY
    # =========================
    if results:

        # =========================
        # 🔥 SORT RESULTS
        # =========================
        results = sorted(

            results,

            key=lambda x: x["ats"],

            reverse=True
        )

        # =========================
        # 🏆 RANKING TABLE
        # =========================
        st.subheader("🏆 Resume Ranking")

        ranking_df = pd.DataFrame(results)

        st.dataframe(

            ranking_df[
                [
                    "name",
                    "ats",
                    "tfidf",
                    "semantic",
                    "time"
                ]
            ],

            use_container_width=True
        )

        # =========================
        # 📊 CHART
        # =========================
        st.subheader("📊 Resume Charts")

        names = [
            r["name"]
            for r in results
        ]

        scores = [
            r["ats"]
            for r in results
        ]

        fig, ax = plt.subplots()

        ax.bar(
            names,
            scores
        )

        ax.set_xlabel("Resume")

        ax.set_ylabel("ATS Score")

        ax.set_title(
            "Resume ATS Ranking"
        )

        st.pyplot(fig)

        # =========================
        # 🏆 TOP RESUME
        # =========================
        top = results[0]

        st.subheader(
            "📊 Top Resume Analysis"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "TF-IDF Similarity",
                f"{top['tfidf']}%"
            )

            st.metric(
                "Matched Skills",
                len(top["matched"])
            )

        with col2:

            st.metric(
                "Semantic Similarity",
                f"{top['semantic']}%"
            )

            st.metric(
                "Missing Skills",
                len(top["missing"])
            )

        st.metric(
            "ATS Score",
            f"{top['ats']}%"
        )

        # =========================
        # 🧠 ROLE PREDICTION
        # =========================
        st.subheader(
            "🧠 Predicted Job Role"
        )

        st.success(top["role"])

        # =========================
        # ✅ MATCHED SKILLS
        # =========================
        st.subheader(
            "✅ Matched Skills"
        )

        if top["matched"]:

            st.success(
                ", ".join(
                    top["matched"]
                )
            )

        else:

            st.warning(
                "No matched skills found"
            )

        # =========================
        # ⚠️ MISSING SKILLS
        # =========================
        st.subheader(
            "⚠️ Missing Skills"
        )

        if top["missing"]:

            st.error(
                ", ".join(
                    top["missing"]
                )
            )

        else:

            st.success(
                "No missing skills 🎉"
            )

        # =========================
        # 🤖 AI RESUME SUGGESTIONS
        # =========================
        st.subheader(
            "🤖 AI Resume Suggestions"
        )

        st.info(top["feedback"])

        # =========================
        # ✍️ RESUME REWRITE
        # =========================
        st.subheader(
            "✍️ Professional Resume Rewrite"
        )

        st.success(top["rewrite"])

        # =========================
        # 🎯 ATS TIPS
        # =========================
        st.subheader(
            "🎯 ATS Optimization Tips"
        )

        st.warning(top["ats_tips"])

        # =========================
        # 📥 CSV EXPORT
        # =========================
        csv_df = pd.DataFrame(results)

        st.download_button(

            label="📥 Download Results as CSV",

            data=csv_df.to_csv(index=False),

            file_name="resume_results.csv",

            mime="text/csv"
        )

    else:

        st.error(
            "No resumes were successfully processed."
        )


# =========================
# 📊 HISTORY DASHBOARD
# =========================
st.subheader("🕒 History Dashboard")

if st.button("Load History"):

    data = load_history()

    if data:

        df = pd.DataFrame(

            data,

            columns=[
                "ID",
                "Resume",
                "ATS",
                "TFIDF",
                "Semantic"
            ]
        )

        st.dataframe(df)

        # =========================
        # 📈 HISTORY CHART
        # =========================
        fig, ax = plt.subplots()

        ax.plot(df["ATS"])

        ax.set_title(
            "ATS Score Trend"
        )

        st.pyplot(fig)

    else:

        st.warning(
            "No data found in database"
        )