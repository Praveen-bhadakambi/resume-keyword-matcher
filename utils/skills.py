import spacy

nlp = spacy.load("en_core_web_sm")

# Technical skills database
SKILLS_DB = [
    "python", "java", "sql", "aws", "docker",
    "machine learning", "deep learning",
    "nlp", "tensorflow", "pytorch",
    "react", "fastapi", "flask",
    "mongodb", "mysql", "kubernetes"
]

def extract_skills(text):

    text = text.lower()

    doc = nlp(text)

    found_skills = set()

    # Keyword matching
    for skill in SKILLS_DB:
        if skill in text:
            found_skills.add(skill)

    # Named entity extraction
    for ent in doc.ents:
        if ent.text.lower() in SKILLS_DB:
            found_skills.add(ent.text.lower())

    return list(found_skills)