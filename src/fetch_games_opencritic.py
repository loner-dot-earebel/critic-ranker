import csv
import requests
import time
from pathlib import Path

OUTPUT_FILE = Path("data/games.csv")
BASE_URL = "https://api.opencritic.com/api/game"
PAGE_SIZE = 50
MAX_PAGES = 20   # ~1000 games; increase later if desired
SLEEP_SECONDS = 0.5

def fetch_page(page: int):
    params = {
        "skip": page * PAGE_SIZE,
        "limit": PAGE_SIZE,
        "sort": "score",
        "order": "desc"
    }
    resp = requests.get(BASE_URL, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()

def main():
    print("=== fetch_games_opencritic.py STARTED ===")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    seen_titles = set()

    for page in range(MAX_PAGES):
        print(f"Fetching OpenCritic page {page}")
        games = fetch_page(page)

        if not games:
            print("No more data returned.")
            break

        for g in games:
            title = g.get("name")
            if not title or title in seen_titles:
                continue

            score = g.get("medianScore") or g.get("topCriticScore")
            if score is None:
                continue

            rows.append({
                "title": title,
                "score": round(score, 1),
                "num_critics": g.get("numReviews"),
                "release_year": g.get("firstReleaseDate", "")[:4],
                "source": "OpenCritic"
            })

            seen_titles.add(title)

        time.sleep(SLEEP_SECONDS)

    print(f"Collected {len(rows)} games")

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "title",
                "score",
                "num_critics",
                "release_year",
                "source"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
