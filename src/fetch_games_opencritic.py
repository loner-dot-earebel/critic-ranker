import requests
import pandas as pd
import time
from pathlib import Path

OUTPUT_CSV = Path("data/games.csv")

BASE_URL = "https://api.opencritic.com/api/game"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_page(skip=0, limit=50):
    params = {
        "skip": skip,
        "limit": limit,
        "sort": "score",
        "order": "desc"
    }
    r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    rows = []
    for game in data:
        score = game.get("topCriticScore")
        if score is None:
            continue
        rows.append({
            "title": game.get("name"),
            "critic_score": round(score),
            "genres": ", ".join(game.get("Genres", [])) if game.get("Genres") else None
        })

    print(f"Fetched {len(rows)} games (skip={skip})")
    return rows

def main():
    print("=== fetch_games_opencritic.py STARTED ===")
    all_rows = []

    for skip in range(0, 200, 50):  # top ~200 games
        rows = fetch_page(skip=skip)
        all_rows.extend(rows)
        time.sleep(1)

    if not all_rows:
        print("No game data collected")
        return

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved games CSV: {OUTPUT_CSV} ({len(df)} rows)")

if __name__ == "__main__":
    main()
