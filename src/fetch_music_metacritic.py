import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

BASE_URL = "https://www.metacritic.com/browse/albums/score/metascore/all/filtered"
OUTPUT_FILE = "outputs/music_metacritic_ranked.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_PAGES = 5  # start small; can be increased safely later


def fetch_page(page):
    url = f"{BASE_URL}?page={page}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    rows = []

    for item in soup.select("td.clamp-summary-wrap"):
        title = item.select_one("a.title h3")
        score = item.select_one("div.metascore_w")
        artist = item.select_one("div.artist")

        if not title or not score:
            continue

        rows.append({
            "title": title.text.strip(),
            "artist": artist.text.strip() if artist else "",
            "critic_score": int(score.text.strip()),
            "medium": "music"
        })

    return rows


def main():
    all_rows = []

    for page in range(MAX_PAGES):
        print(f"Fetching music page {page}")
        rows = fetch_page(page)
        all_rows.extend(rows)
        time.sleep(2)

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("No music data collected")
        return

    df = df.drop_duplicates(subset=["title", "artist"])
    df = df.sort_values("critic_score", ascending=False)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} music albums")


if __name__ == "__main__":
    main()
