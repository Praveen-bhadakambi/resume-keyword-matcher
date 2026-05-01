import streamlit as st
import requests
from utils.parser import extract_text
import matplotlib.pyplot as plt

# 👉 Replace with your deployed API URL
API_URL = "http://127.0.0.1:8000/match"   # change to Render URL later

st.title("📄 Resume Keyword Matcher")

# Upload resumes
resumes = st.file_uploader(
    "Upload Resumes",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# Job description input
jd = st.text_area("Paste Job Description")

# 🔥 MAIN LOGIC
if resumes and jd:

    results = []

    with st.spinner("Processing resumes..."):

        for file in resumes:
            text = extract_text(file)

            try:
                response = requests.post(
                    API_URL,
                    json={"resume": text, "jd": jd},
                    timeout=10   # ⏱ prevents hanging
                )

                # Check API status
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

    # ⚠️ Ensure results exist
    if results:

        # 🔥 SORT
        results = sorted(results, key=lambda x: x["ats"], reverse=True)

        # 🏆 Ranking
        st.subheader("🏆 Resume Ranking")
        for r in results:
            st.write(f"{r['name']} → ATS: {r['ats']}%")

        # 📊 Top Resume
        top = results[0]

        st.subheader("📊 Top Resume Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("TF-IDF", f"{top['tfidf']}%")

        with col2:
            st.metric("Semantic", f"{top['semantic']}%")

        st.metric("ATS Score", f"{top['ats']}%")

        # Skills
        st.success(f"Matched Skills: {top['matched']}")
        st.error(f"Missing Skills: {top['missing']}")

        # 📊 Chart
        labels = ["TF-IDF", "Semantic", "ATS"]
        values = [top["tfidf"], top["semantic"], top["ats"]]

        fig, ax = plt.subplots()
        ax.bar(labels, values)

        st.pyplot(fig)

    else:
        st.warning("No results generated. Check API or input data.")