"""
Test script to validate the skill extraction fixes.
This demonstrates that the bug is fixed:
- "java" no longer matches inside "javascript"
- Multi-word skills like "machine learning" and "power bi" are detected
- Modern technologies (HTML, CSS, Django, Git) are properly detected
"""

import sys
sys.path.insert(0, '/utils')

from utils.skills import extract_skills, extract_skills_with_context
from utils.role_classifier import classify_role

# Test Case 1: Original Issue - "java" should NOT be detected from "javascript"
print("=" * 60)
print("TEST 1: Verify 'java' is NOT detected from 'javascript'")
print("=" * 60)

test_text_1 = """
Experience with JavaScript, Node.js, and web development.
"""
skills_1 = extract_skills(test_text_1)
print(f"Text: {test_text_1.strip()}")
print(f"Detected Skills: {skills_1}")
print(f"'java' in detected skills: {'java' in skills_1}")  # Should be False
print(f"'javascript' in detected skills: {'javascript' in skills_1}")  # Should be True
assert 'java' not in skills_1, "ERROR: 'java' was detected from 'javascript'!"
assert 'javascript' in skills_1, "ERROR: 'javascript' was not detected!"
print("✅ PASS: java correctly NOT detected from javascript\n")

# Test Case 2: Multi-word skills detection
print("=" * 60)
print("TEST 2: Multi-word skills detection")
print("=" * 60)

test_text_2 = """
Expertise in machine learning, deep learning, and data analysis.
Experience with Power BI and Tableau for visualization.
"""
skills_2 = extract_skills(test_text_2)
print(f"Text: {test_text_2.strip()}")
print(f"Detected Skills: {skills_2}")
assert 'machine learning' in skills_2, "ERROR: 'machine learning' not detected!"
assert 'deep learning' in skills_2, "ERROR: 'deep learning' not detected!"
assert 'data analysis' in skills_2, "ERROR: 'data analysis' not detected!"
assert 'power bi' in skills_2, "ERROR: 'power bi' not detected!"
print("✅ PASS: All multi-word skills correctly detected\n")

# Test Case 3: Original User Problem - JD with HTML, CSS, JavaScript, Django, Git
print("=" * 60)
print("TEST 3: Original User Problem - JD skills detection")
print("=" * 60)

jd_text = """
Required Skills:
- HTML/CSS
- JavaScript/TypeScript
- Django Framework
- Git Version Control
- RESTful API Design
"""

jd_skills = extract_skills(jd_text)
print(f"Job Description:\n{jd_text}")
print(f"Detected JD Skills: {jd_skills}")
assert 'html' in jd_skills, "ERROR: 'html' not detected!"
assert 'css' in jd_skills, "ERROR: 'css' not detected!"
assert 'javascript' in jd_skills, "ERROR: 'javascript' not detected!"
assert 'django' in jd_skills, "ERROR: 'django' not detected!"
assert 'git' in jd_skills, "ERROR: 'git' not detected!"
assert 'java' not in jd_skills, "ERROR: False positive 'java' detected!"
print("✅ PASS: All JD skills correctly detected\n")

# Test Case 4: Resume with only Python and FastAPI
print("=" * 60)
print("TEST 4: Resume skills detection")
print("=" * 60)

resume_text = """
Skills:
- Python 3.9
- FastAPI
- PostgreSQL
- Docker
"""

resume_skills = extract_skills(resume_text)
print(f"Resume:\n{resume_text}")
print(f"Detected Resume Skills: {resume_skills}")
assert 'python' in resume_skills, "ERROR: 'python' not detected!"
assert 'fastapi' in resume_skills, "ERROR: 'fastapi' not detected!"
assert 'postgresql' in resume_skills, "ERROR: 'postgresql' not detected!"
assert 'docker' in resume_skills, "ERROR: 'docker' not detected!"
print("✅ PASS: All resume skills correctly detected\n")

# Test Case 5: Skill matching (the actual bug scenario)
print("=" * 60)
print("TEST 5: Skill matching - Matched vs Missing")
print("=" * 60)

jd_skills_set = set(jd_skills)
resume_skills_set = set(resume_skills)

matched = jd_skills_set & resume_skills_set
missing = jd_skills_set - resume_skills_set

