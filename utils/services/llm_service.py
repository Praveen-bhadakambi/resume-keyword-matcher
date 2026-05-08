import ollama
import time
import threading
import queue

def generate_resume_feedback_with_timeout(resume, jd, timeout_seconds=30):
    """Generate AI feedback with proper timeout handling using threading."""

    result_queue = queue.Queue()

    def worker():
        try:
            prompt = f"""
            Analyze this resume against the job description.

            Resume:
            {resume[:2000]}...  # Truncate for performance

            Job Description:
            {jd[:2000]}...  # Truncate for performance

            Give:
            1. Missing skills
            2. Resume improvement tips
            3. ATS optimization suggestions

            Keep response under 500 words.
            """

            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}]
            )

            result_queue.put(("success", response["message"]["content"]))

        except Exception as e:
            result_queue.put(("error", str(e)))

    # Start worker thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    # Wait for result with timeout
    try:
        result_type, result = result_queue.get(timeout=timeout_seconds)
        if result_type == "success":
            return result
        else:
            raise Exception(result)
    except queue.Empty:
        return "AI feedback temporarily unavailable (timeout). Basic ATS analysis completed successfully."

def generate_resume_feedback(resume, jd, timeout_seconds=30):
    """
    Generate AI feedback with timeout handling.
    Returns feedback or fallback message if timeout occurs.
    """

    start_time = time.time()

    try:
        result = generate_resume_feedback_with_timeout(resume, jd, timeout_seconds)
        elapsed = time.time() - start_time
        print(f"🤖 AI Feedback generated in {elapsed:.2f}s")
        return result

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"⚠️ AI Feedback failed after {elapsed:.2f}s: {str(e)}")
        return "AI feedback temporarily unavailable. Basic ATS analysis completed successfully."