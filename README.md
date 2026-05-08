# 📄 AI-Powered Resume Keyword Matcher

An AI-powered ATS (Applicant Tracking System) built using FastAPI, Streamlit, NLP, and Machine Learning to match resumes with job descriptions using TF-IDF, semantic similarity, and skill gap analysis.

---

# 🚀 Features

✅ Resume vs Job Description Matching  
✅ ATS Score Calculation  
✅ TF-IDF Similarity Analysis  
✅ Semantic Similarity using Sentence Transformers  
✅ Skill Extraction & Gap Analysis  
✅ Multi-Resume Ranking System  
✅ CSV Export of Results  
✅ Interactive Dashboard & Charts  
✅ SQLite Database for Persistent Storage  
✅ FastAPI Backend + Streamlit Frontend  

---

# 🧠 Tech Stack

## Frontend
- Streamlit
- Matplotlib
- Pandas

## Backend
- FastAPI
- Uvicorn
- Requests

## NLP & Machine Learning
- Scikit-learn (TF-IDF)
- Sentence Transformers
- NLTK

## Database
- SQLite

---

# 📂 Project Structure

```bash
resume-keyword-matcher/
│
├── app.py
├── api.py
├── database.py
├── requirements.txt
├── README.md
│
├── utils/
│   ├── parser.py
│   ├── preprocess.py
│   ├── similarity.py
│   ├── embeddings.py
│   ├── skills.py
│
├── outputs/
│
└── resumes.db
