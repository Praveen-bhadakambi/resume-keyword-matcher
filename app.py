import streamlit as st
import requests
from utils.parser import extract_text

st.title("📄 Resume Keyword Matcher")

# Upload multiple resumes
resumes = st.file_uploader(
    "Upload Multiple Resumes",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# Job description input
jd = st.text_area("Paste Job Description")

# 🔥 MAIN LOGIC (API CALL)
if resumes and jd:

    results = []

    for file in resumes:
        text = extract_text(file)

        try:
            # 🔥 Call FastAPI backend
            response = requests.post(
                "http://127.0.0.1:8000/match",
                json={"resume": text, "jd": jd}
            )

            result = response.json()

            results.append({
                "name": file.name,
                "tfidf": result["tfidf"],
                "semantic": result["semantic"],
                "ats": result["ats"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"]
            })

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

    # 🔥 SORT BY ATS SCORE
    results = sorted(results, key=lambda x: x["ats"], reverse=True)

    # 🏆 RANKING
    st.subheader("🏆 Resume Ranking")
    for r in results:
        st.write(f"{r['name']} → ATS: {r['ats']}%")

    # 📊 TOP RESUME ANALYSIS
    if results:
        top = results[0]

        st.subheader("📊 Top Resume Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("TF-IDF", f"{top['tfidf']}%")

        with col2:
            st.metric("Semantic", f"{top['semantic']}%")

        st.metric("ATS Score", f"{top['ats']}%")

        # Skills
        st.success(f"Matched Skills: {top['matched_skills']}")
        st.error(f"Missing Skills: {top['missing_skills']}")