from sentence_transformers import SentenceTransformer, util

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')
    return _model


def semantic_similarity(resume, jd):
    model = _get_model()
    emb1 = model.encode(resume, convert_to_tensor=True)
    emb2 = model.encode(jd, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2)
    return round(float(score) * 100, 2)