"""Estimate the parameters of the Bradley-Terry model for a sample of MAL users."""

import os
import re
import json
import random
from datetime import datetime
from itertools import combinations
from typing import Callable
import requests
import numpy as np
from dotenv import load_dotenv
from lxml import html
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

load_dotenv()

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
TIMEOUT = 60
SAMPLE_SIZE = 1
NUM_ITERATIONS = 50
MAL_USERS = 16169097  # as of 12/01/2023
MAL_ANIME = 54225  # as of 12/01/2023
MIN_LIST_SIZE = 5  # Minimum number of anime watched/dropped to consider a user.
LINK_USER_ID = "https://myanimelist.net/comments.php?id="
LINK_USER_LIST = (
    "https://api.myanimelist.net/v2/users/{}/animelist?limit=1000&fields=list_status"
)
USERNAME = re.compile(r"^/profile/(.*)")
HEADERS = {
    "X-MAL-CLIENT-ID": os.getenv("CLIENT_ID"),
    "Content-Type": "application/json",
}


@sleep_and_retry
@limits(calls=1, period=1)
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
@limits(calls=1, period=1)
def get_user_from_id(user_id: int) -> str:
    """Scrape and return the MAL username of a given user ID."""
    response = requests.get(f"{LINK_USER_ID}{user_id}", timeout=60)
    if response.status_code != 200:
        return None
    tree = html.fromstring(response.content)
    # all_users = tree.xpath('*//a/@href')
    user_profile = tree.xpath("body/div/div/div/div/div/div/a/@href")[0]
    username = USERNAME.findall(user_profile)[0]
    return username


def is_list_valid(mal_list: list[dict]) -> bool:
    """Check whether a given list meets requirements.

    Requirements:
        - Non-empty and public list.
        - Minimum size of completed + dropped entries that have been graded."""
    if not mal_list:
        return False
    if (
        sum(
            entry["list_status"]["status"] in {"completed", "dropped"}
            and entry["list_status"]["score"] > 0
            for entry in mal_list
        )
        < MIN_LIST_SIZE
    ):
        return False
    return True


def collect_sample(
    size: int = SAMPLE_SIZE,
    list_check: Callable[[list[dict]], bool] = is_list_valid,
    save: bool = True,
) -> dict[int, list]:
    """Scrape and return a usable data sample of given size."""
    sample = {}
    visited = set()
    print("Collecting sample")
    while len(sample) < size:
        num = random.randint(1, MAL_USERS)
        if num in visited:
            # ID already checked.
            continue
        visited.add(num)
        username = get_user_from_id(num)
        if username is None:
            # no user exists with the given ID.
            continue
        user_mal = get_user_list(username)
        if not list_check(user_mal):
            # user's list does not meet requirements.
            continue
        sample[num] = user_mal
        print(f"{len(sample)} - {username}")

    print(f"Sample obtained after {len(visited)} attempts")
    if save:
        with open(
            file=f"data/sample_{SAMPLE_SIZE}_{TIMESTAMP}.txt",
            mode="w",
            encoding="utf8",
        ) as f:
            f.write(json.dumps(sample))
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


def create_table(sample: dict[int, list], save: bool = True) -> np.ndarray:
    """Return the table used for the Bradley-Terry model for the given sample."""
    matrix = np.zeros((MAL_ANIME, MAL_ANIME), dtype=int)
    # TODO: massive table, should discard IDs not associated to any anime.
    for num, mal in sample.items():
        print(f"Processing user {num}")
        filtered_mal = {
            tuple(
                (
                    entry["node"]["id"],
                    entry["list_status"]["status"],
                    entry["list_status"]["score"],
                )
            )
            for entry in mal
            if entry["list_status"]["status"] in {"completed", "dropped"}
        }
        for (n1, s1, r1), (n2, s2, r2) in combinations(filtered_mal, 2):
            if s1 == "completed" and s2 == "dropped":
                matrix[n1, n2] += 1
            elif s1 == "dropped" and s2 == "completed":
                matrix[n2, n1] += 1
            elif r1 > r2 > 0:
                matrix[n1, n2] += 1
            elif r2 > r1 > 0:
                matrix[n2, n1] += 1

    print("Table constructed")
    if save:
        with open(file=f"data/table_{SAMPLE_SIZE}_{TIMESTAMP}.npy", mode="wb") as f:
            np.save(f, matrix)

    return matrix


def setup_bradley_terry(
    matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the arrays needed to compute the parameters from the given table."""
    mt = matrix + matrix.transpose()
    w = np.sum(matrix, axis=1)
    p = np.fromiter(iter=(0 if x == 0 else 1 for x in w), dtype=float)
    print("Setup completed")
    return p, mt, w


def main(num_iter: int = NUM_ITERATIONS, save: bool = True) -> None:
    """Do the entire calculation from scratch."""
    sample = collect_sample(save=save)
    table = create_table(sample=sample, save=save)
    p, mt, w = setup_bradley_terry(table)
    p_list = [p]
    for _ in tqdm(range(num_iter)):
        p = iterate_parameter(p=p, mt=mt, w=w)
        p_list.append(p)

    if save:
        with open(file=f"data/parameter_{SAMPLE_SIZE}_{TIMESTAMP}.npy", mode="wb") as f:
            np.save(f, p)
        with open(
            file=f"data/parameters_{SAMPLE_SIZE}_{TIMESTAMP}.npz", mode="wb"
        ) as f:
            np.savez(f, *p_list)
    print("Finished")


if __name__ == "__main__":
    main()
