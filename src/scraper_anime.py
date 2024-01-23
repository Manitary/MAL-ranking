import time
from datetime import UTC, datetime
from sqlite3 import Connection
from typing import Any

import requests
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

from config import CALLS, HEADERS, LINK_ANIME_ID, MAL_ANIME, PERIOD, TIMEOUT
from database import get_connection, insert_anime
from logger import logging
from models import Anime

ANIME_DB = get_connection("anime")
API_DB = get_connection("api")


class QueryError(Exception):
    ...


@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def query_anime_from_id(anime_id: int, api_db: Connection = API_DB) -> Any | None:
    """Return the MAL anime entry corresponding to the given ID, if it exists."""
    t = datetime.now(UTC)
    response = requests.get(
        LINK_ANIME_ID.format(anime_id), headers=HEADERS, timeout=TIMEOUT
    )
    api_db.execute(
        """
        INSERT INTO api_call (endpoint, element_id, response, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        ("anime", anime_id, response.status_code, t),
    )
    api_db.commit()
    if response.ok:
        logging.info("Entry %s retrieved", anime_id)
        return response.json()
    if response.status_code == 404:
        logging.info("Entry %s does not exist", anime_id)
        return None
    logging.warning("Entry %s returned status %s", anime_id, response.status_code)
    raise QueryError(response.status_code)


def get_anime_from_id(
    anime_id: int, anime_db: Connection = ANIME_DB, api_db: Connection = API_DB
) -> None:
    timeout = 30
    while True:
        try:
            anime = query_anime_from_id(anime_id, api_db)
        except QueryError:
            logging.info("Sleeping (%s)", timeout)
            time.sleep(timeout)
            timeout *= 2
            continue
        break
    if not anime:
        return
    try:
        anime = Anime(**anime)
        insert_anime(anime_db, anime)
    except Exception:
        anime_db.rollback()
        logging.exception("Entry %s was not added to the database", anime_id)
        api_db.execute(
            """
            UPDATE api_call
            SET response=1
            WHERE
                endpoint = "anime"
            AND element_id = ?
            """,
            (anime_id,),
        )
    else:
        logging.info("Entry %s successfully added to the database", anime_id)


def get_latest_valid_anime_id(anime_db: Connection = ANIME_DB) -> int:
    q = anime_db.execute("SELECT MAX(anime_id) FROM anime").fetchone()
    return q[0] or 0


def get_first_failed_anime_id(api_db: Connection = API_DB) -> int | None:
    q = api_db.execute(
        """SELECT MIN(element_id) FROM api_call
        WHERE endpoint = "anime" AND response != 404 AND response != 200"""
    ).fetchone()
    return q[0]


def get_failed_anime_id(api_db: Connection = API_DB) -> set[int]:
    q = api_db.execute(
        """SELECT element_id FROM api_call WHERE endpoint = "anime" AND response != 404"""
    ).fetchall()
    return {x[0] for x in q}


def get_invalid_anime_id(api_db: Connection = API_DB) -> set[int]:
    q = api_db.execute(
        """SELECT element_id FROM api_call WHERE endpoint = "anime" AND response = 404"""
    ).fetchall()
    return {x[0] for x in q}


def get_all_anime_id(anime_db: Connection = ANIME_DB) -> set[int]:
    q = anime_db.execute("SELECT anime_id FROM anime").fetchall()
    return {x[0] for x in q}


def get_all_anime(anime_db: Connection = ANIME_DB, api_db: Connection = API_DB) -> None:
    latest_valid = get_latest_valid_anime_id(anime_db)
    first_failed = get_first_failed_anime_id(api_db)
    start = min(first_failed, latest_valid) if first_failed else latest_valid + 1
    done_ids = get_all_anime_id(anime_db)
    not_anime = get_invalid_anime_id(api_db)
    invalid_ids = done_ids | not_anime
    for anime_id in tqdm(range(start, MAL_ANIME + 1)):
        if anime_id in invalid_ids:
            continue
        get_anime_from_id(anime_id, anime_db, api_db)


if __name__ == "__main__":
    get_all_anime()
