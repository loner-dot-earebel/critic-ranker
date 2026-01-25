import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

BASE_URL = "https://www.metacritic.com/browse/games/score/metascore/all/filtered"
OUTPUT_FILE = "outputs/games_metacritic_ranked.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml"
}

MAX_PAGES = 2  # safe for GitHub Actions


def fetch_page(page):
    url = f"{BASE_URL}?page={page}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching page {page}: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    print("Items found:", len(soup.select("div.clamp-summary-wrap")))

    rows = []

    for item in soup.select("div.clamp-summary-wrap"):
        title = item.select_one("a.title h3")
        score = item.select_one("div.metascore_w")
        platform = item.select_one("div.platform")

        if not title or not score:
            continue

        rows.append({
            "title": title.text.strip(),
            "platform": platform.text.strip() if platform else "",
            "critic_score": int(score.text.strip()),
            "medium": "game"
        })

    return rows


def main():
    all_rows = []

    for page in range(MAX_PAGES):
        print(f"Fetching games page {page}")
        rows = fetch_page(page)
        all_rows.extend(rows)
        time.sleep(2)

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("No game data collected")
        return

    df = df.drop_duplicates(subset=["title", "platform"])
    df = df.sort_values("critic_score", ascending=False)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df)} games")


if __name__ == "__main__":
    main()
