skills_list = [
    "python", "java", "machine learning", "sql",
    "react", "aws", "docker", "data analysis"
]

def extract_skills(text):
    return [skill for skill in skills_list if skill in text.lower()]