import time
import threading
import queue

try:
    import ollama
    _OLLAMA_AVAILABLE = True
    _OLLAMA_ERROR = ""
except Exception as e:
    _OLLAMA_AVAILABLE = False
    _OLLAMA_ERROR = str(e)

def _ollama_result(prompt, timeout_seconds=25):
    if not _OLLAMA_AVAILABLE:
        raise RuntimeError(f"Ollama unavailable: {_OLLAMA_ERROR}")

    result_queue = queue.Queue()

    def worker():
        try:
            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}]
            )
            if isinstance(response, dict):
                content = response.get("message", {}).get("content", "")
            else:
                content = str(response)
            result_queue.put(("success", content or ""))
        except Exception as e:
            result_queue.put(("error", str(e)))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    try:
        status, payload = result_queue.get(timeout=timeout_seconds)
        if status == "success":
            return payload
        raise RuntimeError(payload)
    except queue.Empty:
        raise TimeoutError("Ollama request timed out")


def _safe_generate(prompt, timeout_seconds, fallback_text):
    start_time = time.time()
    try:
        result = _ollama_result(prompt, timeout_seconds=timeout_seconds)
        elapsed = time.time() - start_time
        print(f"🤖 Ollama response generated in {elapsed:.2f}s")
        return result.strip() or fallback_text
    except Exception as exc:
        elapsed = time.time() - start_time
        print(f"⚠️ Ollama failed after {elapsed:.2f}s: {str(exc)}")
        return fallback_text


def _simple_resume_rewrite_fallback(resume, jd, matched_skills, missing_skills, job_role):
    bullets = []
    if job_role:
        bullets.append(f"Target role: {job_role}. Align experience with this position.")
    if matched_skills:
        bullets.append(f"Highlight strengths in: {', '.join(matched_skills[:6])}.")
    if missing_skills:
        bullets.append(f"Add or strengthen these missing skills: {', '.join(missing_skills[:6])}.")
    bullets.append("Use strong action verbs, quantify results, and keep resume formatting ATS-friendly.")
    bullets.append("Lead with impact statements such as improved, delivered, reduced, automated, and optimized.")
    bullets.append("Keep each bullet short, specific, and focused on measurable achievement.")
    return "\n".join(f"- {line}" for line in bullets)


def generate_resume_feedback(resume, jd, matched_skills=None, missing_skills=None, job_role=None, timeout_seconds=20):
    prompt = f"""
    You are an expert resume reviewer for technical hiring teams.
    Analyze the resume and job description together.

    Target role: {job_role or 'Candidate'}
    Resume:
    {resume[:1400]}

    Job Description:
    {jd[:1200]}

    Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
    Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

    Provide:
    1. A concise summary of the strongest fit areas
    2. Specific suggestions for improving alignment to the JD
    3. What to add or emphasize for ATS and recruiter review

    Keep the output brief, recruiter-friendly, and actionable.
    """

    return _safe_generate(
        prompt,
        timeout_seconds=timeout_seconds,
        fallback_text="💡 Improve alignment by adding quantifiable results and stronger keywords from the job description."
    )


def generate_resume_rewrite(resume, jd, matched_skills=None, missing_skills=None, job_role=None, timeout_seconds=22):
    prompt = f"""
    You are a professional resume writer optimizing resumes for ATS and hiring managers.
    Rewrite the resume content in a more polished, recruiter-friendly way.

    Target role: {job_role or 'Relevant role'}

    Job Description:
    {jd[:1200]}

    Resume:
    {resume[:1400]}

    Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
    Missing Skills to consider: {', '.join(missing_skills) if missing_skills else 'None'}

    Return:
    - 4 bullet points for experience or key qualifications
    - A stronger summary sentence
    - ATS-friendly phrasing with measurable accomplishments
    - Use action verbs and quantify impact when possible

    Output only the rewritten resume section in bullet form.
    """

    return _safe_generate(
        prompt,
        timeout_seconds=timeout_seconds,
        fallback_text=_simple_resume_rewrite_fallback(resume, jd, matched_skills, missing_skills, job_role)
    )


