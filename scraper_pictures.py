"""Get anime pictures."""

import json
import shutil

import requests
from tqdm import tqdm

with open("docs/data/anime.json", encoding="utf8") as f:
    anime = json.load(f)

anime = {int(k): v for k, v in anime.items()}

for i, entry in tqdm(anime.items()):
    if "picture" in entry and entry["picture"]:
        r = requests.get(f"{entry['picture'][:-4]}.jpg", timeout=60, stream=True)
        if r.status_code == 200:
            with open(f"pictures/{i}s.jpg", "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
