from fastapi import FastAPI
from pydantic import BaseModel

from utils.preprocess import preprocess
from utils.similarity import compute_similarity
from utils.embeddings import semantic_similarity
from utils.skills import extract_skills
from utils.role_classifier import classify_role

from utils.services.llm_service import generate_resume_feedback

from database import cursor, conn

app = FastAPI()


# =========================
# 📌 REQUEST MODEL
# =========================
class RequestModel(BaseModel):
    resume: str
    jd: str


# =========================
# 📌 ATS SCORE FUNCTION
# =========================
def ats_score(tfidf, semantic, skill_match):

    return round(
        (0.3 * tfidf) +
        (0.5 * semantic) +
        (0.2 * skill_match),
        2
    )


# =========================
# 🏠 HOME ROUTE
# =========================
@app.get("/")
def home():

    return {
        "message": "Backend Running Successfully"
    }


# =========================
# 🚀 MAIN MATCH ENDPOINT
# =========================
@app.post("/match")
async def match(data: RequestModel):

    import time
    start_time = time.time()

    try:
        # =========================
        # 🔹 PREPROCESSING
        # =========================
        preprocess_start = time.time()
        clean_resume = preprocess(data.resume)
        clean_jd = preprocess(data.jd)
        preprocess_time = time.time() - preprocess_start
        print(f"🔹 Preprocessing completed in {preprocess_time:.2f}s")

        # =========================
        # 🔹 SIMILARITY SCORES
        # =========================
        similarity_start = time.time()
        tfidf = compute_similarity(clean_resume, clean_jd)
        semantic = semantic_similarity(clean_resume, clean_jd)
        similarity_time = time.time() - similarity_start
        print(f"🔹 Similarity scores computed in {similarity_time:.2f}s")

        # =========================
        # 🔹 SKILL EXTRACTION
        # =========================
        skills_start = time.time()
        resume_skills = extract_skills(clean_resume)
        jd_skills = extract_skills(clean_jd)
        skills_time = time.time() - skills_start
        print(f"🔹 Skills extracted in {skills_time:.2f}s")

        # =========================
        # 🔥 SKILL MATCHING
        # =========================
        common = list(set(resume_skills) & set(jd_skills))
        missing = list(set(jd_skills) - set(resume_skills))

        # =========================
        # 🔹 SKILL MATCH SCORE
        # =========================
        skill_score = (len(common) / len(jd_skills)) * 100 if jd_skills else 0

        # =========================
        # 🔹 ATS SCORE
        # =========================
        ats = ats_score(tfidf, semantic, skill_score)

        # =========================
        # 🤖 ROLE CLASSIFICATION
        # =========================
        role_start = time.time()
        predicted_role = classify_role(resume_skills)
        role_time = time.time() - role_start
        print(f"🤖 Role classification completed in {role_time:.2f}s")

        # =========================
        # 🤖 AI FEEDBACK (WITH TIMEOUT)
        # =========================
        ai_feedback = "AI feedback temporarily unavailable"
        try:
            ai_start = time.time()
            # Use shorter timeout for AI feedback to prevent blocking
            ai_feedback = generate_resume_feedback(data.resume, data.jd, timeout_seconds=20)
            ai_time = time.time() - ai_start
            print(f"🤖 AI feedback generated in {ai_time:.2f}s")
        except Exception as e:
            ai_time = time.time() - ai_start if 'ai_start' in locals() else 0
            print(f"⚠️ AI feedback failed after {ai_time:.2f}s: {str(e)}")
            # Continue with default message - don't fail the entire request

        # =========================
        # 🧪 DEBUG LOGS
        # =========================
        total_time = time.time() - start_time
        print(f"\n========== DEBUG ==========")
        print(f"Total processing time: {total_time:.2f}s")
        print("Resume Skills:", resume_skills)
        print("JD Skills:", jd_skills)
        print("Matched Skills:", common)
        print("Missing Skills:", missing)
        print("Predicted Role:", predicted_role)
        print("===========================\n")

        # =========================
        # 💾 STORE RESULTS (NON-BLOCKING)
        # =========================
        try:
            cursor.execute(
                """
                INSERT INTO results
                (resume_name, ats, tfidf, semantic)
                VALUES (?, ?, ?, ?)
                """,
                ("resume", ats, tfidf, semantic)
            )
            conn.commit()
        except Exception as db_e:
            print(f"⚠️ Database error (non-critical): {str(db_e)}")

        # =========================
        # 📤 FINAL RESPONSE
        # =========================
        return {
            "tfidf": tfidf,
            "semantic": semantic,
            "ats": ats,
            "matched_skills": common,
            "missing_skills": missing,
            "predicted_role": predicted_role,
            "ai_feedback": ai_feedback,
            "processing_time": round(total_time, 2)
        }

    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ CRITICAL ERROR after {error_time:.2f}s: {str(e)}")

        # Return minimal response even on error
        return {
            "error": str(e),
            "tfidf": 0,
            "semantic": 0,
            "ats": 0,
            "matched_skills": [],
            "missing_skills": [],
            "predicted_role": "Unknown",
            "ai_feedback": "Error occurred during processing",
            "processing_time": round(error_time, 2)
        }