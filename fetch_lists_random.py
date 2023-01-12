import os
import re
import json
import requests
import random
from dotenv import load_dotenv
from lxml import html
from ratelimit import limits, sleep_and_retry

load_dotenv()

NUM_ENTRIES = 10000
MAL_USERS_MAX = 16164317  # as if 11/01/2023
FILENAME = f"random_sample_{NUM_ENTRIES}_12012023.txt"
USER_ID_LINK = "https://myanimelist.net/comments.php?id="
USER_LIST_LINK = (
    "https://api.myanimelist.net/v2/users/{}/animelist?limit=1000&fields=list_status"
)
username_pattern = re.compile(r"/profile/(.*)")
headers = {
    "X-MAL-CLIENT-ID": os.getenv("CLIENT_ID"),
    "Content-Type": "application/json",
}


@sleep_and_retry
@limits(calls=1, period=1)
def get_user_list(username: str) -> list:
    url = USER_LIST_LINK.format(username)
    user_list = []
    while True:
        response = requests.get(
            url,
            headers=headers,
            timeout=60,
        )
        if response.status_code != 200:
            break
        payload = response.json()
        user_list += payload["data"]
        paging = payload["paging"]
        if "next" in paging:
            url = paging["next"]
        else:
            break
    return user_list


@sleep_and_retry
@limits(calls=1, period=1)
def get_user_from_id(user_id: int) -> str:
    response = requests.get(f"{USER_ID_LINK}{user_id}", timeout=60)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        # all_users = tree.xpath('*//a/@href')
        user = tree.xpath("body/div/div/div/div/div/div/a/@href")[0]
        username = username_pattern.findall(user)[0]
        return username


def main() -> None:
    mal_lists = {}
    visited = set()
    while len(mal_lists) < NUM_ENTRIES:
        num = random.randint(1, MAL_USERS_MAX)
        if num not in visited:
            visited.add(num)
            print(num)
            username = get_user_from_id(num)
            if username:
                mal = get_user_list(username)
                mal_lists[num] = {"name": username, "list": mal}
                print(len(mal_lists), username)
    with open(file=FILENAME, mode="w", encoding="utf8") as f:
        f.write(json.dumps(mal_lists))


if __name__ == "__main__":
    main()
