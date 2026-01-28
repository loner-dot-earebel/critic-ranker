import pandas as pd
from pathlib import Path

# Paths to your scored media CSVs
MOVIES_CSV = Path("outputs/critics_all_media_ranked.csv")
MUSIC_CSV = Path("outputs/music_metacritic_ranked.csv")
GAMES_CSV = Path("data/games.csv")
#TV_CSV = Path("src/seeds/movies_tv.csv")  # TV series included structurally

# Output paths
OUTPUT_ALL = Path("outputs/critics_all_media_merged.csv")
OUTPUT_COMEDY = Path("outputs/critics_comedy_humor_merged.csv")

def load_movies():
    if not MOVIES_CSV.exists():
        print(f"WARNING: Movies CSV not found at {MOVIES_CSV}")
        return pd.DataFrame()
    df = pd.read_csv(MOVIES_CSV)
    df["medium"] = "movie"  # Force correct medium
    df["critic_score"] = pd.to_numeric(df.get("critic_score", None), errors="coerce")
    return df

def load_music():
    if not MUSIC_CSV.exists():
        print(f"WARNING: Music CSV not found at {MUSIC_CSV}")
        return pd.DataFrame()
    df = pd.read_csv(MUSIC_CSV)
    df["medium"] = "music"
    df.rename(columns={"score": "critic_score"}, inplace=True)
    df["critic_score"] = pd.to_numeric(df.get("critic_score", None), errors="coerce")
    return df

def load_games():
    if not GAMES_CSV.exists():
        print(f"WARNING: Games CSV not found at {GAMES_CSV}")
        return pd.DataFrame()
    df = pd.read_csv(GAMES_CSV)
    df["medium"] = "game"
    df.rename(columns={"score": "critic_score"}, inplace=True)
    df["critic_score"] = pd.to_numeric(df.get("critic_score", None), errors="coerce")
    return df

#def load_tv():
#    if not TV_CSV.exists():
#        print(f"WARNING: TV CSV not found at {TV_CSV}")
#        return pd.DataFrame()
#    df = pd.read_csv(TV_CSV)
#    df["medium"] = "series"  # Force TV medium
#    df["critic_score"] = pd.NA  # No reliable scores yet
#    return df

def print_medium_counts(df, label):
    if df.empty:
        print(f"{label}: No rows")
        return
    counts = df["medium"].value_counts()
    print(f"{label} medium counts:")
    for medium, count in counts.items():
        print(f"  {medium}: {count}")

def main():
    print("=== merge_all_critics.py STARTED ===")

    # Load all data
    movies = load_movies()
    music = load_music()
    games = load_games()
#    tv = load_tv()

    # Debug: show counts before merging
    print_medium_counts(movies, "Movies")
    print_medium_counts(music, "Music")
    print_medium_counts(games, "Games")
#    print_medium_counts(tv, "TV series")

    # Combine all
#    combined = pd.concat([movies, music, games, tv], ignore_index=True)
    combined = pd.concat([movies, music, games], ignore_index=True)

    
    # Debug: counts after merging
    print_medium_counts(combined, "Combined dataset")

    # Drop rows without critic_score for ranking
    ranked = combined.dropna(subset=["critic_score"]).sort_values("critic_score", ascending=False)

    print(f"Rows after dropping missing scores: {len(ranked)}")

    # Save full merged dataset (includes TV structurally)
    combined.to_csv(OUTPUT_ALL, index=False)
    print(f"Saved merged dataset: {OUTPUT_ALL} ({len(combined)} rows)")

    # Comedy/Humor filter
    if "genres" in combined.columns:
        comedy_mask = combined["genres"].str.lower().str.contains("comedy|humor|satire", na=False)
        combined[comedy_mask].to_csv(OUTPUT_COMEDY, index=False)
        print(f"Saved comedy/humor dataset: {OUTPUT_COMEDY} ({comedy_mask.sum()} rows)")
    else:
        print("No 'genres' column found; skipping comedy/humor CSV")

if __name__ == "__main__":
    main()
