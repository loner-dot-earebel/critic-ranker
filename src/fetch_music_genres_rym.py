import requests
import pandas as pd
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

INPUT_MUSIC = Path("outputs/music_metacritic_ranked.csv")
OUTPUT_GENRES = Path("outputs/music_genres_rym.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

DEBUG_FILE = Path("debug_rym.html")

# -------------------------
# Search DuckDuckGo for RYM release page
# -------------------------
def search_rym(title, artist):
    query = f'site:rateyourmusic.com/release "{title}" "{artist}"'
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "lxml")

    for a in soup.select("a.result__a"):
        href = a.get("href", "")
        if "rateyourmusic.com/release" in href:
            return href

    return None

# -------------------------
# Extract genres from album page
# -------------------------
def fetch_genres(album_url):
    try:
        r = requests.get(album_url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException:
        return None

    # Always dump first page for debugging
    DEBUG_FILE.write_text(r.text, encoding="utf-8")

    soup = BeautifulSoup(r.text, "lxml")

    genres = set()

    for g in soup.select("a.genre"):
        text = g.text.strip()
        if text:
            genres.add(text)

    return ", ".join(sorted(genres)) if genres else None

# -------------------------
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
        print(f"  Found URL: {album_url}")

        if not album_url:
            continue

        genres = fetch_genres(album_url)

        print(f"  Genres: {genres}")

        if not genres:
            continue

        rows.append({
            "title": title,
            "artist": artist,
            "genres": genres
        })

        time.sleep(2)

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_GENRES, index=False)
        print(f"Saved RYM genres: {OUTPUT_GENRES} ({len(df)} rows)")
    else:
        print("No RYM genres collected")

# -------------------------
if __name__ == "__main__":
    main()
