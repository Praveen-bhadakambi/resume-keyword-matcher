import ollama
import time
import threading
import queue
from typing import Dict, Optional

# Fallback messages for when AI is unavailable
FALLBACK_MESSAGES = {
    "resume_suggestions": "💡 Improve your resume by: 1) Add quantified achievements, 2) Use strong action verbs, 3) Tailor to job description keywords, 4) Keep formatting clean and ATS-friendly",
    "ats_tips": "🎯 ATS Optimization: 1) Use standard section headings (Experience, Skills, Education), 2) Include keywords from job description, 3) Avoid graphics and unusual formatting, 4) Use common fonts, 5) Include company names and dates",
    "resume_rewrite": "📝 Improved Resume Format:\n\n[Professional Summary]\nExperienced professional with strong technical skills seeking [Target Role] position to drive [Business Value].\n\n[Key Achievements]\n• Increased [Metric] by [%] through [Action]\n• Led implementation of [Technology/Process] resulting in [Outcome]\n• Improved [Area] by [Amount] using [Skill/Tool]",
    "skill_recommendations": "🎓 To improve fit, consider developing: SQL Database Management, Cloud Infrastructure (AWS/Azure), DevOps Practices, System Design, Advanced Frontend Frameworks",
    "action_verbs": "✍️ Use stronger action verbs: Architected, Engineered, Optimized, Transformed, Accelerated, Spearheaded, Pioneered, Deployed, Orchestrated, Streamlined"
}

def _call_ollama_with_timeout(prompt: str, timeout_seconds: int = 20) -> Optional[str]:
    """
    Call Ollama with timeout handling.
    
    Args:
        prompt: The prompt to send to Ollama
        timeout_seconds: Timeout in seconds
        
    Returns:
        Response text or None if timeout/error
    """
    result_queue = queue.Queue()

    def worker():
        try:
            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}]
            )
            result_queue.put(("success", response["message"]["content"]))
        except Exception as e:
            result_queue.put(("error", str(e)))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    try:
        result_type, result = result_queue.get(timeout=timeout_seconds)
        if result_type == "success":
            return result
        else:
            print(f"Ollama error: {result}")
            return None
    except queue.Empty:
        print(f"Ollama timeout after {timeout_seconds}s")
        return None


def generate_resume_suggestions(resume: str, jd: str, matched_skills: list, missing_skills: list, timeout_seconds: int = 15) -> str:
    """
    Generate comprehensive resume improvement suggestions.
    
    Args:
        resume: Resume text
        jd: Job description text
        matched_skills: List of matched skills
        missing_skills: List of missing skills
        timeout_seconds: Timeout for AI generation
        
    Returns:
        AI-generated suggestions or fallback message
    """
    try:
        prompt = f"""You are an expert resume coach. Analyze this resume against the job description and provide specific, actionable suggestions.

Resume (first 1500 chars):
{resume[:1500]}

Job Description (first 1000 chars):
{jd[:1000]}

Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

Provide 4-5 specific suggestions to improve this resume for this job:
- Focus on achievements and quantifiable results
- Highlight relevant skills from the job description
- Use specific examples from their experience
- Keep suggestions concise and actionable

Format as a bullet list."""

        result = _call_ollama_with_timeout(prompt, timeout_seconds)
        return result if result else FALLBACK_MESSAGES["resume_suggestions"]
    except Exception as e:
        print(f"Error in generate_resume_suggestions: {e}")
        return FALLBACK_MESSAGES["resume_suggestions"]


def generate_ats_optimization_tips(resume: str, jd: str, timeout_seconds: int = 15) -> str:
    """
    Generate ATS-specific optimization tips.
    
    Args:
        resume: Resume text
        jd: Job description text
        timeout_seconds: Timeout for AI generation
        
    Returns:
        ATS optimization tips or fallback message
    """
    try:
        prompt = f"""You are an ATS (Applicant Tracking System) expert. Analyze this resume and provide specific ATS optimization tips.

Resume (first 1200 chars):
{resume[:1200]}

Job Description:
{jd[:800]}

Provide 5-6 specific ATS optimization recommendations:
- Keep formatting simple (no graphics, tables, or unusual fonts)
- Include relevant keywords from the job description
- Use standard section headings
- Proper spacing and line breaks
- Avoid fancy formatting
- Include metrics and numbers where possible

Format as a numbered list with brief explanations."""

        result = _call_ollama_with_timeout(prompt, timeout_seconds)
        return result if result else FALLBACK_MESSAGES["ats_tips"]
    except Exception as e:
        print(f"Error in generate_ats_optimization_tips: {e}")
        return FALLBACK_MESSAGES["ats_tips"]


