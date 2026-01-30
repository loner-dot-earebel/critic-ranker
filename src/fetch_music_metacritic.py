import requests
import pandas as pd
import time
from pathlib import Path

OUTPUT_CSV = Path("outputs/music_metacritic_ranked.csv")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_with_retries(url, max_retries=3, backoff=5, timeout=10):
    attempt = 0
    while attempt < max_retries:
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Request failed (attempt {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                print(f"Max retries reached for URL: {url}")
                return None
            sleep_time = backoff * attempt
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

def fetch_page(page):
    url = f"https://www.metacritic.com/browse/albums/release-date/new-releases/all/date?page={page}"
    r = fetch_with_retries(url)
    if r is None:
        return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "lxml")
    rows = []
    for item in soup.select(".product_wrap"):
        title_tag = item.select_one(".product_title a")
        artist_tag = item.select_one(".product_artist")
        score_tag = item.select_one(".metascore_w")

        if title_tag and score_tag and score_tag.text.strip().isdigit():
            title = title_tag.text.strip()

            artist = None
            if artist_tag:
                artist = artist_tag.text.strip()
                if artist.lower().startswith("by "):
                    artist = artist[3:].strip()

            rows.append({
                "title": title,
                "artist": artist,
                "score": int(score_tag.text.strip())
            })

    print(f"Items found on page {page}: {len(rows)}")
    return rows

def main():
    print("=== fetch_music_metacritic.py STARTED ===")
    all_rows = []
    for page in range(2):  # first 2 pages for demo
        rows = fetch_page(page)
        all_rows.extend(rows)
        time.sleep(1)  # polite delay
    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved music CSV: {OUTPUT_CSV} ({len(df)} rows)")
    else:
        print("No music data collected")

if __name__ == "__main__":
    main()
