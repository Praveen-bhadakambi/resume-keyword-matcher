# 📄 AI Resume Keyword Matcher

An AI-powered Resume Analysis and ATS Optimization platform built using FastAPI, Streamlit, NLP, Semantic Similarity, and Ollama LLM.

This project helps candidates optimize resumes for Applicant Tracking Systems (ATS) by analyzing resume content against job descriptions using AI and NLP techniques.

---

# 🚀 Features

## ✅ ATS Resume Scoring
Calculates ATS score using:
- TF-IDF similarity
- Semantic similarity
- Skill matching percentage

## ✅ Semantic Resume Analysis
Uses Sentence Transformers and cosine similarity to compare resume and job description semantically.

## ✅ AI Resume Suggestions
Generates intelligent resume improvement suggestions using Llama3.

## ✅ AI Resume Rewrite
Creates stronger professional resume bullet points.

## ✅ ATS Optimization Tips
Provides ATS-friendly resume optimization recommendations.

## ✅ Missing Skill Detection
Identifies missing technical skills from the job description.

## ✅ Job Role Prediction
Predicts suitable technical role based on resume skills.

## ✅ Resume Ranking
Ranks multiple resumes based on ATS score.

## ✅ History Dashboard
Stores and displays previous analysis results using SQLite.

## ✅ CSV Export
Allows exporting analysis results as CSV.

---

# 🛠️ Tech Stack

## Frontend
- Streamlit

## Backend
- FastAPI

## AI / NLP
- Ollama Llama3
- SentenceTransformers
- Scikit-learn
- TF-IDF
- Cosine Similarity

## Database
- SQLite

---

# 📂 Project Structure

```bash
resume-keyword-matcher/
│
├── api.py
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── utils/
│   ├── preprocess.py
│   ├── similarity.py
│   ├── embeddings.py
│   ├── skills.py
│   ├── role_classifier.py
│   │
│   └── services/
│       └── llm_service.py
│
├── resumes.db
