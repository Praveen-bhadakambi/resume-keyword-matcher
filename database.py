import sqlite3

# Create connection
conn = sqlite3.connect("resumes.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_name TEXT,
    ats REAL,
    tfidf REAL,
    semantic REAL
)
""")

conn.commit()