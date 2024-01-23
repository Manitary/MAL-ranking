import os

from dotenv import load_dotenv

load_dotenv()

MAL_ANIME = 60000  # As of January 2024

CALLS = 15
PERIOD = 10
assert CALLS / PERIOD > 0.5
TIMEOUT = 60

HEADERS = {
    "X-MAL-CLIENT-ID": os.getenv("CLIENT_ID") or "",
    "Content-Type": "application/json",
}
LINK_ANIME_ID = (
    "https://api.myanimelist.net/v2/anime/{}?fields="
    "id,title,main_picture,alternative_titles,start_date,end_date,synopsis,"
    "mean,rank,popularity,num_list_users,num_scoring_users,nsfw,genres,"
    "media_type,status,num_episodes,start_season,broadcast,source,"
    "average_episode_duration,rating,studios,pictures,background,"
    "related_anime,related_manga,recommendations,statistics"
)
# https://myanimelist.net/forum/?goto=post&topicid=140439&id=70370969 has highest entry 57847
