import pandas as pd
import os

MOVIES_FILE = "outputs/critics_all_media_ranked.csv"
TV_FILE = "outputs/tv_metacritic_ranked.csv"

OUTPUT_ALL = "outputs/critics_all_media_normalized.csv"
OUTPUT_COMEDY = "outputs/critics_comedy_humor_normalized.csv"


def load_and_label(path, medium):
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["medium"] = medium
    return df


def normalize_within_medium(df):
    df["normalized_score"] = (
        (df["critic_score"] - df["critic_score"].mean())
        / df["critic_score"].std()
    )
    return df


def main():
    movies = load_and_label(MOVIES_FILE, "movie")
    tv = load_and_label(TV_FILE, "tv")

    combined = pd.concat([movies, tv], ignore_index=True)

    if combined.empty:
        print("No data available for normalization")
        return

    combined = combined.dropna(subset=["critic_score"])

    normalized = (
        combined
        .groupby("medium", group_keys=False)
        .apply(normalize_within_medium)
    )

    normalized = normalized.sort_values(
        "normalized_score", ascending=False
    )

    normalized.to_csv(OUTPUT_ALL, index=False)

    comedy_mask = normalized["genres"].str.lower().str.contains(
        "comedy|humor|satire", na=False
    )
    normalized[comedy_mask].to_csv(OUTPUT_COMEDY, index=False)


if __name__ == "__main__":
    main()
