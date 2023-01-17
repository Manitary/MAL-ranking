"""Functions used for the calculation of comparative MAL rankings."""

import pickle
import os
import re
import json
import random
import logging
from datetime import datetime
from itertools import combinations
from typing import Callable, Iterator
import requests
import numpy as np
from dotenv import load_dotenv
from lxml import html
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

load_dotenv()

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
REQUEST_DELAY = 0.6  # Recommended to stay above 0.5s
TIMEOUT = 60
SAMPLE_SIZE = 10000
NUM_ITERATIONS = 50
MAL_USERS = 16169097  # As of 12/01/2023
LEN_USERS = 8  # Number of digits
MAL_ANIME = 54225  # As of 12/01/2023
MIN_LIST_SIZE = 5  # Minimum number of anime watched/dropped to consider a user.
LINK_USER_ID = "https://myanimelist.net/comments.php?id={}"
LINK_ANIME_ID = (
    "https://api.myanimelist.net/v2/anime/{}?fields="
    "id,title,main_picture,alternative_titles,start_date,end_date,synopsis,"
    "mean,rank,popularity,num_list_users,num_scoring_users,nsfw,genres,media_type,status,"
    "num_episodes,start_season,source,average_episode_duration,studios,statistics"
)
LINK_USER_LIST = (
    "https://api.myanimelist.net/v2/users/{}/animelist?limit=1000&fields=list_status"
)
USERNAME = re.compile(r"^/profile/(.*)")
HEADERS = {
    "X-MAL-CLIENT-ID": os.getenv("CLIENT_ID"),
    "Content-Type": "application/json",
}
FILE_INVALID_USER_ID = "data/invalid_user_ids"
FILE_VISITED_USER_ID = "data/visited_user_ids"
FILE_VALID_ANIME_ID = "data/valid_anime_ids"
FILE_ANIME_DB = "data/anime"


@sleep_and_retry
@limits(calls=1, period=REQUEST_DELAY)
def get_user_list(username: str) -> list[dict]:
    """Scrape and return the MAL list of a user from their username.

    The response schema is available at:
    https://myanimelist.net/apiconfig/references/api/v2#operation/users_user_id_animelist_get"""
    url = LINK_USER_LIST.format(username)
    user_list = []
    while True:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 200:
            break
        payload = response.json()
        user_list += payload["data"]
        paging = payload["paging"]
        if "next" not in paging:
            break
        url = paging["next"]
    return user_list


@sleep_and_retry
@limits(calls=1, period=REQUEST_DELAY)
def get_user_from_id(user_id: int) -> str:
    """Scrape and return the MAL username of a given user ID."""
    response = requests.get(LINK_USER_ID.format(user_id), timeout=60)
    if response.status_code != 200:
        return None
    tree = html.fromstring(response.content)
    try:
        user_profile = tree.xpath("body/div/div/div/div/div/div/a/@href")[0]
        # all_users = tree.xpath('*//a/@href')
        username = USERNAME.findall(user_profile)[0]
        return username
    except Exception:
        logging.exception(
            "The following user ID should have been valid, but raised an exception: %s",
            user_id,
        )
    return None


@sleep_and_retry
@limits(calls=1, period=REQUEST_DELAY)
def get_anime_from_id(anime_id: int) -> bool:
    """Return the MAL anime entry corresponding to the given ID, if it exists."""
    response = requests.get(
        LINK_ANIME_ID.format(anime_id), headers=HEADERS, timeout=TIMEOUT
    )
    if response.status_code != 200:
        return None
    return response.json()


