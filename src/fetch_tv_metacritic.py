import os
import time
import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

SEED_FILE = "src/seeds/tv_metacritic.csv"
OUTPUT_FILE = "outputs/tv_critics_metacritic.csv"

HEADERS = {
    "User-Agent": "critic-ranker/1.0 (non-commercial research)"
}

def slugify(title):
    title = title.lower()
    title = re.sub(r"[^\w\s-]", "", title)
    title = re.sub(r"\s+", "-", title)
    return title.strip("-")

def fetch_metacritic_tv(title, year):
    slug = slugify(title)
    url = f"https://www.metacritic.com/tv/{slug}"

    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    score_tag = soup.find("span", class_="metascore")

    if not score_tag:
        return None

    try:
        score = int(score_tag.text.strip())
    except ValueError:
        return None

    return {
        "title": title,
        "year": year,
        "critic_score": score,
        "source": "metacritic_tv"
    }

def main():
    os.makedirs("outputs", exist_ok=True)

    rows = []

    with open(SEED_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print("Fetching:", row["title"])
            result = fetch_metacritic_tv(row["title"], row["year_hint"])
            if result:
                rows.append(result)
            time.sleep(5)  # rate limit

    if not rows:
        print("No TV critic data found")
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()
