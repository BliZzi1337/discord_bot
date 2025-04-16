
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    database_url = os.environ['DATABASE_URL']
    
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id SERIAL PRIMARY KEY,
            frage TEXT NOT NULL,
            lernfeld VARCHAR(10) NOT NULL,
            punkte INTEGER NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES quiz_questions(id),
            antwort TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_progress (
            user_id BIGINT NOT NULL,
            lernfeld VARCHAR(10) NOT NULL,
            gesamt INTEGER DEFAULT 0,
            richtig INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, lernfeld)
        )
    """)
    
    cur.close()
    conn.close()

async def setup(bot):
    setup_database()
