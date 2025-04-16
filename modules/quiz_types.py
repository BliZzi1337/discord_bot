
from typing import TypedDict, Literal

LernfeldID = Literal["LF1", "LF2", "LF3", "LF4", "LF5"]

class QuizQuestion(TypedDict):
    frage: str
    antworten: list[str] 
    richtig: int
    punkte: int
    lernfeld: LernfeldID

LF_MAPPING = {
    "LF1": "Lernfeld 1: Grundlagen der IT-Systeme",
    "LF2": "Lernfeld 2: Vernetzte Systeme einrichten", 
    "LF3": "Lernfeld 3: Systeme zur Datenverarbeitung",
    "LF4": "Lernfeld 4: IT-Sicherheit und Datenschutz",
    "LF5": "Lernfeld 5: Benutzerunterstützung und Support"
}

OPTION_LETTERS = ["A", "B", "C", "D"]
QUIZ_CHANNEL_ID = 1359197662443737400

async def setup(bot):
    pass
