print("=== rank_all_media.py STARTED ===")

import os
import csv
import requests
import pandas as pd

import re

def normalize_title(title):
    return re.sub(r"\s*\(.*?\)", "", title).strip()


OMDB_API_KEY = os.getenv("OMDB_API_KEY")

SEED_FILE = "src/seeds/movies_tv.csv"
OUTPUT_ALL = "outputs/critics_all_media_ranked.csv"
OUTPUT_COMEDY = "outputs/critics_comedy_humor_ranked.csv"


def fetch_omdb(title, media_type, year_hint=None):
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "type": "series" if media_type.lower() in ("tv", "series", "tv_series", "miniseries") else "movie",
        "r": "json"
    }
    if year_hint:
        params["y"] = year_hint

    r = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
    data = r.json()

    if data.get("Response") != "True":
    # Retry without type constraint
        params.pop("type", None)
        r = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
        data = r.json()

    if data.get("Response") != "True":
        return None


    metacritic = data.get("Metascore")
    critic_score = int(metacritic) if metacritic not in (None, "N/A") else None


    return {
        "title": data.get("Title"),
        "medium": media_type,
        "year": data.get("Year"),
        "critic_score": critic_score,
        "genres": data.get("Genre", "")
    }


def main():
    print("=== ENTERED main() ===")
    print("Seed file path:", SEED_FILE)
    print("Seed file exists:", os.path.exists(SEED_FILE))
    print("OMDB_API_KEY present:", bool(OMDB_API_KEY))
    os.makedirs("outputs", exist_ok=True)

    rows = []

    with open(SEED_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows_in_seed = list(reader)
        print("Rows in seed CSV:", len(rows_in_seed))

        for row in rows_in_seed:
            if row["type"] != "movie":
                continue

            result = fetch_omdb(
                normalize_title(row["title"]),
                row["type"],
                row.get("year_hint")
            )
   

            if result is None:
                print("NOT FOUND:", row["title"])
            else:
                if result["critic_score"] is None:
                    print("FOUND, NO METASCORE:", result["title"])
                rows.append(result)



    df = pd.DataFrame(rows)

    if df.empty:
        print("No valid rows returned from OMDb")
        return

# Drop entries without a critic score
    df = df.dropna(subset=["critic_score"])

    if df.empty:
        print("All rows missing Metacritic scores")
        return

    df = df.sort_values("critic_score", ascending=False)


    df.to_csv(OUTPUT_ALL, index=False)

    comedy_mask = df["genres"].str.lower().str.contains(
        "comedy|humor|satire", na=False
    )
    df[comedy_mask].to_csv(OUTPUT_COMEDY, index=False)


if __name__ == "__main__":
    main()
