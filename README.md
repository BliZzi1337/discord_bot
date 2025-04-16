# 🛠️ DAA Discord Bot

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Ein moderner, modular aufgebauter Discord-Bot für Fachinformatiker-Umschulungen und IT-Communities.  
Enthält Automatisierungen, Tools und Admin-Funktionen wie Byte-Umrechnung, Zahlensystem-Konvertierung, interaktives Quiz-System, automatische Voice-Channel-Verwaltung, geplante User-Verschiebungen und vieles mehr.

🌐 **Web-Interface:** [bot.blizzi1337.de](https://bot.blizzi1337.de)

## ⚙️ Features

| Funktion             | Beschreibung |
|----------------------|--------------|
| 🌐 Web-Interface     | Live-Status, Voice-Tracking und Quiz-Statistiken unter bot.blizzi1337.de |
| `/bytes`             | Byte, Kilo-, Mebi-, Gibi-Umrechnung mit Formeln & Rechenweg |
| `/convert`           | Binär/Dezimal/Hex-Umwandlung mit vollständigem Rechenweg |
| `/usv`               | Interaktive Berechnung von Kapazität, Watt, Zeit, Spannung, Akkus inkl. Formeln |
| `/verschieben`       | Admins verschieben alle aus eigenem Channel in Zielchannel |
| `/wheel`             | Interaktives Zufallsauswahl-Rad |
| `!move`              | Manuelles Verschieben mit Admincheck |
| ⏰ Auto-Move          | Automatische Voice-Verschiebung um 11:15 Uhr (Di–Fr) |
| ♻️ Voice-Auto-System  | Erstellt & löscht Voice-Talks automatisch – inkl. Logging |
| 🔄 Reorganisation     | Immer nur ein leerer Talk sichtbar, keine Doppelungen |
| 👀 Join-Logs          | Beitritte, Verlassen, Wechsel von Talk-Usern mit Zeitstempel |
| 🎮 Raider.IO         | Integration für WoW Charakterinfos und M+ Scores |
| 🧠 `/quiz`            | Interaktives Quizsystem nach Lernfeldern (Dropdown + Buttons) |
| 📊 Statistik-Button   | Zeigt den Lernfortschritt pro Lernfeld (richtig/gesamt, %) |
| 🧾 Fortschritt        | Punkte pro Frage, automatische Auswertung & Speicherfunktion |

## 📁 Projektstruktur

```bash
discord_bot/
├── main.py                 # Bot-Starter mit Status-Rotation, Cog-Loader
├── cogs/                  # Slash- und Textcommands
│   ├── convert_cog.py     # /convert: Zahlensysteme mit Rechenweg
│   ├── bytes_cog.py       # /bytes: Speichergrößen mit Rechenweg
│   ├── usv_cog.py         # /usv: USV-Rechner mit interaktivem UI & Formeln
│   ├── move_anywhere_cog.py # /verschieben: Admin verschiebt per Command 
│   ├── reload_cog.py      # /reload: Cogs neuladen (nur Owner)
│   ├── wheel_cog.py       # Zufallsauswahl-Rad
│   ├── raiderio_cog.py    # Raider.IO Integration
│   └── quiz_cog.py        # /quiz: Interaktives Quiz mit Lernfeldern
└── modules/               # Hintergrundfunktionen, Listener, Tasks
    ├── move.py            # Auto-Move 11:15 Uhr (Di–Fr) + !move
    ├── auto_voice.py      # Automatische Voice-Channel-Erstellung
    ├── websocket_handler.py # WebSocket für Live-Updates
    └── quiz_manager.py    # Verwaltung von Fragen und Fortschritt
```

## 🔧 Setup

1. Erstelle eine `.env` Datei mit den nötigen Tokens und IDs
2. Installiere die Abhängigkeiten: `pip install -r requirements.txt`
3. Starte den Bot: `python main.py`

## 🔐 Erforderliche Berechtigungen

- Nachrichten lesen & schreiben
- Mitglieder in Sprachkanälen verschieben
- Voice Intents aktiv
- Slash-Commands registrieren

## 👨‍💻 Entwickler

Chris aka **BliZzi1337**  
Betreut Discord-Server für Fachinformatiker, baut Lern-Tools & Discord-Bots mit ❤️

## 📜 Lizenz

Private Nutzung erlaubt – bitte nicht ungefragt kopieren oder veröffentlichen.