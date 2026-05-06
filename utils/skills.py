def extract_skills(text):

    skills_db = [
        "python", "java", "c++", "c", "javascript",
        "machine learning", "deep learning", "nlp",
        "sql", "mysql", "mongodb",
        "aws", "docker", "kubernetes",
        "react", "node", "flask", "fastapi",
        "pandas", "numpy", "tensorflow", "pytorch",
        "data analysis", "data science"
    ]

    text = text.lower()

    found_skills = []

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    return found_skills