
import os
from pathlib import Path

# Paths
DATA_DIR = Path("data")
TEMPLATE_DIR = Path("templates")
FRAGEN_FILE = DATA_DIR / "fragen.json"
FORTSCHRITT_FILE = DATA_DIR / "fortschritt.json"

# Server
PORT = 8080
HOST = "0.0.0.0"

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
