import os
import csv
import requests
import pandas as pd

OMDB_API_KEY = os.getenv("OMDB_API_KEY")

SEED_FILE = "src/seeds/movies_tv.csv"
OUTPUT_ALL = "outputs/critics_all_media_ranked.csv"
OUTPUT_COMEDY = "outputs/critics_comedy_humor_ranked.csv"


def fetch_omdb(title, media_type, year_hint=None):
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "type": "series" if media_type == "series" else "movie",
        "r": "json"
    }
    if year_hint:
        params["y"] = year_hint

    r = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
    data = r.json()

    if data.get("Response") != "True":
        return None

    metacritic = data.get("Metascore")
    if metacritic in (None, "N/A"):
        return None

    return {
        "title": data.get("Title"),
        "medium": media_type,
        "year": data.get("Year"),
        "critic_score": int(metacritic),
        "genres": data.get("Genre", "")
    }


def main():
    os.makedirs("outputs", exist_ok=True)

    rows = []

    with open(SEED_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = fetch_omdb(
                row["title"],
                row["type"],
                row.get("year_hint")
            )
            if result:
                rows.append(result)

    df = pd.DataFrame(rows)

    if df.empty:
        return

    df = df.sort_values("critic_score", ascending=False)

    df.to_csv(OUTPUT_ALL, index=False)

    comedy_mask = df["genres"].str.lower().str.contains(
        "comedy|humor|satire", na=False
    )
    df[comedy_mask].to_csv(OUTPUT_COMEDY, index=False)


if __name__ == "__main__":
    main()
