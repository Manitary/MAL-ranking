import re
import time
from datetime import UTC, datetime
from sqlite3 import Connection

import requests
from bs4 import BeautifulSoup, Tag
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

from config import CALLS, HEADERS, LINK_COMPANY_ID, MAL_COMPANY, PERIOD, TIMEOUT
from database import get_connection
from logger import logging

ANIME_DB = get_connection("anime")
API_DB = get_connection("api")

RE_ANIME_ID = re.compile(r"anime/(\d+)/")


class QueryError(Exception):
    ...


@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def query_company_from_id(
    company_id: int, api_db: Connection = API_DB
) -> BeautifulSoup | None:
    """Return the MAL anime entry corresponding to the given ID, if it exists."""
    t = datetime.now(UTC)
    response = requests.get(
        LINK_COMPANY_ID.format(company_id), headers=HEADERS, timeout=TIMEOUT
    )
    api_db.execute(
        """
        INSERT INTO api_call (endpoint, element_id, response, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        ("producer", company_id, response.status_code, t),
    )
    api_db.commit()
    if response.ok:
        logging.info("Entry %s retrieved", company_id)
        return BeautifulSoup(response.text, features="html.parser")
    if response.status_code == 404:
        logging.info("Entry %s does not exist", company_id)
        return None
    logging.warning("Entry %s returned status %s", company_id, response.status_code)
    raise QueryError(response.status_code)


def get_company_name(company: BeautifulSoup) -> str:
    info = company.find("div", class_="h1-title")
    assert isinstance(info, Tag)
    return info.text.strip()


def get_anime_id(div: Tag) -> int:
    title = div.find("div", class_="title")
    assert isinstance(title, Tag)
    assert title.a
    match = RE_ANIME_ID.search(title.a.attrs["href"])
    assert match
    return int(match.group(1))


def get_company_role(div: Tag) -> str:
    cat = div.find("div", class_="category")
    assert isinstance(cat, Tag)
    return cat.text.strip()


def get_anime_data(div: Tag) -> tuple[int, str]:
    return (get_anime_id(div), get_company_role(div))


def get_anime_from_company(company: BeautifulSoup) -> list[tuple[int, str]]:
    divs = company.find_all("div", class_="js-anime-type-all")
    return list(map(get_anime_data, divs))


def get_company_from_id(
    company_id: int, anime_db: Connection = ANIME_DB, api_db: Connection = API_DB
) -> None:
    timeout = 30
    while True:
        try:
            company = query_company_from_id(company_id, api_db)
        except QueryError:
            logging.info("Sleeping (%s)", timeout)
            time.sleep(timeout)
            timeout *= 2
            continue
        break
    if not company:
        return
    try:
        company_name = get_company_name(company)
        anime_data = get_anime_from_company(company)
        anime_db.execute(
            "INSERT INTO company (company_id, name) VALUES (?, ?)",
            (company_id, company_name),
        )
        anime_db.executemany(
            "INSERT INTO company_anime (company_id, anime_id, category) VALUES (?, ?, ?)",
            ((company_id, anime_id, relation) for anime_id, relation in anime_data),
        )
        anime_db.commit()
    except Exception:
        anime_db.rollback()
        logging.exception("Entry %s was not added to the database", company_id)
        api_db.execute(
            """
            UPDATE api_call
            SET response=1
            WHERE
                endpoint = "company"
            AND element_id = ?
            """,
            (company_id,),
        )
        api_db.commit()
    else:
        logging.info("Entry %s successfully added to the database", company_id)


def get_latest_valid_company_id(anime_db: Connection = ANIME_DB) -> int:
    q = anime_db.execute("SELECT MAX(company_id) FROM company").fetchone()
    return q[0] or 0


def get_first_failed_company_id(api_db: Connection = API_DB) -> int | None:
    q = api_db.execute(
        """SELECT MIN(element_id) FROM api_call
        WHERE endpoint = "company" AND response != 404 AND response != 200"""
    ).fetchone()
    return q[0]


def get_all_company_id(anime_db: Connection = ANIME_DB) -> set[int]:
    q = anime_db.execute("SELECT company_id FROM company").fetchall()
    return {x[0] for x in q}


def get_invalid_company_id(api_db: Connection = API_DB) -> set[int]:
    q = api_db.execute(
        """SELECT element_id FROM api_call WHERE endpoint = "company" AND response = 404"""
    ).fetchall()
    return {x[0] for x in q}


def get_all_companies(
    anime_db: Connection = ANIME_DB, api_db: Connection = API_DB
) -> None:
    latest_valid = get_latest_valid_company_id(anime_db)
    first_failed = get_first_failed_company_id(api_db)
    start = min(first_failed, latest_valid) if first_failed else latest_valid + 1
    done_ids = get_all_company_id(anime_db)
    not_company = get_invalid_company_id(api_db)
    invalid_ids = done_ids | not_company
    for company_id in tqdm(range(start, MAL_COMPANY + 1)):
        if company_id in invalid_ids:
            continue
        get_company_from_id(company_id, anime_db, api_db)


if __name__ == "__main__":
    get_all_companies()