def get_all_anime() -> None:
    """Scrape all anime information.

    Store list of valid IDs and anime data."""
    id_list = []
    anime_info = {}
    for anime_id in tqdm(range(MAL_ANIME)):
        try:
            data = get_anime_from_id(anime_id=anime_id)
            if data:
                anime_info[anime_id] = data
                id_list.append(anime_id)
        except Exception:
            logging.exception("\nThe entry %s caused an exception\n", anime_id)
            continue

    order_to_id = dict(enumerate(id_list))
    id_to_order = {j: i for i, j in enumerate(id_list)}
    anime_list = {"order": order_to_id, "id": id_to_order}
    with open(FILE_VALID_ANIME_ID, "wb") as f:
        pickle.dump(anime_list, f)
    with open(FILE_ANIME_DB, "wb") as f:
        pickle.dump(anime_info, f)
    return anime_list, anime_info


def is_list_valid(mal_list: list[dict]) -> bool:
    """Check whether a given list meets requirements.

    Requirements:
        - Non-empty and public list.
        - Minimum size of completed + dropped entries that have been graded."""
    if not mal_list:
        return False
    try:
        if (
            sum(
                entry["list_status"]["status"] in {"completed", "dropped"}
                and entry["list_status"]["score"] > 0
                for entry in mal_list
            )
            < MIN_LIST_SIZE
        ):
            return False
    except Exception:
        logging.exception("The following list raised an exception:\n%s", str(mal_list))
        return False
    return True


def save_sample(
    sample: dict[int, list], invalid: set = None, visited: set = None
) -> None:
    """Save a sample to disk."""
    with open(
        f"data/samples/sample_{TIMESTAMP}_{len(sample)}.json",
        "w",
        encoding="utf8",
    ) as f:
        f.write(json.dumps(sample))
    print("Sample saved to disk.")
    if invalid:
        with open(FILE_INVALID_USER_ID, "wb") as f:
            pickle.dump(invalid, f)
        print("List of invalid IDs updated.")
    if visited:
        with open(FILE_VISITED_USER_ID, "wb") as f:
            pickle.dump(visited, f)
        print("List of visited IDs updated.")


def get_set_data(filename: str) -> set:
    """Return a set pickled from a file.

    If the file does not exist, create an empty file and return an empty set.
    If the file is empty, return an empty set.
    Raise an error if the pickled data is not a set."""
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            if not isinstance(data, set):
                raise TypeError("The contents of the file are not a set.")
            return data
    except FileNotFoundError:
        with open(filename, "xb"):
            pass
    except EOFError:
        pass
    return set()


def collect_sample(
    size: int = SAMPLE_SIZE,
    list_check: Callable[[list[dict]], bool] = is_list_valid,
    save: bool = True,
) -> dict[int, list]:
    """Scrape and return a usable data sample of given size randomly selected.

    Parameters:
        size: Size of the sample.
        list_check: Function that checks whether a user's list is admissible.
        save: If True, store as JSON when the finished, or when a keyboard interrupt occurs.

    Return:
        sample: a dictionary of user ID -> associated MAL list."""
    sample = {}
    visited = get_set_data(FILE_VISITED_USER_ID)
    invalid = get_set_data(FILE_INVALID_USER_ID)
    count = 0
    print("Collecting sample")
    with tqdm(total=size) as progress_bar:
        while len(sample) < size:
            try:
                count += 1
                num = random.randint(1, MAL_USERS)
                progress_bar.set_description(f"Processing ID {num:{LEN_USERS}}")
                if num in visited or num in invalid:
                    # ID already checked.
                    continue
                username = get_user_from_id(user_id=num)
                if username is None:
                    # no user exists with the given ID.
                    invalid.add(num)
                    continue
                visited.add(num)
                user_mal = get_user_list(username=username)
                if not list_check(user_mal):
                    # user's list does not meet requirements.
                    continue
                sample[num] = user_mal
                progress_bar.update(1)
            except (KeyboardInterrupt, SystemExit):
                if save:
                    logging.exception("Interrupted. Saving partial data...")
                    save_sample(sample=sample, invalid=invalid, visited=visited)
                return sample
            except KeyError:
                # Rarely, the 'status' key may be missing for unknown reasons.
                continue
            except Exception:
                logging.exception(
                    "An exception occurred while scraping user ID %s", str(num)
                )
                continue

    print(f"Sample obtained after {count} attempts")
    if save:
        save_sample(sample=sample, invalid=invalid, visited=visited)
    return sample


