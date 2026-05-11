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

                # Handle partial results gracefully - Extract all available fields
                ats_score = result.get("ats", 0)
                tfidf_score = result.get("tfidf", 0)
                semantic_score = result.get("semantic", 0)
                matched_skills = result.get("matched_skills", [])
                missing_skills = result.get("missing_skills", [])
                predicted_role = result.get("predicted_role", "Unknown")
                skill_match_score = result.get("skill_match_score", 0)
                
                # AI-Generated Features
                ai_feedback = result.get("ai_feedback", "")
                resume_rewrite = result.get("resume_rewrite", "")
                ats_tips = result.get("ats_tips", "")
                skill_suggestions = result.get("skill_suggestions", "")
                action_verbs = result.get("action_verbs", "")
                processing_time = result.get("processing_time", 0)

                results.append({
                    "name": file.name,
                    "ats": ats_score,
                    "tfidf": tfidf_score,
                    "semantic": semantic_score,
                    "matched": matched_skills,
                    "missing": missing_skills,
                    "role": predicted_role,
                    "skill_match_score": skill_match_score,
                    "ai_feedback": ai_feedback,
                    "resume_rewrite": resume_rewrite,
                    "ats_tips": ats_tips,
                    "skill_suggestions": skill_suggestions,
                    "action_verbs": action_verbs,
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
                
                # 1. KEY METRICS
                st.markdown("### 📊 Key Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("ATS Score", f"{r['ats']:.1f}%", delta=f"Skill Match: {r['skill_match_score']:.0f}%")
                    st.metric("TF-IDF Similarity", f"{r['tfidf']:.1f}%")
                
                with col2:
                    st.metric("Semantic Similarity", f"{r['semantic']:.1f}%")
                    st.metric("Processing Time", f"{r['time']:.1f}s")
                
                with col3:
                    st.metric("Predicted Role", r['role'])
                    st.metric("Matched Skills", len(r['matched']))

                st.markdown("---")
                
                # 2. SKILLS ANALYSIS
                st.markdown("### 🎯 Skills Analysis")
                col_skills1, col_skills2 = st.columns(2)
                
                with col_skills1:
                    if r['matched']:
                        st.success(f"✅ Matched Skills ({len(r['matched'])})")
                        matched_text = ", ".join(sorted(r['matched']))
                        st.caption(matched_text)
                    else:
                        st.info("No matched skills yet")

                with col_skills2:
                    if r['missing']:
                        st.error(f"❌ Missing Skills ({len(r['missing'])})")
                        missing_text = ", ".join(sorted(r['missing']))
                        st.caption(missing_text)
                    else:
                        st.success("No missing skills 🎉")
                
                st.markdown("---")
                
                # 3. AI RESUME FEEDBACK
                st.markdown("### 💡 AI Resume Feedback")
                if r['ai_feedback']:
                    st.info(r['ai_feedback'])
                else:
                    st.warning("⏳ Feedback not available")
                
                st.markdown("---")
                
                # 4. ATS OPTIMIZATION TIPS
                st.markdown("### 🎯 ATS Optimization Tips")
                if r['ats_tips']:
                    st.success(r['ats_tips'])
                else:
                    st.warning("⏳ Tips not available")
                
                st.markdown("---")
                
                # 5. RESUME REWRITING
                st.markdown("### ✍️ Professional Resume Rewrite")
                if r['resume_rewrite']:
                    with st.expander("👉 Click to see rewritten resume bullets"):
                        st.code(r['resume_rewrite'], language="markdown")
                else:
                    st.warning("⏳ Rewrite not available")

                st.markdown("---")

                # 6. MISSING SKILL SUGGESTIONS
                st.markdown("### 🎓 Missing Skill Suggestions")
                if r['skill_suggestions']:
                    st.info(r['skill_suggestions'])
                else:
                    st.warning("⏳ Suggestions not available")

                st.markdown("---")

                # 7. ACTION VERBS
                st.markdown("### ✍️ Stronger Action Verbs")
                if r['action_verbs']:
                    st.info(r['action_verbs'])
                else:
                    st.warning("⏳ Verb suggestions not available")

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
        # 🏆 TOP RESUME ANALYSIS
        # =========================
        top = results[0]

        st.subheader("🏆 Top Resume Analysis")

        # Key Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("ATS Score", f"{top['ats']:.1f}%")
            st.metric("TF-IDF Similarity", f"{top['tfidf']:.1f}%")

        with col2:
            st.metric("Semantic Similarity", f"{top['semantic']:.1f}%")
            st.metric("Skill Match", f"{top.get('skill_match_score', 0):.0f}%")

        with col3:
            st.metric("Predicted Role", top['role'])
            st.metric("Processing Time", f"{top['time']:.1f}s")

        # Skills Summary
        col_skills1, col_skills2 = st.columns(2)
        
        with col_skills1:
            if top["matched"]:
                st.success(f"✅ Matched Skills ({len(top['matched'])})")
                matched_skills_text = ", ".join(sorted(top['matched']))
                st.caption(matched_skills_text)
            else:
                st.warning("No matched skills found")

        with col_skills2:
            if top["missing"]:
                st.error(f"❌ Missing Skills ({len(top['missing'])})")
                missing_skills_text = ", ".join(sorted(top['missing']))
                st.caption(missing_skills_text)
            else:
                st.success("No missing skills 🎉")

        # Score Visualization
        labels = ["TF-IDF", "Semantic", "Skill Match", "ATS"]
        values = [top["tfidf"], top["semantic"], top.get("skill_match_score", 0), top["ats"]]

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        colors = ["#2196f3", "#ff9800", "#4caf50", "#f44336"]
        ax2.barh(labels, values, color=colors)
        ax2.set_xlim(0, 100)
        ax2.set_xlabel("Score (%)")
        ax2.set_title("Top Resume - Comprehensive Score Breakdown")
        for i, v in enumerate(values):
            ax2.text(v + 2, i, f"{v:.1f}%", va="center")
        st.pyplot(fig2)

        # AI Features for Top Resume
        st.markdown("---")
        st.subheader("🤖 AI-Powered Insights for Top Resume")
        
        # Resume Feedback
        with st.expander("💡 AI Resume Feedback", expanded=False):
            if top['ai_feedback']:
                st.info(top['ai_feedback'])
            else:
                st.warning("⏳ Generating feedback...")
        
        # ATS Tips
        with st.expander("🎯 ATS Optimization Tips", expanded=False):
            if top['ats_tips']:
                st.success(top['ats_tips'])
            else:
                st.warning("⏳ Generating tips...")
        
        # Resume Rewrite
        with st.expander("✍️ Professional Resume Rewrite", expanded=False):
            if top['resume_rewrite']:
                st.code(top['resume_rewrite'], language="markdown")
                st.info("👆 Use the above stronger bullet points in your resume")
            else:
                st.warning("⏳ Generating rewrite...")

        # Skill Recommendations
        with st.expander("🎓 Missing Skill Suggestions", expanded=False):
            if top.get('skill_suggestions'):
                st.info(top['skill_suggestions'])
            else:
                st.warning("⏳ Generating recommendations...")

        # Action Verbs
        with st.expander("✍️ Stronger Action Verbs", expanded=False):
            if top.get('action_verbs'):
                st.markdown(top['action_verbs'])
            else:
                st.warning("⏳ Generating suggestions...")

        # =========================
        # 📥 CSV EXPORT
        # =========================
        df = pd.DataFrame([{
            "Resume": r["name"],
            "ATS_Score": r["ats"],
            "TF-IDF_Score": r["tfidf"],
            "Semantic_Score": r["semantic"],
            "Skill_Match_Score": r.get("skill_match_score", 0),
            "Predicted_Role": r["role"],
            "Matched_Skills": ", ".join(r["matched"]),
            "Missing_Skills": ", ".join(r["missing"]),
            "AI_Feedback": r.get("ai_feedback", "")[:100],
            "ATS_Tips": r.get("ats_tips", "")[:100],
            "Resume_Rewrite": r.get("resume_rewrite", "")[:100],
            "Skill_Suggestions": r.get("skill_suggestions", "")[:100],
            "Action_Verbs": r.get("action_verbs", "")[:100],
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