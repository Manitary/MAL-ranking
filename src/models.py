from enum import StrEnum, auto
from typing import Required, TypedDict


class Relation(StrEnum):
    SEQUEL = auto()
    PREQUEL = auto()
    ALTERNATIVE_SETTING = auto()
    ALTERNATIVE_VERSION = auto()
    SIDE_STORY = auto()
    PARENT_STORY = auto()
    SUMMARY = auto()
    FULL_STORY = auto()


class AgeRating(StrEnum):
    G = auto()
    PG = auto()
    PG_13 = auto()
    R = auto()
    R_PLUS = "r+"
    RX = auto()


class MediaType(StrEnum):
    UNKNOWN = auto()
    TV = auto()
    OVA = auto()
    MOVIE = auto()
    SPECIAL = auto()
    ONA = auto()
    MUSIC = auto()


class AiringStatus(StrEnum):
    FINISHED_AIRING = auto()
    CURRENTLY_AIRING = auto()
    NOT_YET_AIRED = auto()


class NSFWClass(StrEnum):
    WHITE = auto()
    GRAY = auto()
    BLACK = auto()


class SourceType(StrEnum):
    OTHER = auto()
    ORIGINAL = auto()
    MANGA = auto()
    FOUR_KOMA = "4_koma_manga"
    WEB_MANGA = auto()
    DIGITAL_MANGA = auto()
    NOVEL = auto()
    LIGHT_NOVEL = auto()
    VISUAL_NOVEL = auto()
    GAME = auto()
    CARD_GAME = auto()
    BOOK = auto()
    PICTURE_BOOK = auto()
    RADIO = auto()
    MUSIC = auto()


type Picture = dict[str, str]


class ListStatus(TypedDict):
    status: str
    score: int
    num_watched_episodes: int
    is_rewatching: bool
    updated_at: str


class ListNode(TypedDict):
    id: int
    title: str
    main_picture: Picture


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


class Broadcast(TypedDict, total=False):
    day_of_the_week: str
    start_time: str


class RelatedEntry(TypedDict, total=False):
    node: ListNode
    relation_type: Relation
    relation_type_formatted: str


class Recommendation(TypedDict, total=False):
    node: ListNode
    num_recommendations: int


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
    main_picture: Picture | None
    alternative_titles: AltTitles | None
    start_date: str | None
    end_date: str | None
    synopsis: str | None
    mean: float | None
    rank: int | None
    popularity: int | None
    num_list_users: int
    num_scoring_users: int
    nsfw: NSFWClass | None
    genres: list[Genre]
    created_at: Required[str]
    updated_at: Required[str]
    media_type: MediaType
    status: AiringStatus
    # my_list_status: ListStatus
    num_episodes: int
    start_season: Season | None
    broadcast: Broadcast | None
    source: SourceType | None
    average_episode_duration: int | None
    rating: AgeRating | None
    studios: list[Studio]
    pictures: list[Picture]
    background: str | None
    related_anime: list[RelatedEntry]
    related_manga: list[RelatedEntry]
    recommendations: list[Recommendation]
    statistics: AnimeStats | None


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
