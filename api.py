from fastapi import FastAPI
from pydantic import BaseModel
from utils.preprocess import preprocess
from utils.similarity import compute_similarity
from utils.embeddings import semantic_similarity
from utils.skills import extract_skills

app = FastAPI()

# Request structure
class RequestModel(BaseModel):
    resume: str
    jd: str

def ats_score(tfidf, semantic, skill_match):
    return round((0.3*tfidf + 0.5*semantic + 0.2*skill_match), 2)

@app.post("/match")
async def match(data: RequestModel):

    clean_resume = preprocess(data.resume)
    clean_jd = preprocess(data.jd)

    tfidf = compute_similarity(clean_resume, clean_jd)
    semantic = semantic_similarity(clean_resume, clean_jd)

    resume_skills = extract_skills(clean_resume)
    jd_skills = extract_skills(clean_jd)

    common = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    skill_score = (len(common) / len(jd_skills)) * 100 if jd_skills else 0
    ats = ats_score(tfidf, semantic, skill_score)

    return {
        "tfidf": tfidf,
        "semantic": semantic,
        "ats": ats,
        "matched_skills": common,
        "missing_skills": missing
    }