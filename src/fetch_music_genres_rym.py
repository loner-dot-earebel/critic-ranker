import requests
import pandas as pd
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup

INPUT_MUSIC = Path("outputs/music_metacritic_ranked.csv")
OUTPUT_GENRES = Path("outputs/music_genres_rym.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()

def search_rym(title, artist):
    query = f"{title} {artist}".strip()
    url = "https://rateyourmusic.com/search"
    params = {"searchterm": query, "type": "l"}

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "lxml")
    result = soup.select_one(".searchpage a")
    if not result or not result.get("href"):
        return None

    return "https://rateyourmusic.com" + result["href"]

def fetch_genres(album_url):
    try:
        r = requests.get(album_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "lxml")

    genres = set()

    # Primary genres
    for g in soup.select(".release_pri_genres a.genre"):
        genres.add(g.text.strip())

    # Secondary genres
    for g in soup.select(".release_sec_genres a.genre"):
        genres.add(g.text.strip())

    with open("debug_rym.html", "w", encoding="utf-8") as f:
        f.write(r.text)


    return ", ".join(sorted(genres)) if genres else None


def main():
    print("=== fetch_music_genres_rym.py STARTED ===")

    if not INPUT_MUSIC.exists():
        print("No music input file found.")
        return

    music = pd.read_csv(INPUT_MUSIC)
    rows = []

    for _, row in music.iterrows():
        title = str(row.get("title", "")).strip()
        artist = str(row.get("artist", "")).strip()

        if not title:
            continue

        print(f"RYM lookup: {title} – {artist}")

        album_url = search_rym(title, artist)
        if not album_url:
            continue

        genres = fetch_genres(album_url)
        if not genres:
            continue

        rows.append({
            "title": title,
            "artist": artist,
            "genres": genres
        })

        time.sleep(2)  # very polite

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_GENRES, index=False)
        print(f"Saved RYM genres: {OUTPUT_GENRES} ({len(df)} rows)")
    else:
        print("No RYM genres collected")

if __name__ == "__main__":
    main()
