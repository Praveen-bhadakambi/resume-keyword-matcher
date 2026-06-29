from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")




from sklearn.metrics.pairwise import cosine_similarity


# =========================
# 🚀 LOAD MODEL ONLY ONCE
# =========================
model = None


def get_model():

    global model

    if model is None:

        try:

            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        except Exception as e:

            print(
                "Semantic model unavailable:",
                str(e)
            )

            return None

    return model


# =========================
# 🚀 FAST SEMANTIC SIMILARITY
# =========================
def semantic_similarity(

    resume,

    jd
):

    try:

        current_model = get_model()

        if current_model is None:

            return 0.0

        # =========================
        # ✅ REDUCE TEXT SIZE
        # =========================
        resume = resume[:500]

        jd = jd[:500]

        # =========================
        # 🚀 FAST EMBEDDINGS
        # =========================
        embeddings = current_model.encode(

            [resume, jd],

            convert_to_numpy=True,

            show_progress_bar=False
        )

        # =========================
        # 🚀 COSINE SIMILARITY
        # =========================
        similarity = cosine_similarity(

            [embeddings[0]],

            [embeddings[1]]
        )[0][0]

        # =========================
        # ✅ FIX NUMPY FLOAT ERROR
        # =========================
        similarity = float(similarity)

        # =========================
        # ✅ RETURN NORMAL PYTHON FLOAT
        # =========================
        return round(
            similarity * 100,
            2
        )

    except Exception as e:

        print(
            "Semantic Error:",
            str(e)
        )

        # ✅ RETURN SAFE PYTHON FLOAT
        return 0.0
