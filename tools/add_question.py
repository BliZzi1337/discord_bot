import json
import os

FRAGEN_PFAD = os.path.join("data", "fragen.json")


def lade_fragen():
    if not os.path.exists(FRAGEN_PFAD):
        return {}
    with open(FRAGEN_PFAD, "r", encoding="utf-8") as f:
        return json.load(f)


def speichere_fragen(daten):
    os.makedirs(os.path.dirname(FRAGEN_PFAD), exist_ok=True)
    with open(FRAGEN_PFAD, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)


def frage_hinzufuegen():
    daten = lade_fragen()

    lernfeld = input("Für welches Lernfeld? (z.B. LF1): ").strip()
    frage_text = input("Frage: ").strip()

    antworten = []
    for i in range(4):
        antworten.append(input(f"Antwort {chr(65 + i)}: ").strip())

    richtig = input("Welche Antwort ist richtig? (A/B/C/D): ").strip().upper()
    richtig_index = ord(richtig) - 65

    punkte = int(input("Wie viele Punkte gibt diese Frage?: ").strip())

    frage_objekt = {
        "frage": frage_text,
        "antworten": antworten,
        "richtig": richtig_index,
        "punkte": punkte
    }

    if lernfeld not in daten:
        daten[lernfeld] = []

    daten[lernfeld].append(frage_objekt)
    speichere_fragen(daten)
    print("✅ Frage erfolgreich gespeichert.")


if __name__ == "__main__":
    frage_hinzufuegen()