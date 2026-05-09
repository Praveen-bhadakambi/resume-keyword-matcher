def classify_role(skills):
    """
    Classify job role based on detected skills.
    
    Args:
        skills: List of detected skills from resume
        
    Returns:
        Predicted job role
    """
    if not skills:
        return "Software Developer"
    
    skills_lower = [s.lower() for s in skills]
    
    # Define role requirements (based on skill combinations)
    
    # AI/ML Engineer - requires ML/AI skills
    ai_ml_skills = {
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "nlp", "computer vision", "opencv", "huggingface"
    }
    data_skills = {"pandas", "numpy", "matplotlib", "seaborn", "plotly", "data analysis"}
    
    ai_ml_count = sum(1 for skill in skills_lower if skill in ai_ml_skills)
    data_count = sum(1 for skill in skills_lower if skill in data_skills)
    
    if ai_ml_count >= 2:
        if data_count >= 2:
            return "AI/ML Engineer & Data Scientist"
        return "AI/ML Engineer"
    
    if data_count >= 3:
        return "Data Scientist"
    
    # Frontend Developer - requires frontend frameworks/languages
    frontend_skills = {
        "html", "css", "javascript", "typescript", "react", "nextjs",
        "vue", "angular", "svelte", "tailwind", "bootstrap", "material ui"
    }
    frontend_count = sum(1 for skill in skills_lower if skill in frontend_skills)
    
    # Backend Developer - requires backend frameworks
    backend_skills = {
        "python", "java", "nodejs", "express", "django", "flask",
        "fastapi", "asp.net", "php", "ruby", "golang", "rust"
    }
    backend_count = sum(1 for skill in skills_lower if skill in backend_skills)
    
    # Database skills
    db_skills = {
        "sql", "mysql", "postgresql", "mongodb", "redis", "dynamodb",
        "elasticsearch", "cassandra"
    }
    db_count = sum(1 for skill in skills_lower if skill in db_skills)
    
    # DevOps/Cloud skills
    devops_skills = {
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "jenkins", "ci/cd", "git", "github", "gitlab", "bitbucket"
    }
    devops_count = sum(1 for skill in skills_lower if skill in devops_skills)
    
    # Full Stack - has both frontend and backend
    if frontend_count >= 2 and backend_count >= 2:
        if devops_count >= 2:
            return "Full Stack Developer & DevOps Engineer"
        return "Full Stack Developer"
    
    # Frontend Developer
    if frontend_count >= 3:
        if devops_count >= 1:
            return "Frontend Developer & DevOps Engineer"
        return "Frontend Developer"
    
    # Backend Engineer
    if backend_count >= 2:
        if devops_count >= 2:
            return "Backend Engineer & DevOps Engineer"
        if db_count >= 2:
            return "Backend Engineer & Database Specialist"
        return "Backend Engineer"
    
    # DevOps/Cloud Engineer
    if devops_count >= 3:
        return "DevOps/Cloud Engineer"
    
    # Database Specialist
    if db_count >= 3:
        return "Database Administrator"
    
    # Default classification based on single strongest area
    if frontend_count > backend_count and frontend_count > 0:
        return "Frontend Developer"
    elif backend_count > frontend_count and backend_count > 0:
        return "Backend Engineer"
    elif devops_count > 0:
        return "DevOps Engineer"
    elif db_count > 0:
        return "Database Specialist"
    
    # Fallback
    return "Software Developer"