def generate_ats_tips(resume, jd, timeout_seconds=18):
    prompt = f"""
    You are an ATS optimization expert.
    Review this resume and the job description.

    Resume:
    {resume[:1100]}

    Job Description:
    {jd[:1100]}

    Provide:
    1. Key ATS formatting and keyword improvements
    2. What to simplify or remove for better parsing
    3. How to make bullet points more scan-friendly

    Keep the advice concise and practical.
    """

    return _safe_generate(
        prompt,
        timeout_seconds=timeout_seconds,
        fallback_text="🎯 Keep formatting simple, include JD keywords, avoid graphics, and use standard section headings for better ATS parsing."
    )


def generate_skill_suggestions(missing_skills, jd_skills, timeout_seconds=18):
    prompt = f"""
    You are a career coach advising a candidate on missing skills.
    Based on the job description and the current resume fit:

    Required skills: {', '.join(jd_skills) if jd_skills else 'None'}
    Missing skills: {', '.join(missing_skills) if missing_skills else 'None'}

    Provide:
    1. A prioritized list of missing skills to develop
    2. Recommended focus areas or learning resources
    3. How the candidate can mention these skills once they build them

    Keep the response actionable and concise.
    """

    return _safe_generate(
        prompt,
        timeout_seconds=timeout_seconds,
        fallback_text="🎓 Build the missing skills listed above and emphasize them with concrete project outcomes and tools."
    )


def generate_action_verbs(job_role=None, timeout_seconds=12):
    prompt = f"""
    You are generating strong resume action verbs for a {job_role or 'professional'} candidate.
    Provide 6-8 high-impact verbs related to leadership, delivery, optimization, and results.
    """

    return _safe_generate(
        prompt,
        timeout_seconds=timeout_seconds,
        fallback_text="✍️ Use strong verbs like Architected, Engineered, Optimized, Transformed, Delivered, Accelerated, Automated, Streamlined."
    )


def generate_all_ai_features(resume, jd, matched_skills, missing_skills, jd_skills, job_role, timeout_seconds=50):
    start_time = time.time()
    fallbacks = {
        "ai_feedback": "💡 Improve your resume by adding more quantifiable achievements and aligning with job description keywords.",
        "resume_rewrite": _simple_resume_rewrite_fallback(resume, jd, matched_skills, missing_skills, job_role),
        "ats_tips": "🎯 Keep formatting simple, include JD keywords, avoid graphics, and use standard section headings for better ATS parsing.",
        "skill_suggestions": "🎓 Build the missing skills listed above and emphasize them with concrete project outcomes and tools.",
        "action_verbs": "✍️ Use powerful action verbs like Architected, Engineered, Optimized, Transformed, Delivered, Accelerated."
    }

    feature_map = {
        "ai_feedback": (generate_resume_feedback, (resume, jd, matched_skills, missing_skills, job_role)),
        "resume_rewrite": (generate_resume_rewrite, (resume, jd, matched_skills, missing_skills, job_role)),
        "ats_tips": (generate_ats_tips, (resume, jd)),
        "skill_suggestions": (generate_skill_suggestions, (missing_skills, jd_skills)),
        "action_verbs": (generate_action_verbs, (job_role,))
    }

    results = {}
    queues = {}
    threads = []
    per_feature_timeout = max(10, timeout_seconds // len(feature_map))

    for feature_name, (func, args) in feature_map.items():
        feature_queue = queue.Queue()
        queues[feature_name] = feature_queue

        def worker(fn=func, fargs=args, q=feature_queue, name=feature_name):
            try:
                value = fn(*fargs, timeout_seconds=per_feature_timeout)
                q.put(("success", value))
            except Exception as exc:
                q.put(("error", str(exc)))

        thread = threading.Thread(target=worker, daemon=True)
        threads.append(thread)
        thread.start()

    end_time = time.time() + timeout_seconds
    for feature_name, q in queues.items():
        remaining_time = max(0.1, end_time - time.time())
        try:
            status, value = q.get(timeout=remaining_time)
            results[feature_name] = value if status == "success" else fallbacks.get(feature_name, "")
        except queue.Empty:
            results[feature_name] = fallbacks.get(feature_name, "")

    elapsed = time.time() - start_time
    print(f"🤖 All AI features generated in {elapsed:.2f}s")
    return results