def generate_resume_rewrite(resume_text: str, jd: str, job_role: str, timeout_seconds: int = 20) -> str:
    """
    Generate a rewritten version of resume bullets with stronger language.
    
    Args:
        resume_text: Original resume text
        jd: Job description
        job_role: Predicted job role
        timeout_seconds: Timeout for AI generation
        
    Returns:
        Rewritten resume or fallback message
    """
    try:
        prompt = f"""You are a professional resume writer. Rewrite the key resume bullets to be more impressive and ATS-friendly.

Original Resume (key content):
{resume_text[:1500]}

Job Description:
{jd[:800]}

Target Role: {job_role}

Rewrite 4-5 key resume bullet points to:
- Use powerful action verbs
- Include quantifiable achievements with metrics
- Align with job description requirements
- Sound professional and impressive
- Be ATS-optimized

Format as bullet points using dashes (-)."""

        result = _call_ollama_with_timeout(prompt, timeout_seconds)
        return result if result else FALLBACK_MESSAGES["resume_rewrite"]
    except Exception as e:
        print(f"Error in generate_resume_rewrite: {e}")
        return FALLBACK_MESSAGES["resume_rewrite"]


def generate_skill_recommendations(resume_skills: list, jd_skills: list, missing_skills: list, timeout_seconds: int = 15) -> str:
    """
    Generate recommendations for missing skills to develop.
    
    Args:
        resume_skills: Skills found in resume
        jd_skills: Skills required by job description
        missing_skills: Skills missing from resume
        timeout_seconds: Timeout for AI generation
        
    Returns:
        Skill recommendations or fallback message
    """
    try:
        prompt = f"""You are a career development advisor. Provide strategic recommendations for developing missing skills.

Resume Skills: {', '.join(resume_skills) if resume_skills else 'None found'}
Required Skills: {', '.join(jd_skills) if jd_skills else 'None found'}
Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}

Provide recommendations for:
1. Which missing skills to prioritize
2. How to develop these skills (courses, projects, certifications)
3. Timeline and resources
4. Related skills to learn alongside
5. How to showcase these skills once developed

Keep recommendations practical and actionable."""

        result = _call_ollama_with_timeout(prompt, timeout_seconds)
        return result if result else FALLBACK_MESSAGES["skill_recommendations"]
    except Exception as e:
        print(f"Error in generate_skill_recommendations: {e}")
        return FALLBACK_MESSAGES["skill_recommendations"]


def generate_action_verbs_suggestions(resume: str, timeout_seconds: int = 10) -> str:
    """
    Generate suggestions for stronger action verbs.
    
    Args:
        resume: Resume text
        timeout_seconds: Timeout for AI generation
        
    Returns:
        Action verb suggestions or fallback message
    """
    try:
        prompt = f"""Review this resume excerpt and suggest stronger action verbs to replace weak ones.

Resume excerpt:
{resume[:1000]}

For each weak verb found, suggest 2-3 stronger alternatives:
- Current weak verbs might include: worked, helped, involved, responsible for, did, handled
- Replace with powerful verbs: architected, engineered, spearheaded, optimized, accelerated, transformed

Format as: 'Weak Verb -> Stronger Alternatives'
List 5-7 suggestions."""

        result = _call_ollama_with_timeout(prompt, timeout_seconds)
        return result if result else FALLBACK_MESSAGES["action_verbs"]
    except Exception as e:
        print(f"Error in generate_action_verbs_suggestions: {e}")
        return FALLBACK_MESSAGES["action_verbs"]


def generate_all_ai_features(resume: str, jd: str, matched_skills: list, missing_skills: list, jd_skills: list, job_role: str) -> Dict[str, str]:
    """
    Generate all AI features in parallel for performance.
    
    Args:
        resume: Resume text
        jd: Job description text
        matched_skills: Skills matched with JD
        missing_skills: Skills missing from resume
        jd_skills: All skills from JD
        job_role: Predicted job role
        
    Returns:
        Dictionary with all AI-generated features
    """
    results = {
        "resume_suggestions": FALLBACK_MESSAGES["resume_suggestions"],
        "ats_optimization_tips": FALLBACK_MESSAGES["ats_tips"],
        "resume_rewrite": FALLBACK_MESSAGES["resume_rewrite"],
        "skill_recommendations": FALLBACK_MESSAGES["skill_recommendations"],
        "action_verbs": FALLBACK_MESSAGES["action_verbs"]
    }
    
    # Create threads for parallel processing
    threads = []
    
    def get_resume_suggestions():
        results["resume_suggestions"] = generate_resume_suggestions(resume, jd, matched_skills, missing_skills)
    
    def get_ats_tips():
        results["ats_optimization_tips"] = generate_ats_optimization_tips(resume, jd)
    
    def get_resume_rewrite():
        results["resume_rewrite"] = generate_resume_rewrite(resume, jd, job_role)
    
    def get_skill_recs():
        results["skill_recommendations"] = generate_skill_recommendations(matched_skills, jd_skills, missing_skills)
    
    def get_action_verbs():
        results["action_verbs"] = generate_action_verbs_suggestions(resume)
    
    # Start all threads
    for func in [get_resume_suggestions, get_ats_tips, get_resume_rewrite, get_skill_recs, get_action_verbs]:
        thread = threading.Thread(target=func, daemon=True)
        thread.start()
        threads.append(thread)
    
    # Wait for all threads with timeout
    for thread in threads:
        thread.join(timeout=25)
    
    return results