from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')

def semantic_similarity(resume, jd):
    emb1 = model.encode(resume, convert_to_tensor=True)
    emb2 = model.encode(jd, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2)
    return round(float(score) * 100, 2)