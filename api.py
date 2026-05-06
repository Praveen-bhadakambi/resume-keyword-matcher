from fastapi import FastAPI
from pydantic import BaseModel
from utils.preprocess import preprocess
from utils.similarity import compute_similarity
from utils.embeddings import semantic_similarity
from utils.skills import extract_skills
from database import cursor, conn

app = FastAPI()

# =========================
# 📌 Request Model
# =========================
class RequestModel(BaseModel):
    resume: str
    jd: str


# =========================
# 📌 ATS Score Function
# =========================
def ats_score(tfidf, semantic, skill_match):
    return round((0.3 * tfidf + 0.5 * semantic + 0.2 * skill_match), 2)


# =========================
# 🚀 MAIN API ENDPOINT
# =========================
@app.post("/match")
async def match(data: RequestModel):
    try:
        # 🔹 Preprocess text
        clean_resume = preprocess(data.resume)
        clean_jd = preprocess(data.jd)

        # 🔹 Similarity calculations
        tfidf = compute_similarity(clean_resume, clean_jd)
        semantic = semantic_similarity(clean_resume, clean_jd)

        # 🔹 Skill extraction
        resume_skills = extract_skills(clean_resume)
        jd_skills = extract_skills(clean_jd)

        # =========================
        # 🔥 SKILL MATCHING LOGIC
        # =========================
        common = list(set(resume_skills) & set(jd_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        # =========================
        # 🧪 DEBUG OUTPUT
        # =========================
        print("\n========== DEBUG ==========")
        print("Resume Skills:", resume_skills)
        print("JD Skills:", jd_skills)
        print("Matched Skills:", common)
        print("Missing Skills:", missing)
        print("===========================\n")

        # 🔹 Skill match %
        skill_score = (len(common) / len(jd_skills)) * 100 if jd_skills else 0

        # 🔹 ATS score
        ats = ats_score(tfidf, semantic, skill_score)

        # =========================
        # 💾 STORE IN DATABASE
        # =========================
        cursor.execute(
            "INSERT INTO results (resume_name, ats, tfidf, semantic) VALUES (?, ?, ?, ?)",
            ("resume", ats, tfidf, semantic)
        )
        conn.commit()

        # =========================
        # 📤 RESPONSE
        # =========================
        return {
            "tfidf": tfidf,
            "semantic": semantic,
            "ats": ats,
            "matched_skills": common,
            "missing_skills": missing
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "error": str(e)
        }