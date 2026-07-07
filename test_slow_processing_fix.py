import time

from utils.services.llm_service import generate_all_ai_features


def test_ai_feature_generation_fails_fast_on_slow_ollama():
    start = time.time()
    result = generate_all_ai_features(
        "Python developer with FastAPI and Docker",
        "Python backend engineer",
    )
    elapsed = time.time() - start

    assert isinstance(result, dict)
    assert "ai_feedback" in result
    assert "resume_rewrite" in result
    assert "ats_tips" in result
    assert elapsed < 5, f"Expected fast fallback, got {elapsed:.2f}s"


if __name__ == "__main__":
    test_ai_feature_generation_fails_fast_on_slow_ollama()
    print("✅ Fast fallback regression test passed")
