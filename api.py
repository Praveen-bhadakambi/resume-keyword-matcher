from fastapi import FastAPI
from pydantic import BaseModel

from utils.preprocess import preprocess
from utils.similarity import compute_similarity
from utils.embeddings import semantic_similarity
from utils.skills import extract_skills
from utils.role_classifier import classify_role

from utils.services.llm_service import generate_all_ai_features

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
        # 🔥 CRITICAL FIX: Extract skills from ORIGINAL text, not preprocessed
        # Preprocessing removes punctuation and stopwords needed for multi-word skills
        skills_start = time.time()
        resume_skills = extract_skills(data.resume)
        jd_skills = extract_skills(data.jd)
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
        # 🤖 AI FEATURES (WITH TIMEOUT & FALLBACK)
        # =========================
        ai_features_start = time.time()
        ai_features = {}
        try:
            # Call all AI features in parallel with fallbacks
            ai_features = generate_all_ai_features(
                resume=data.resume,
                jd=data.jd,
                matched_skills=common,
                missing_skills=missing,
                jd_skills=jd_skills,
                job_role=predicted_role
            )
            ai_features_time = time.time() - ai_features_start
            print(f"🤖 All AI features generated in {ai_features_time:.2f}s")
        except Exception as e:
            ai_features_time = time.time() - ai_features_start
            print(f"⚠️ AI features generation failed after {ai_features_time:.2f}s: {str(e)}")
            # Use fallback messages - don't fail the request
            ai_features = {
                "ai_feedback": "💡 Improve your resume by adding more quantifiable achievements and aligning with job description keywords.",
                "resume_rewrite": "📝 Professional resume format with stronger action verbs and quantified results.",
                "ats_tips": "🎯 Use standard formatting, include JD keywords, and avoid graphics for better ATS compatibility.",
                "skill_suggestions": "🎓 Consider developing skills in emerging technologies and frameworks relevant to your target role.",
                "action_verbs": "✍️ Use powerful action verbs like Architected, Engineered, Optimized, Transformed, Accelerated."
            }

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
        print("AI Features Generated:", list(ai_features.keys()))
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
        # 📤 FINAL RESPONSE - COMPREHENSIVE AI FEATURES
        # =========================
        return {
            # Scoring Metrics
            "ats": ats,
            "tfidf": tfidf,
            "semantic": semantic,
            
            # Skills Analysis
            "matched_skills": common,
            "missing_skills": missing,
            "skill_match_score": round(skill_score, 2),
            
            # Role Prediction
            "predicted_role": predicted_role,
            
            # AI-Generated Features
            "ai_feedback": ai_features.get("ai_feedback", ""),
            "resume_rewrite": ai_features.get("resume_rewrite", ""),
            "ats_tips": ai_features.get("ats_tips", ""),
            "skill_suggestions": ai_features.get("skill_suggestions", ""),
            "action_verbs": ai_features.get("action_verbs", ""),
            
            # Metadata
            "processing_time": round(total_time, 2)
        }

    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ CRITICAL ERROR after {error_time:.2f}s: {str(e)}")

        # Return minimal response even on error with all fields for UI compatibility
        return {
            "error": str(e),
            "ats": 0,
            "tfidf": 0,
            "semantic": 0,
            "matched_skills": [],
            "missing_skills": [],
            "skill_match_score": 0,
            "predicted_role": "Unknown",
            "ai_feedback": "⚠️ Error during processing. Please try again.",
            "resume_rewrite": "⚠️ Error during processing. Please try again.",
            "ats_tips": "⚠️ Error during processing. Please try again.",
            "skill_suggestions": "⚠️ Error during processing. Please try again.",
            "action_verbs": "⚠️ Error during processing. Please try again.",
            "processing_time": round(error_time, 2)
        }