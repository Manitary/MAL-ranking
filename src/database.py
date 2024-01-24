import sqlite3
from datetime import datetime
from pathlib import Path

from models import Anime

DB_DIR_PATH = Path(__file__).resolve().parent.parent / "data"
SCRIPT_PATH = Path(__file__).resolve().parent


def adapt_date_iso(val: datetime) -> str:
    return val.isoformat()


sqlite3.register_adapter(datetime, adapt_date_iso)


def db_path(db_name: str) -> Path:
    return DB_DIR_PATH / f"{db_name}.sqlite"


def create_tables(db_name: str, schema_name: str) -> None:
    path = db_path(db_name)
    script = SCRIPT_PATH / f"{schema_name}_schema.sql"

    with script.open(encoding="utf-8") as f:
        queries = f.read()

    conn = sqlite3.connect(path)
    conn.executescript(queries)


def get_connection(db_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(db_name))
    conn.row_factory = sqlite3.Row
    conn.autocommit = False
    conn.execute("PRAGMA foreign_keys=ON")
    conn.commit()
    return conn


def insert_anime(anime_db: sqlite3.Connection, anime: Anime) -> None:
    alt_titles = anime.get("alternative_titles", None)
    start_season = anime.get("start_season", None)
    broadcast = anime.get("broadcast", None)
    anime_db.execute(
        """
        INSERT INTO anime
        (anime_id, title, title_en, title_ja, start_date, end_date, synopsis,
        mean, rank, popularity, num_list_users, num_scoring_users,
        nsfw, media_type, status, num_episodes,
        start_season, start_season_year, broadcast_day, broadcast_time,
        source, average_episode_duration, rating, background)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            anime["id"],
            anime["title"],
            alt_titles.get("en", None) if alt_titles else None,
            alt_titles.get("ja", None) if alt_titles else None,
            anime.get("start_date", None),
            anime.get("end_date", None),
            anime.get("synopsis", None),
            anime.get("mean", None),
            anime.get("rank", None),
            anime.get("popularity", None),
            anime["num_list_users"],
            anime["num_scoring_users"],
            anime.get("nsfw", None),
            anime["media_type"],
            anime["status"],
            anime["num_episodes"],
            start_season["season"] if start_season else None,
            start_season["year"] if start_season else None,
            broadcast["day_of_the_week"] if broadcast else None,
            broadcast.get("start_time", None) if broadcast else None,
            anime.get("source", None),
            anime.get("average_episode_duration", None),
            anime.get("rating", None),
            anime.get("background", None),
        ),
    )
    if alt_titles and (synonyms := alt_titles.get("synonyms", None)):
        anime_db.executemany(
            "INSERT INTO synonyms (anime_id, synonym) VALUES (?, ?)",
            ((anime["id"], synonym) for synonym in synonyms),
        )
    if genres := anime.get("genres", None):
        anime_db.executemany(
            "INSERT INTO genre (genre_id, name) VALUES (?, ?)",
            ((genre["id"], genre["name"]) for genre in genres),
        )
        anime_db.executemany(
            "INSERT INTO anime_genre (anime_id, genre_id) VALUES (?, ?)",
            ((anime["id"], genre["id"]) for genre in genres),
        )
    anime_db.executemany(
        "INSERT INTO studio (studio_id, name) VALUES (?, ?)",
        ((studio["id"], studio["name"]) for studio in anime["studios"]),
    )
    anime_db.executemany(
        "INSERT INTO anime_studio (anime_id, studio_id) VALUES (?, ?)",
        ((anime["id"], studio["id"]) for studio in anime["studios"]),
    )
    if main_picture := anime.get("main_picture", None):
        anime_db.execute(
            "INSERT INTO main_picture (anime_id, large, medium) VALUES (?, ?, ?)",
            (anime["id"], main_picture.get("large", None), main_picture["medium"]),
        )
    anime_db.executemany(
        "INSERT INTO anime_picture (anime_id, large, medium) VALUES (?, ?, ?)",
        (
            (anime["id"], picture.get("large", None), picture["medium"])
            for picture in anime["pictures"]
        ),
    )
    anime_db.executemany(
        """INSERT INTO recommendations
        (anime_id, recommended_anime_id, num_recommendations)
        VALUES (?, ?, ?)""",
        (
            (anime["id"], rec["node"]["id"], rec["num_recommendations"])
            for rec in anime["recommendations"]
        ),
    )
    anime_db.executemany(
        """INSERT INTO related_anime
        (anime_id, related_anime_id, relation_type)
        VALUES (?, ?, ?)""",
        (
            (anime["id"], entry["node"]["id"], entry["relation_type"])
            for entry in anime["related_anime"]
        ),
    )
    anime_db.executemany(
        """INSERT INTO related_manga
        (anime_id, manga_id, relation_type)
        VALUES (?, ?, ?)""",
        (
            (anime["id"], entry["node"]["id"], entry["relation_type"])
            for entry in anime["related_manga"]
        ),
    )
    if stats := anime.get("statistics", None):
        status = stats["status"]
        anime_db.execute(
            """
            INSERT INTO statistics
            (anime_id, num_list_users, watching, completed, on_hold, dropped, plan_to_watch)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anime["id"],
                stats["num_list_users"],
                status["watching"],
                status["completed"],
                status["on_hold"],
                status["dropped"],
                status["plan_to_watch"],
            ),
        )
    anime_db.commit()


if __name__ == "__main__":
    create_tables("anime", "anime")
    create_tables("api", "api")
