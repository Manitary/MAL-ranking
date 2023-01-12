import requests
from lxml import html
from ratelimit import limits, sleep_and_retry

USERS_LINK = "https://myanimelist.net/users.php?lucky=1"
USERS_AMOUNT = 50000
DATE = "11012023"


@sleep_and_retry
@limits(calls=1, period=1)
def get_users_lucky() -> set[str]:
    response = requests.get(USERS_LINK, timeout=60)
    tree = html.fromstring(response.content)
    names = set(tree.xpath('//td[@align="center"]/div/a/text()'))
    return names


def main() -> None:
    names = set()
    count = 0
    while len(names) < USERS_AMOUNT:
        count += 1
        names |= get_users_lucky()
        print(count, len(names))
    with open(f"names_{DATE}.txt", mode="w", encoding="utf8") as f:
        f.write(str(names))


if __name__ == "__main__":
    main()
