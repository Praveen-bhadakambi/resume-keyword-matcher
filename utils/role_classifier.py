def classify_role(skills):

    skills = [s.lower() for s in skills]

    if "machine learning" in skills:
        return "Data Scientist"

    elif "fastapi" in skills:
        return "Backend Engineer"

    elif "aws" in skills:
        return "Cloud Engineer"

    else:
        return "Software Engineer"