from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")


import ollama
import time


# =========================
# 🚀 FAST AI GENERATION
# =========================
def generate_all_ai_features(

    resume,
    jd,
    resume_skills=None,
    missing_skills=None,
    predicted_role=None
):

    start_time = time.time()

    try:

        # =========================
        # ✂️ SMALLER INPUT
        # =========================
        resume = resume[:800]

        jd = jd[:500]

        skills = ", ".join(
            resume_skills or []
        )

        missing = ", ".join(
            missing_skills or []
        )

        role = predicted_role or "Software Engineer"

        # =========================
        # 🤖 SHORT PROMPT
        # =========================
        prompt = f"""
        Resume:
        {resume}

        Job Description:
        {jd}

        Skills:
        {skills}

        Missing:
        {missing}

        Role:
        {role}

        Return EXACTLY:

        FEEDBACK:
        short feedback

        REWRITE:
        short rewrite

        ATS:
        short ATS tip

        Maximum 1 line each.
        """

        # =========================
        # 🚀 FAST OLLAMA CALL
        # =========================
        response = ollama.chat(

            model="llama3",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            options={

                # ✅ VERY FAST SETTINGS
                "temperature": 0.1,

                "num_predict": 40
            }
        )

        output = response["message"]["content"]

        elapsed = time.time() - start_time

        print(
            f"🤖 AI completed in "
            f"{elapsed:.2f}s"
        )

        # =========================
        # ✅ DEFAULT VALUES
        # =========================
        feedback = (
            "Add more ATS keywords "
            "and quantify achievements."
        )

        rewrite = (
            "Developed scalable backend "
            "APIs using FastAPI."
        )

        ats = (
            "Use ATS-friendly formatting "
            "and keyword-rich bullet points."
        )

        # =========================
        # 🔥 SAFE PARSING
        # =========================
        try:

            if "FEEDBACK:" in output:

                feedback = output.split(
                    "FEEDBACK:"
                )[1].split(
                    "REWRITE:"
                )[0].strip()

            if "REWRITE:" in output:

                rewrite = output.split(
                    "REWRITE:"
                )[1].split(
                    "ATS:"
                )[0].strip()

            if "ATS:" in output:

                ats = output.split(
                    "ATS:"
                )[1].strip()

        except Exception:

            print("⚠️ Parsing fallback used")

        # =========================
        # ✅ NEVER RETURN BLANK
        # =========================
        if not feedback.strip():

            feedback = (
                "Improve ATS keyword matching."
            )

        if not rewrite.strip():

            rewrite = (
                "Built scalable AI-powered "
                "resume analysis platform."
            )

        if not ats.strip():

            ats = (
                "Use simple ATS-friendly "
                "resume formatting."
            )

        # =========================
        # ✅ FINAL RESPONSE
        # =========================
        return {

            "ai_feedback": feedback,

            "resume_rewrite": rewrite,

            "ats_tips": ats
        }

    except Exception as e:

        print("❌ AI ERROR:", str(e))

        return {

            "ai_feedback":
            "Improve ATS keyword matching.",

            "resume_rewrite":
            "Developed scalable backend APIs.",

            "ats_tips":
            "Use ATS-friendly formatting."
        }