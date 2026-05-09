import re
from typing import Set, List

# Comprehensive Technical Skills Database (50+ modern technologies)
SKILLS_DB = {
    # Frontend Technologies
    "html": r"\bhtml\b",
    "css": r"\bcss\b",
    "javascript": r"\bjavascript\b",
    "typescript": r"\btypescript\b",
    "react": r"\breact\b",
    "nextjs": r"\bnext\.?js\b|\bnextjs\b",
    "vue": r"\bvue\b",
    "angular": r"\bangular\b",
    "svelte": r"\bsvelte\b",
    "tailwind": r"\btailwind\b",
    "bootstrap": r"\bbootstrap\b",
    "material ui": r"\bmaterial\s+ui\b",
    
    # Backend & Server Technologies
    "python": r"\bpython\b",
    "java": r"\bjava\b(?!script)",  # Negative lookahead to avoid javascript
    "nodejs": r"\bnode\.?js\b|\bnodejs\b",
    "express": r"\bexpress\b",
    "django": r"\bdjango\b",
    "flask": r"\bflask\b",
    "fastapi": r"\bfastapi\b",
    "asp.net": r"\basp\.net\b|\basp\b",
    "php": r"\bphp\b",
    "ruby": r"\bruby\b",
    "golang": r"\bgo\b|\bgolang\b",
    "rust": r"\brust\b",
    
    # Databases
    "sql": r"\bsql\b",
    "mysql": r"\bmysql\b",
    "postgresql": r"\bpostgresql\b|\bpostgres\b",
    "mongodb": r"\bmongodb\b",
    "redis": r"\bredis\b",
    "dynamodb": r"\bdynamodb\b",
    "elasticsearch": r"\belasticsearch\b",
    "cassandra": r"\bcassandra\b",
    
    # Cloud & DevOps
    "aws": r"\baws\b",
    "azure": r"\bazure\b",
    "gcp": r"\bgcp\b|\bgoogle\s+cloud\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes\b|\bk8s\b",
    "terraform": r"\bterraform\b",
    "jenkins": r"\bjenkins\b",
    "ci/cd": r"\bci\s*\/\s*cd\b|\bcicd\b",
    "git": r"\bgit\b",
    "github": r"\bgithub\b",
    "gitlab": r"\bgitlab\b",
    "bitbucket": r"\bbitbucket\b",
    
    # AI & Machine Learning
    "machine learning": r"\bmachine\s+learning\b",
    "deep learning": r"\bdeep\s+learning\b",
    "tensorflow": r"\btensorflow\b",
    "pytorch": r"\bpytorch\b",
    "keras": r"\bkeras\b",
    "scikit-learn": r"\bscikit[\s-]?learn\b",
    "nlp": r"\bnlp\b|\bnatural\s+language\s+processing\b",
    "computer vision": r"\bcomputer\s+vision\b",
    "opencv": r"\bopencv\b",
    "huggingface": r"\bhuggingface\b",
    
    # Data Analysis & Visualization
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "matplotlib": r"\bmatplotlib\b",
    "seaborn": r"\bseaborn\b",
    "plotly": r"\bplotly\b",
    "power bi": r"\bpower\s+bi\b",
    "tableau": r"\btableau\b",
    "data analysis": r"\bdata\s+analysis\b",
    "etl": r"\betl\b",
    
    # Testing & QA
    "pytest": r"\bpytest\b",
    "unittest": r"\bunittest\b",
    "jest": r"\bjest\b",
    "mocha": r"\bmocha\b",
    "selenium": r"\bselenium\b",
    "postman": r"\bpostman\b",
    "jira": r"\bjira\b",
    
    # Other Technologies
    "rest api": r"\brest\s+api\b|\brestful\b",
    "graphql": r"\bgraphql\b",
    "api": r"\bapi\b",
    "linux": r"\blinux\b",
    "windows": r"\bwindows\b",
    "macos": r"\bmacos\b|\bmac\s+os\b",
    "soap": r"\bsoap\b",
    "xml": r"\bxml\b",
    "json": r"\bjson\b",
    "websocket": r"\bwebsocket\b",
    "microservices": r"\bmicroservices\b",
    "agile": r"\bagile\b",
    "scrum": r"\bscrum\b",
    "c++": r"\bc\+\+\b",
    "c#": r"\bc#\b",
}

