from typing import Required, TypedDict


class ListStatus(TypedDict):
    status: str
    score: int
    num_watched_episodes: int
    is_rewatching: bool
    updated_at: str


class ListNode(TypedDict):
    id: int
    title: str
    main_picture: dict[str, str]


class UserListEntry(TypedDict):
    node: ListNode
    list_status: ListStatus


type UserList = list[UserListEntry]


class AltTitles(TypedDict, total=False):
    synonyms: list[str]
    en: str
    ja: str


class Genre(TypedDict, total=False):
    id: int
    name: str


class Season(TypedDict, total=False):
    year: int
    season: str


class Studio(TypedDict, total=False):
    id: int
    name: str


class AnimeStatus(TypedDict, total=False):
    watching: int
    completed: int
    on_hold: int
    dropped: int
    plan_to_watch: int


class AnimeStats(TypedDict, total=False):
    status: AnimeStatus
    num_list_users: int


class Anime(TypedDict, total=False):
    id: Required[int]
    title: Required[str]
    main_picture: dict[str, str]
    alternative_titles: AltTitles
    start_date: str
    end_date: str
    synopsis: str
    mean: float
    rank: int
    popularity: int
    num_list_users: int
    num_scoring_users: int
    nsfw: str
    genres: list[Genre]
    media_type: str
    status: str
    num_episodes: int
    start_season: Season
    source: str
    average_episode_duration: int
    studios: list[Studio]
    statistics: AnimeStats

    # created_at: str
    # updated_at: str
    # my_list_status: ListStatus
    # broadcast
    # rating: str
    # pictures: list[...]
    # background: str
    # related_anime: list[...]
    # recommendations: list[...]


class ResultShort(TypedDict):
    mal_ID: int
    title: str
    parameter: float


class Result(TypedDict):
    mal_ID: int
    parameter: float
    num_comparisons: int
    num_lists: int
    pct_lists: float
    rel_error_pct: float
