import pandas as pd
from pathlib import Path

# Paths to your scored media CSVs
MOVIES_CSV = Path("outputs/critics_all_media_ranked.csv")
MUSIC_CSV = Path("outputs/music_metacritic_ranked.csv")
GAMES_CSV = Path("data/games.csv")
TV_CSV = Path("src/seeds/movies_tv.csv")  # TV series included structurally

# Output paths
OUTPUT_ALL = Path("outputs/critics_all_media_merged.csv")
OUTPUT_COMEDY = Path("outputs/critics_comedy_humor_merged.csv")

def load_movies():
    if not MOVIES_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(MOVIES_CSV)
    df["medium"] = "movie"
    df["critic_score"] = pd.to_numeric(df.get("critic_score", 0), errors="coerce")
    return df

def load_music():
    if not MUSIC_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(MUSIC_CSV)
    df["medium"] = "music"
    df.rename(columns={"score": "critic_score"}, inplace=True)
    df["critic_score"] = pd.to_numeric(df.get("critic_score", 0), errors="coerce")
    return df

def load_games():
    if not GAMES_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(GAMES_CSV)
    df["medium"] = "game"
    df.rename(columns={"score": "critic_score"}, inplace=True)
    df["critic_score"] = pd.to_numeric(df.get("critic_score", 0), errors="coerce")
    return df

def load_tv():
    if not TV_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(TV_CSV)
    df["medium"] = "series"
    df["critic_score"] = pd.NA  # No reliable scores yet
    return df

def main():
    # Load all data
    movies = load_movies()
    music = load_music()
    games = load_games()
    tv = load_tv()

    print(f"Movies: {len(movies)}, Music: {len(music)}, Games: {len(games)}, TV: {len(tv)}")

    # Combine all
    combined = pd.concat([movies, music, games, tv], ignore_index=True)

    # Drop rows without critic_score for ranking
    ranked = combined.dropna(subset=["critic_score"]).sort_values("critic_score", ascending=False)

    # Save full merged dataset
    combined.to_csv(OUTPUT_ALL, index=False)
    print(f"Saved merged dataset: {OUTPUT_ALL} ({len(combined)} rows)")

    # Optionally, filter Comedy/Humor
    if "genres" in combined.columns:
        comedy_mask = combined["genres"].str.lower().str.contains("comedy|humor|satire", na=False)
        combined[comedy_mask].to_csv(OUTPUT_COMEDY, index=False)
        print(f"Saved comedy/humor dataset: {OUTPUT_COMEDY} ({comedy_mask.sum()} rows)")

if __name__ == "__main__":
    main()
