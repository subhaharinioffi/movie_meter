"""
Data Loader Utility for MovieMeter.
Downloads and caches the IMDb Movie Metadata dataset.
"""

import os
import pandas as pd
import requests

DATA_URL = "https://raw.githubusercontent.com/nitishghosal/IMDB-Data-Analysis/master/movie_metadata.csv"
RAW_DATA_DIR = os.path.join("data", "raw")
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, "movie_metadata.csv")

def download_dataset():
    """
    Downloads the IMDb dataset from the raw GitHub URL if it doesn't already exist.
    """
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        print(f"Created raw data directory: {RAW_DATA_DIR}")

    if not os.path.exists(RAW_DATA_PATH):
        print(f"Downloading dataset from {DATA_URL}...")
        response = requests.get(DATA_URL, timeout=30)
        response.raise_for_status()
        with open(RAW_DATA_PATH, "wb") as f:
            f.write(response.content)
        print(f"Dataset downloaded successfully and saved to {RAW_DATA_PATH}")
    else:
        print(f"Dataset already exists at {RAW_DATA_PATH}")

def load_dataset() -> pd.DataFrame:
    """
    Loads and returns the raw IMDb dataset as a Pandas DataFrame.
    """
    download_dataset()
    return pd.read_csv(RAW_DATA_PATH)

if __name__ == "__main__":
    df = load_dataset()
    print(f"Loaded dataset with shape: {df.shape}")
