import csv
from pathlib import Path

import httpx


FILES_DIR = "notes_files"
FILE = "second_brain_notes_chatgpt.csv"
file_path = Path(FILES_DIR) / FILE


with open(file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        note = row["note"].strip()
        if note:
            response = httpx.post("http://localhost:8000/notes", json={"content": note})
            print(response.status_code)
            print(response.text)
