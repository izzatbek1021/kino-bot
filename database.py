import sqlite3

conn = sqlite3.connect("kino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")

conn.commit()

def add_movie(code, file_id):
    cursor.execute("INSERT INTO movies (code, file_id) VALUES (?, ?)", (code, file_id))
    conn.commit()

def get_movie(code):
    cursor.execute("SELECT file_id FROM movies WHERE code=?", (code,))
    return cursor.fetchone()

def delete_movie(code):
    cursor.execute("DELETE FROM movies WHERE code=?", (code,))
    conn.commit()

def count_movies():
    cursor.execute("SELECT COUNT(*) FROM movies")
    return cursor.fetchone()[0]