def iterate_parameter(p: np.ndarray, mt: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Return the next approximation of the parameters of the Bradley-Terry model.

    Arguments:
        p: Array of parameters.
        mt: Sum of the matrix of results and its transpose.
        w: Array of weights, i.e. sum of each row of the original table.

    p'_i = w_i / sum_j{ mt_ij / (p_i + p_j) }
    """
    s = np.fromiter(
        iter=(1 if w[i] == 0 else sum(mt[i] / (p[i] + p)) for i in range(p.shape[0])),
        dtype=float,
    )
    p_new = w / s
    return p_new / sum(p_new)


def load_id_to_order_map() -> dict:
    """Return the map id->order."""
    with open(FILE_VALID_ANIME_ID, encoding="utf8") as f:
        id_to_order = pickle.load(f)["id"]
    return id_to_order


def filter_entry(id_to_order: dict[int, int], entry: dict) -> tuple:
    """Filter the relevant values of an entry to analyse."""
    filtered_entry = tuple(
        (
            id_to_order[entry["node"]["id"]],
            entry["list_status"]["status"],
            entry["list_status"]["score"],
        )
    )
    return filtered_entry


def compare_filtered_entries(entry_1: tuple, entry_2: tuple) -> tuple[int, int]:
    """Compare two entries and return the corresponding table entry to update."""
    n1, s1, r1 = entry_1
    n2, s2, r2 = entry_2
    if s1 == "completed" and s2 == "dropped":
        return n1, n2
    if s1 == "dropped" and s2 == "completed":
        return n2, n1
    if r1 > r2 > 0:
        return n1, n2
    if r2 > r1 > 0:
        return n2, n1
    raise ValueError("Something went wrong")


def create_table(
    size: int, id_to_order: dict[int, int], sample: dict[int, list], save: bool = True
) -> np.ndarray:
    """Return the table used for the Bradley-Terry model for the given sample."""
    print("Initialising table")
    matrix = np.zeros((size, size), dtype=int)
    with tqdm(total=len(sample)) as progress_bar:
        for num, mal in sample.items():
            progress_bar.set_description(f"Processing user {num}")
            filtered_mal = {
                filter_entry(id_to_order, entry)
                for entry in mal
                if entry["list_status"]["status"] in {"completed", "dropped"}
            }
            for a, b in combinations(filtered_mal, 2):
                # Criteria to assign score
                matrix[compare_filtered_entries(a, b)] += 1
            progress_bar.update(1)

    print("Table constructed")
    if save:
        with open(file=f"data/table_{TIMESTAMP}_{len(sample)}.npy", mode="wb") as f:
            np.save(f, matrix)

    return matrix


def setup_bradley_terry(
    matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the arrays needed to compute the parameters from the given table."""
    print("Constructing arrays")
    mt = matrix + matrix.transpose()
    w = np.sum(matrix, axis=1)
    p = np.fromiter(iter=(0 if x == 0 else 1 for x in w), dtype=float)
    print("Setup completed")
    return p, mt, w


def load_samples(*filenames: str) -> dict[int, list]:
    """Load samples from JSON files and return the resulting sample.

    File names are sorted; with proper naming this allows duplicate entries
    to only keep the most up-to-date version, if any exist."""
    sample = {}
    for filename in sorted(tqdm(filenames)):
        with open(file=filename, encoding="utf8") as f:
            sample |= json.load(f)
    return sample


def yield_samples(*filenames: str) -> Iterator[dict[int, list]]:
    """Yield samples from JSON files.

    This assumes that all samples are disjoint."""
    for filename in tqdm(filenames):
        with open(file=filename, encoding="utf8") as f:
            yield json.load(f)
