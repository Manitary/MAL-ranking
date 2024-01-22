"""Verify integrity of scraped data.

Compare users' sampled data with anime sample data to make sure the anime IDs line up.
Specifically, the anime scraper may have received an incorrect response, or
raised an exception when scraping the information about an ID."""

import glob
import pickle

from mal_rankings import SAMPLE_PATH
from utils import FILE_ANIME_DB, load_samples


def get_anime_ids_from_sample(path_name: str = SAMPLE_PATH) -> set[int]:
    """Retrieve the anime IDs that appear in users' lists."""
    paths = glob.glob(path_name)
    sample = load_samples(*paths)
    sample_anime_ids = {
        entry["node"]["id"] for _, user_data in sample.items() for entry in user_data
    }
    return sample_anime_ids


def get_anime_ids_from_db(path_name: str = FILE_ANIME_DB) -> set[int]:
    """Retrieve the anime IDs that appear in the db."""
    with open(path_name, "rb") as f:
        anime_info = pickle.load(f)
    db_anime_ids = set(map(int, anime_info.keys()))
    return db_anime_ids


def main() -> None:
    """Run the check.

    Display mismatches on screen."""
    sample_anime_ids = get_anime_ids_from_sample()
    db_anime_ids = get_anime_ids_from_db()
    diff = sample_anime_ids.difference(db_anime_ids)
    print(diff)


if __name__ == "__main__":
    main()