def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from text using regex with word boundaries.
    
    Features:
    - Case-insensitive matching
    - Word boundary protection to avoid false positives
    - Multi-word skill support
    - No preprocessing (uses original text)
    
    Args:
        text: Raw text from resume or job description
        
    Returns:
        List of detected skills in lowercase
    """
    if not text:
        return []
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    found_skills: Set[str] = set()
    
    # Match skills using regex with word boundaries
    for skill, pattern in SKILLS_DB.items():
        try:
            # Use regex search with case-insensitive flag
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_skills.add(skill)
        except re.error:
            # Skip malformed regex patterns
            print(f"Warning: Malformed regex pattern for skill '{skill}'")
            continue
    
    # Return sorted list of found skills
    return sorted(list(found_skills))


def extract_skills_with_context(text: str) -> dict:
    """
    Extract skills and provide contextual information.
    
    Args:
        text: Raw text from resume or job description
        
    Returns:
        Dictionary with skills list and skill categories
    """
    skills = extract_skills(text)
    
    # Categorize skills
    categories = {
        "frontend": [],
        "backend": [],
        "database": [],
        "devops": [],
        "ai_ml": [],
        "data": [],
        "testing": [],
        "other": []
    }
    
    skill_categories_map = {
        "html": "frontend", "css": "frontend", "javascript": "frontend",
        "typescript": "frontend", "react": "frontend", "nextjs": "frontend",
        "vue": "frontend", "angular": "frontend", "svelte": "frontend",
        "tailwind": "frontend", "bootstrap": "frontend", "material ui": "frontend",
        
        "python": "backend", "java": "backend", "nodejs": "backend",
        "express": "backend", "django": "backend", "flask": "backend",
        "fastapi": "backend", "asp.net": "backend", "php": "backend",
        "ruby": "backend", "golang": "backend", "rust": "backend",
        "rest api": "backend", "graphql": "backend", "api": "backend",
        "soap": "backend", "microservices": "backend", "websocket": "backend",
        
        "sql": "database", "mysql": "database", "postgresql": "database",
        "mongodb": "database", "redis": "database", "dynamodb": "database",
        "elasticsearch": "database", "cassandra": "database",
        
        "aws": "devops", "azure": "devops", "gcp": "devops",
        "docker": "devops", "kubernetes": "devops", "terraform": "devops",
        "jenkins": "devops", "ci/cd": "devops", "git": "devops",
        "github": "devops", "gitlab": "devops", "bitbucket": "devops",
        "linux": "devops", "windows": "devops", "macos": "devops",
        
        "machine learning": "ai_ml", "deep learning": "ai_ml",
        "tensorflow": "ai_ml", "pytorch": "ai_ml", "keras": "ai_ml",
        "scikit-learn": "ai_ml", "nlp": "ai_ml", "computer vision": "ai_ml",
        "opencv": "ai_ml", "huggingface": "ai_ml",
        
        "pandas": "data", "numpy": "data", "matplotlib": "data",
        "seaborn": "data", "plotly": "data", "power bi": "data",
        "tableau": "data", "data analysis": "data", "etl": "data",
        
        "pytest": "testing", "unittest": "testing", "jest": "testing",
        "mocha": "testing", "selenium": "testing", "postman": "testing",
        "jira": "testing",
    }
    
    for skill in skills:
        category = skill_categories_map.get(skill, "other")
        categories[category].append(skill)
    
    return {
        "skills": skills,
        "count": len(skills),
        "categories": categories
    }