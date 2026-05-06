import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import requests
from utils.parser import extract_text

# 👉 Backend API URL
API_URL = "http://127.0.0.1:8000/match"

st.title("📄 Resume Keyword Matcher")

# =========================
# 📊 DATABASE FUNCTION
# =========================
def load_history():
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")
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

jd = st.text_area("Paste Job Description")


# =========================
# 🔥 MAIN LOGIC
# =========================
if resumes and jd:

    results = []

    with st.spinner("Processing resumes..."):

        for file in resumes:
            text = extract_text(file)

            try:
                response = requests.post(
                    API_URL,
                    json={"resume": text, "jd": jd},
                    timeout=10
                )

                if response.status_code != 200:
                    st.error(f"API error for {file.name}")
                    continue

                result = response.json()

                results.append({
                    "name": file.name,
                    "tfidf": result.get("tfidf", 0),
                    "semantic": result.get("semantic", 0),
                    "ats": result.get("ats", 0),
                    "matched": result.get("matched_skills", []),
                    "missing": result.get("missing_skills", [])
                })

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

    # =========================
    # ✅ RESULTS DISPLAY
    # =========================
    if results:

        # 🔥 SORT
        results = sorted(results, key=lambda x: x["ats"], reverse=True)

        # 🏆 Ranking
        st.subheader("🏆 Resume Ranking")
        for r in results:
            st.write(f"{r['name']} → ATS: {r['ats']}%")

        # =========================
        # 📥 CSV EXPORT
        # =========================
        df = pd.DataFrame(results)

        st.download_button(
            label="📥 Download Results as CSV",
            data=df.to_csv(index=False),
            file_name="resume_results.csv",
            mime="text/csv"
        )

        # =========================
        # 📊 MULTI-RESUME CHART
        # =========================
        names = [r["name"] for r in results]
        scores = [r["ats"] for r in results]

        fig, ax = plt.subplots()
        ax.bar(names, scores)
        ax.set_xlabel("Resumes")
        ax.set_ylabel("ATS Score")
        ax.set_title("Resume Ranking")

        st.pyplot(fig)

        # =========================
        # 📊 TOP RESUME ANALYSIS
        # =========================
        top = results[0]

        st.subheader("📊 Top Resume Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("TF-IDF", f"{top['tfidf']}%")

        with col2:
            st.metric("Semantic", f"{top['semantic']}%")

        st.metric("ATS Score", f"{top['ats']}%")

        # =========================
        # 🎯 SKILLS DISPLAY (FIXED)
        # =========================
        if top["matched"]:
            st.success(f"Matched Skills: {', '.join(top['matched'])}")
        else:
            st.warning("No matched skills found")

        if top["missing"]:
            st.error(f"Missing Skills: {', '.join(top['missing'])}")
        else:
            st.success("No missing skills 🎉")

        # =========================
        # 📊 TOP RESUME CHART
        # =========================
        labels = ["TF-IDF", "Semantic", "ATS"]
        values = [top["tfidf"], top["semantic"], top["ats"]]

        fig2, ax2 = plt.subplots()
        ax2.bar(labels, values)

        st.pyplot(fig2)

    else:
        st.warning("No results generated. Check API or input data.")


# =========================
# 📊 HISTORY DASHBOARD
# =========================
st.subheader("📊 History Dashboard")

if st.button("Load History"):

    data = load_history()

    if data:
        df = pd.DataFrame(data, columns=[
            "ID", "Resume", "ATS", "TFIDF", "Semantic"
        ])

        st.dataframe(df)

        # 📈 Trend chart
        fig, ax = plt.subplots()
        ax.plot(df["ATS"])
        ax.set_title("ATS Score Trend")

        st.pyplot(fig)

    else:
        st.warning("No data found in database")