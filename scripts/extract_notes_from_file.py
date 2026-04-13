from pathlib import Path

import httpx

FILES_DIR = "notes_files"
FILE = ""


def notes_stream(file_path: Path):
    with file_path.open("r", encoding="utf-8") as f:
        current_note = []

        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("-"):
                if current_note:
                    yield " ".join(current_note)
                    current_note = []

                current_note.append(line.lstrip("- ").strip())
            else:
                current_note.append(line)

        if current_note:
            yield " ".join(current_note)


file_path = Path(FILES_DIR) / FILE

for note in notes_stream(file_path):
    httpx.post("http://localhost:8000/notes", json={"content": note})
