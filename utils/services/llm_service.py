from dotenv import load_dotenv
import os
import time
from queue import Queue
from threading import Thread

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST")

try:
    import ollama
except Exception:  # pragma: no cover - optional dependency
    ollama = None


def _build_fast_ai_response(
    resume_skills=None,
    missing_skills=None,
    predicted_role=None
):
    skills = ", ".join(resume_skills or [])
    missing = ", ".join(missing_skills or [])
    role = predicted_role or "Software Engineer"

    feedback = (
        f"Add more role-specific keywords like {missing or 'relevant skills'} "
        f"to better match {role}."
        if missing
        else "Highlight measurable impact and role-specific achievements."
    )
    rewrite = (
        f"Tailored {role} resume summary emphasizing relevant experience, "
        f"core skills such as {skills or 'domain expertise'}, and measurable impact."
    )
    ats = (
        "Use ATS-friendly formatting, concise bullets, and keyword-rich phrases "
        "that mirror the job description."
    )

    return {
        "ai_feedback": feedback,
        "resume_rewrite": rewrite,
        "ats_tips": ats,
    }


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
        # 🚀 FAST OLLAMA CALL WITH TIMEOUT
        # =========================
        if ollama is None:
            return _build_fast_ai_response(
                resume_skills=resume_skills,
                missing_skills=missing_skills,
                predicted_role=predicted_role,
            )

        result_queue = Queue()

        def _run_ollama_call():
            try:
                response = ollama.chat(
                    model="llama3",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    options={
                        "temperature": 0.1,
                        "num_predict": 30,
                    },
                )
                result_queue.put(("ok", response))
            except Exception as exc:
                result_queue.put(("error", str(exc)))

        thread = Thread(target=_run_ollama_call, daemon=True)
        thread.start()

        try:
            result_type, result = result_queue.get(timeout=2)
        except Exception:
            print("⚠️ Ollama slow; using local AI fallback")
            return _build_fast_ai_response(
                resume_skills=resume_skills,
                missing_skills=missing_skills,
                predicted_role=predicted_role,
            )

        if result_type != "ok":
            raise RuntimeError(result)

        output = result["message"]["content"]

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

        return _build_fast_ai_response(
            resume_skills=resume_skills,
            missing_skills=missing_skills,
            predicted_role=predicted_role,
        )