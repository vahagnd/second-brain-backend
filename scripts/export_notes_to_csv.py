import csv
from datetime import datetime
from pathlib import Path

import httpx


BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
NOTES_ENDPOINT = f"{BASE_URL}{API_PREFIX}/notes"
OUTPUT_DIR = Path("notes_files")
PAGE_LIMIT = 100


def fetch_all_notes():
    page = 1
    while True:
        response = httpx.get(NOTES_ENDPOINT, params={"page": page, "limit": PAGE_LIMIT})
        response.raise_for_status()
        data = response.json()
        yield from data["items"]
        if page >= data["pages"]:
            break
        page += 1


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = OUTPUT_DIR / f"notes_{timestamp}.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "content"])
    writer.writeheader()
    for note in fetch_all_notes():
        writer.writerow({"id": note["id"], "content": note["content"]})

print(f"Exported notes to {output_file}")
