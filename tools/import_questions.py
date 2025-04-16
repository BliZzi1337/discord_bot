
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quiz_manager import QuizManager

def import_questions():
    with open('data/fragen.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    manager = QuizManager()
    conn = manager.get_connection()
    cur = conn.cursor()
    
    try:
        print(f"📚 Starte Import von {len(questions)} Fragen...")
        for question in questions:
            # Check if question already exists
            cur.execute("""
                SELECT id FROM quiz_questions 
                WHERE frage = %s AND lernfeld = %s
            """, (question['frage'], question['lernfeld']))
            
            existing = cur.fetchone()
            
            if existing:
                # Update existing question
                question_id = existing[0]
                print(f"🔄 Aktualisiere Frage: {question['frage'][:50]}...")
                cur.execute("""
                    UPDATE quiz_questions 
                    SET punkte = %s
                    WHERE id = %s
                """, (question['punkte'], question_id))
                
                # Delete old answers
                cur.execute("DELETE FROM quiz_answers WHERE question_id = %s", (question_id,))
            else:
                # Insert new question
                print(f"➕ Neue Frage: {question['frage'][:50]}...")
                cur.execute("""
                    INSERT INTO quiz_questions (frage, lernfeld, punkte)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (question['frage'], question['lernfeld'], question['punkte']))
                question_id = cur.fetchone()[0]
            
            # Insert answers
            for i, answer in enumerate(question['antworten']):
                cur.execute("""
                    INSERT INTO quiz_answers (question_id, antwort, is_correct)
                    VALUES (%s, %s, %s)
                """, (question_id, answer, i == question['richtig']))
        
        conn.commit()
        print("✅ Alle Fragen erfolgreich importiert/aktualisiert!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Fehler beim Import: {e}")
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import_questions()
