"""Fetch the existing anime id on MAL"""

import json
import requests
from ratelimit import limits, sleep_and_retry

MAX_ID = 23441
# MAX_ID = 20


@sleep_and_retry
@limits(calls=1, period=1)
def query_id(i: int) -> dict:
    response = requests.get(f"https://api.jikan.moe/v4/anime/{i}", timeout=60)
    if response.status_code == 200:
        print(i)
        data = response.json()["data"]
        return data["mal_id"], data
    return None, None


def main() -> None:
    db = {}
    for i in range(1, MAX_ID + 1):
        mal_id, data = query_id(i)
        if mal_id:
            db[mal_id] = dict(data)
    with open("anime_id_info.txt", mode="w", encoding="utf8") as f:
        f.write(json.dumps(db))


if __name__ == "__main__":
    main()