print(f"JD Skills: {sorted(jd_skills_set)}")
print(f"Resume Skills: {sorted(resume_skills_set)}")
print(f"Matched Skills: {sorted(matched) if matched else 'None'}")
print(f"Missing Skills: {sorted(missing)}")

# Expected results
print("\nExpected Results:")
print("- Matched: [] (no overlap)")
print("- Missing: ['css', 'django', 'git', 'html', 'javascript', 'rest api', 'typescript']")

assert 'python' not in missing, "ERROR: 'python' should be matched, not missing!"
assert 'html' in missing, "ERROR: 'html' should be missing!"
assert 'css' in missing, "ERROR: 'css' should be missing!"
assert 'javascript' in missing, "ERROR: 'javascript' should be missing!"
assert 'django' in missing, "ERROR: 'django' should be missing!"
assert 'git' in missing, "ERROR: 'git' should be missing!"
assert 'java' not in missing, "ERROR: 'java' should NOT be in missing!"
print("✅ PASS: Skill matching works correctly\n")

# Test Case 6: Role Classification
print("=" * 60)
print("TEST 6: Role Classification")
print("=" * 60)

# Backend Engineer
backend_skills = extract_skills("""
Python, Django, FastAPI, Flask, PostgreSQL, MongoDB, AWS, Docker
""")
role_1 = classify_role(backend_skills)
print(f"Backend Skills: {sorted(backend_skills)}")
print(f"Classified Role: {role_1}")
assert "Backend" in role_1 or "backend" in role_1.lower(), f"ERROR: Backend engineer not detected! Got: {role_1}"
print("✅ PASS: Backend engineer correctly classified\n")

# Frontend Developer
frontend_skills = extract_skills("""
HTML, CSS, JavaScript, TypeScript, React, Vue, Tailwind CSS
""")
role_2 = classify_role(frontend_skills)
print(f"Frontend Skills: {sorted(frontend_skills)}")
print(f"Classified Role: {role_2}")
assert "Frontend" in role_2 or "frontend" in role_2.lower(), f"ERROR: Frontend developer not detected! Got: {role_2}"
print("✅ PASS: Frontend developer correctly classified\n")

# Full Stack Developer
fullstack_skills = extract_skills("""
HTML, CSS, JavaScript, React, Python, Django, PostgreSQL, Docker, Git
""")
role_3 = classify_role(fullstack_skills)
print(f"Full Stack Skills: {sorted(fullstack_skills)}")
print(f"Classified Role: {role_3}")
assert "Full Stack" in role_3 or "full stack" in role_3.lower(), f"ERROR: Full stack developer not detected! Got: {role_3}"
print("✅ PASS: Full stack developer correctly classified\n")

# AI/ML Engineer
ai_skills = extract_skills("""
Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn
""")
role_4 = classify_role(ai_skills)
print(f"AI/ML Skills: {sorted(ai_skills)}")
print(f"Classified Role: {role_4}")
assert "AI" in role_4 or "ML" in role_4 or "Data Scientist" in role_4, f"ERROR: AI/ML engineer not detected! Got: {role_4}"
print("✅ PASS: AI/ML engineer correctly classified\n")

# Test Case 7: Skill categorization
print("=" * 60)
print("TEST 7: Skill Categorization")
print("=" * 60)

mixed_text = """
Python, JavaScript, React, Django, PostgreSQL, Docker, TensorFlow, Pandas
"""
result = extract_skills_with_context(mixed_text)
print(f"Text: {mixed_text}")
print(f"Total Skills Found: {result['count']}")
print(f"Skills by Category:")
for category, skills in result['categories'].items():
    if skills:
        print(f"  {category}: {skills}")

assert result['count'] > 0, "ERROR: No skills detected!"
assert len(result['categories']['frontend']) > 0, "ERROR: Frontend skills not categorized!"
assert len(result['categories']['backend']) > 0, "ERROR: Backend skills not categorized!"
assert len(result['categories']['ai_ml']) > 0, "ERROR: AI/ML skills not categorized!"
print("✅ PASS: Skill categorization works correctly\n")

print("=" * 60)
print("🎉 ALL TESTS PASSED! The fixes work correctly!")
print("=" * 60)
