import os
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool
import random

class QuizManager:
    def __init__(self):
        self.database_url = os.environ['DATABASE_URL']
        self.pool = SimpleConnectionPool(1, 20, self.database_url)

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        self.pool.putconn(conn)

    def lade_fragen(self, lernfeld: str):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT q.*, array_agg(a.antwort) as antworten,
                           array_position(array_agg(a.antwort), 
                                        (SELECT antwort FROM quiz_answers 
                                         WHERE question_id = q.id AND is_correct = true LIMIT 1)) - 1 as richtig
                    FROM quiz_questions q
                    JOIN quiz_answers a ON a.question_id = q.id
                    WHERE q.lernfeld = %s
                    GROUP BY q.id
                """, (lernfeld,))
                return [dict(row) for row in cur.fetchall()]

    def speichere_fortschritt(self, user_id: int, lernfeld: str, richtig: bool):
        # Konvertiere bool zu int (True = 1, False = 0)
        richtig_int = 1 if richtig else 0
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO quiz_progress (user_id, lernfeld, gesamt, richtig)
                    VALUES (%s, %s, 1, %s)
                    ON CONFLICT (user_id, lernfeld) 
                    DO UPDATE SET 
                        gesamt = quiz_progress.gesamt + 1,
                        richtig = quiz_progress.richtig + CASE WHEN %s = 1 THEN 1 ELSE 0 END
                """, (user_id, lernfeld, richtig_int, richtig_int))

    def hole_statistik(self, user_id: int):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT lernfeld, gesamt, richtig
                    FROM quiz_progress
                    WHERE user_id = %s
                """, (user_id,))
                return {row['lernfeld']: {'gesamt': row['gesamt'], 'richtig': row['richtig']}
                        for row in cur.fetchall()}

    def hole_alle_fragen(self, lernfeld: str, anzahl: int = 5):
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT q.*, array_agg(a.antwort) as antworten,
                           array_position(array_agg(a.antwort), 
                                        (SELECT antwort FROM quiz_answers 
                                         WHERE question_id = q.id AND is_correct = true LIMIT 1)) - 1 as richtig
                    FROM quiz_questions q
                    JOIN quiz_answers a ON a.question_id = q.id
                    WHERE q.lernfeld = %s
                    GROUP BY q.id
                """, (lernfeld,))
                fragen = [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
        
        if len(fragen) > anzahl:
            return random.sample(fragen, anzahl)
        return fragen