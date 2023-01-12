import os
import re
import requests
from dotenv import load_dotenv
from lxml import html
from ratelimit import limits, sleep_and_retry

load_dotenv()
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


def main() -> dict:
    mal_lists = {}
    for num in range(1, 3):
        print(num)
        username = get_user_from_id(num)
        if username:
            print(username)
            mal = get_user_list(username)
            mal_lists[num] = {"name": username, "list": mal}
    return mal_lists


if __name__ == "__main__":
    main()
