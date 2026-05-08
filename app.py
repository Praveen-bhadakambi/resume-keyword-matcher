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
    progress_bar = st.progress(0)
    status_text = st.empty()

    with st.spinner("🔄 Initializing processing..."):

        total_files = len(resumes)
        processed = 0

        for file in resumes:
            try:
                # Update progress
                status_text.text(f"📄 Processing {file.name}... ({processed+1}/{total_files})")

                # Extract text
                text = extract_text(file)

                # API call with increased timeout
                response = requests.post(
                    API_URL,
                    json={"resume": text, "jd": jd},
                    timeout=120  # Increased from 10 to 120 seconds
                )

                if response.status_code != 200:
                    st.error(f"❌ API error for {file.name}: {response.status_code}")
                    processed += 1
                    progress_bar.progress(processed / total_files)
                    continue

                result = response.json()

                # Handle partial results gracefully
                ats_score = result.get("ats", 0)
                tfidf_score = result.get("tfidf", 0)
                semantic_score = result.get("semantic", 0)
                matched_skills = result.get("matched_skills", [])
                missing_skills = result.get("missing_skills", [])
                predicted_role = result.get("predicted_role", "Unknown")
                ai_feedback = result.get("ai_feedback", "AI feedback not available")
                processing_time = result.get("processing_time", 0)

                results.append({
                    "name": file.name,
                    "ats": ats_score,
                    "tfidf": tfidf_score,
                    "semantic": semantic_score,
                    "matched": matched_skills,
                    "missing": missing_skills,
                    "role": predicted_role,
                    "ai_feedback": ai_feedback,
                    "time": processing_time
                })

                # Show success for this file
                st.success(f"✅ {file.name} processed in {processing_time:.1f}s")

            except requests.exceptions.Timeout:
                st.error(f"⏰ Timeout processing {file.name} (took >120s)")
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Connection error for {file.name} - check if backend is running")
            except Exception as e:
                st.error(f"❌ Error processing {file.name}: {str(e)}")

            finally:
                processed += 1
                progress_bar.progress(processed / total_files)

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # =========================
    # ✅ RESULTS DISPLAY
    # =========================
    if results:

        # 🔥 SORT by ATS score
        results = sorted(results, key=lambda x: x["ats"], reverse=True)

        # 🏆 Ranking Table
        st.subheader("🏆 Resume Ranking")

        # Create summary table
        summary_data = []
        for i, r in enumerate(results, 1):
            summary_data.append({
                "Rank": i,
                "Resume": r['name'],
                "ATS Score": f"{r['ats']:.1f}%",
                "TF-IDF": f"{r['tfidf']:.1f}%",
                "Semantic": f"{r['semantic']:.1f}%",
                "Processing Time": f"{r['time']:.1f}s"
            })

        st.table(summary_data)

        # =========================
        # 📊 DETAILED RESULTS
        # =========================
        st.subheader("📊 Detailed Analysis")

        for r in results:
            with st.expander(f"📄 {r['name']} - ATS: {r['ats']:.1f}%"):

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("TF-IDF Similarity", f"{r['tfidf']:.1f}%")
                    st.metric("Semantic Similarity", f"{r['semantic']:.1f}%")
                    st.metric("Predicted Role", r['role'])

                with col2:
                    st.metric("Processing Time", f"{r['time']:.1f}s")

                    if r['matched']:
                        st.success(f"✅ Matched Skills ({len(r['matched'])})")
                        st.write(", ".join(r['matched'][:10]))  # Show first 10

                    if r['missing']:
                        st.warning(f"⚠️ Missing Skills ({len(r['missing'])})")
                        st.write(", ".join(r['missing'][:10]))  # Show first 10

                # AI Feedback (if available)
                if "AI feedback temporarily unavailable" not in r['ai_feedback']:
                    st.subheader("🤖 AI Feedback")
                    st.info(r['ai_feedback'])
                else:
                    st.warning("🤖 AI feedback was not available for this resume")

        # =========================
        # 📊 CHARTS
        # =========================
        st.subheader("📊 Resume Charts")

        names = [r["name"] for r in results]
        scores = [r["ats"] for r in results]

        fig, ax = plt.subplots()
        ax.bar(names, scores, color="#4caf50")
        ax.set_xlabel("Resumes")
        ax.set_ylabel("ATS Score")
        ax.set_title("Resume Ranking")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

        # =========================
        # 📊 TOP RESUME ANALYSIS
        # =========================
        top = results[0]

        st.subheader("📊 Top Resume Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("TF-IDF", f"{top['tfidf']:.1f}%")
            st.metric("Matched Skills", len(top['matched']))

        with col2:
            st.metric("Semantic", f"{top['semantic']:.1f}%")
            st.metric("Missing Skills", len(top['missing']))

        st.metric("ATS Score", f"{top['ats']:.1f}%")

        if top["matched"]:
            st.success(f"Matched Skills: {', '.join(top['matched'][:10])}")
        else:
            st.warning("No matched skills found")

        if top["missing"]:
            st.error(f"Missing Skills: {', '.join(top['missing'][:10])}")
        else:
            st.success("No missing skills 🎉")

        labels = ["TF-IDF", "Semantic", "ATS"]
        values = [top["tfidf"], top["semantic"], top["ats"]]

        fig2, ax2 = plt.subplots()
        ax2.bar(labels, values, color=["#2196f3", "#ff9800", "#4caf50"])
        ax2.set_ylim(0, 100)
        ax2.set_title("Top Resume Performance")
        st.pyplot(fig2)

        # =========================
        # 📥 CSV EXPORT
        # =========================
        df = pd.DataFrame([{
            "Resume": r["name"],
            "ATS_Score": r["ats"],
            "TFIDF_Score": r["tfidf"],
            "Semantic_Score": r["semantic"],
            "Predicted_Role": r["role"],
            "Matched_Skills": ", ".join(r["matched"]),
            "Missing_Skills": ", ".join(r["missing"]),
            "AI_Feedback": r["ai_feedback"],
            "Processing_Time_s": r["time"]
        } for r in results])

        st.download_button(
            label="📥 Download Results as CSV",
            data=df.to_csv(index=False),
            file_name="resume_analysis_results.csv",
            mime="text/csv"
        )

        # =========================
        # 🕒 HISTORY DASHBOARD
        # =========================
        st.subheader("🕒 History Dashboard")
        history = load_history()
        if history:
            history_df = pd.DataFrame(history, columns=["id", "resume_name", "ats", "tfidf", "semantic"])
            st.table(history_df)
        else:
            st.info("No history available yet.")

    else:
        st.error("❌ No resumes were successfully processed. Check the errors above.")

else:
    st.info("📤 Please upload resumes and paste a job description to get started.")


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