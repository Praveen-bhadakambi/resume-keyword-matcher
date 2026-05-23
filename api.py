from fastapi import FastAPI
from pydantic import BaseModel

from utils.preprocess import preprocess
from utils.similarity import compute_similarity
from utils.embeddings import semantic_similarity
from utils.skills import extract_skills
from utils.role_classifier import classify_role

from utils.services.llm_service import (
    generate_all_ai_features
)

from database import cursor, conn


# =========================
# 🚀 FASTAPI APP
# =========================
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
def ats_score(

    tfidf,

    semantic,

    skill_match

):

    return round(

        (0.3 * tfidf) +

        (0.5 * semantic) +

        (0.2 * skill_match),

        2
    )


# =========================
# 🚀 MAIN API ENDPOINT
# =========================
@app.post("/match")
async def match(data: RequestModel):

    try:

        # =========================
        # 🔹 PREPROCESS TEXT
        # =========================
        clean_resume = preprocess(
            data.resume
        )

        clean_jd = preprocess(
            data.jd
        )

        # =========================
        # 🔹 TF-IDF SIMILARITY
        # =========================
        try:

            tfidf = compute_similarity(

                clean_resume,

                clean_jd
            )

        except Exception as e:

            print("TFIDF ERROR:", e)

            tfidf = 0

        # =========================
        # 🔹 SEMANTIC SIMILARITY
        # =========================
        try:

            semantic = semantic_similarity(

                clean_resume,

                clean_jd
            )

        except Exception as e:

            print("SEMANTIC ERROR:", e)

            semantic = 0

        # =========================
        # 🔹 SKILL EXTRACTION
        # =========================
        try:

            resume_skills = extract_skills(
                clean_resume
            )

            jd_skills = extract_skills(
                clean_jd
            )

        except Exception as e:

            print("SKILL ERROR:", e)

            resume_skills = []

            jd_skills = []

        # =========================
        # 🔥 MATCHED SKILLS
        # =========================
        common = list(

            set(resume_skills) &

            set(jd_skills)
        )

        # =========================
        # ⚠️ MISSING SKILLS
        # =========================
        missing = list(

            set(jd_skills) -

            set(resume_skills)
        )

        # =========================
        # 🔹 SKILL MATCH %
        # =========================
        skill_score = (

            (len(common) / len(jd_skills)) * 100

            if jd_skills else 0
        )

        # =========================
        # 🎯 ATS SCORE
        # =========================
        ats = ats_score(

            tfidf,

            semantic,

            skill_score
        )

        # =========================
        # 🧠 ROLE PREDICTION
        # =========================
        try:

            predicted_role = classify_role(
                resume_skills
            )

        except Exception as e:

            print("ROLE ERROR:", e)

            predicted_role = (
                "Software Engineer"
            )

        # =========================
        # 🤖 SINGLE AI CALL
        # =========================
        try:

            ai_results = generate_all_ai_features(

                data.resume,

                data.jd,

                resume_skills,

                missing,

                predicted_role
            )

        except Exception as e:

            print("AI ERROR:", e)

            ai_results = {

                "ai_feedback":
                "Improve ATS keyword matching.",

                "resume_rewrite":
                "Developed scalable backend APIs.",

                "ats_tips":
                "Use ATS-friendly formatting."
            }

        # =========================
        # 📌 AI VALUES
        # =========================
        ai_feedback = ai_results.get(

            "ai_feedback",

            "Improve ATS keyword matching."
        )

        resume_rewrite = ai_results.get(

            "resume_rewrite",

            "Built scalable applications."
        )

        ats_tips = ai_results.get(

            "ats_tips",

            "Use ATS-friendly formatting."
        )

        # =========================
        # 💾 STORE IN DATABASE
        # =========================
        try:

            cursor.execute(

                """
                INSERT INTO results
                (
                    resume_name,
                    ats,
                    tfidf,
                    semantic
                )

                VALUES (?, ?, ?, ?)
                """,

                (
                    "resume",

                    ats,

                    tfidf,

                    semantic
                )
            )

            conn.commit()

        except Exception as e:

            print("DATABASE ERROR:", e)

        # =========================
        # 🧪 DEBUG OUTPUT
        # =========================
        print("\n========== DEBUG ==========")

        print("Resume Skills:", resume_skills)

        print("JD Skills:", jd_skills)

        print("Matched Skills:", common)

        print("Missing Skills:", missing)

        print("Predicted Role:", predicted_role)

        print("ATS:", ats)

        print("===========================\n")

        # =========================
        # ✅ FINAL RESPONSE
        # =========================
        return {

            "tfidf": tfidf,

            "semantic": semantic,

            "ats": ats,

            "matched_skills": common,

            "missing_skills": missing,

            "predicted_role": predicted_role,

            "ai_feedback": ai_feedback,

            "resume_rewrite": resume_rewrite,

            "ats_tips": ats_tips
        }

    except Exception as e:

        print("❌ API CRASH:", str(e))

        # ✅ NEVER CRASH
        return {

            "tfidf": 0,

            "semantic": 0,

            "ats": 0,

            "matched_skills": [],

            "missing_skills": [],

            "predicted_role":
            "Software Engineer",

            "ai_feedback":
            "AI feedback unavailable.",

            "resume_rewrite":
            "Resume rewrite unavailable.",

            "ats_tips":
            "ATS tips unavailable."
        }