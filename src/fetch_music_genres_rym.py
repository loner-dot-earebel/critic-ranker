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

def search_musicbrainz(title, artist):
    url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "query": f'release:"{title}" AND artist:"{artist}"',
        "fmt": "json",
        "limit": 1
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    releases = data.get("releases", [])
    if not releases:
        return None

    return releases[0].get("id")
    
def get_rym_from_mb(release_id):
    url = f"https://musicbrainz.org/ws/2/release/{release_id}"
    params = {"inc": "url-rels", "fmt": "json"}

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return None

    for rel in data.get("relations", []):
        if rel.get("type") == "rateyourmusic":
            return rel.get("url", {}).get("resource")

    return None


# -------------------------
# Search DuckDuckGo for RYM release page
# -------------------------
def search_rym(title, artist):
    mb_id = search_musicbrainz(title, artist)
    if not mb_id:
        return None

    return get_rym_from_mb(mb_id)



# -------------------------
# Extract genres from album page
# -------------------------
def fetch_genres(album_url):
    try:
        r = requests.get(album_url, headers=HEADERS, timeout=10)
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

        time.sleep(0.3)

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_GENRES, index=False)
        print(f"Saved RYM genres: {OUTPUT_GENRES} ({len(df)} rows)")
    else:
        print("No RYM genres collected")

# -------------------------
if __name__ == "__main__":
    main()
