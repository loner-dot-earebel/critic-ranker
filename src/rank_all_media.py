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


def fetch_omdb(title, media_type):
    url = "https://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "type": media_type
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            print(f"OMDb HTTP error {r.status_code} for: {title}")
            return None

        try:
            data = r.json()
        except Exception:
            print(f"OMDb returned non-JSON for: {title}")
            print(r.text[:300])
            return None

        if data.get("Response") != "True":
            return None

        return data

    except requests.RequestException as e:
        print(f"OMDb request failed: {e}")
        return None



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
