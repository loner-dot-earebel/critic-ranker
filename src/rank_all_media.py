import pandas as pd

# Placeholder fetch functions
# These will just load sample data for now
def fetch_movies_tv():
    return pd.DataFrame(columns=["title", "medium", "critic_score", "genres"])

def fetch_games():
    return pd.DataFrame(columns=["title", "medium", "critic_score", "genres"])

def fetch_music():
    return pd.DataFrame(columns=["title", "medium", "critic_score", "genres"])

def fetch_podcasts():
    return pd.DataFrame(columns=["title", "medium", "critic_score", "genres"])

def fetch_books():
    return pd.DataFrame(columns=["title", "medium", "critic_score", "genres"])

def normalize_all_media(df):
    df["score_norm"] = 50  # placeholder
    df["percentile"] = 50
    df["composite_score"] = 50
    return df

def filter_comedy(df):
    return df[df["genres"].str.contains("comedy|humor", case=False, na=False)]

def main():
    movies_tv = fetch_movies_tv()
    games = fetch_games()
    music = fetch_music()
    podcasts = fetch_podcasts()
    books = fetch_books()

    all_media = pd.concat([movies_tv, games, music, podcasts, books], ignore_index=True)
    ranked = normalize_all_media(all_media)

    ranked.to_csv("outputs/critics_all_media_ranked.csv", index=False)

    comedy = filter_comedy(ranked)
    comedy.to_csv("outputs/critics_comedy_humor_ranked.csv", index=False)

if __name__ == "__main__":
    main()
