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
    import pandas as pd

    # Make sure outputs folder exists
    os.makedirs("outputs", exist_ok=True)

    # Create a small sample dataframe
    sample = pd.DataFrame([
        {"title": "Sample Movie", "medium": "movie", "critic_score": 95, "genres": "Comedy"},
        {"title": "Sample Game", "medium": "game", "critic_score": 90, "genres": "Adventure"},
        {"title": "Sample Podcast", "medium": "podcast", "critic_score": 85, "genres": "Comedy"},
        {"title": "Sample Book", "medium": "book", "critic_score": 80, "genres": "Satire"},
    ])

    # Save the "all media" list
    sample.to_csv("outputs/critics_all_media_ranked.csv", index=False)

    # Filter comedy/humor only
    comedy = sample[sample["genres"].str.lower().str.contains("comedy|humor|satire")]
    comedy.to_csv("outputs/critics_comedy_humor_ranked.csv", index=False)


if __name__ == "__main__":
    main()
