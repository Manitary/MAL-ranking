CREATE TABLE IF NOT EXISTS "anime" (
    "anime_id" INTEGER NOT NULL PRIMARY KEY,
    "title" TEXT UNIQUE NOT NULL,
    "title_en" TEXT,
    "title_ja" TEXT,
    "start_date" TEXT,
    "end_date" TEXT,
    "synopsis" TEXT,
    "mean" REAL,
    "rank" INTEGER,
    "popularity" INTEGER,
    "num_list_users" INTEGER NOT NULL DEFAULT 0,
    "num_scoring_users" INTEGER NOT NULL DEFAULT 0,
    "nsfw" TEXT,
    "media_type" TEXT NOT NULL DEFAULT "unknown",
    "status" TEXT NOT NULL,
    "num_episodes" INTEGER NOT NULL DEFAULT 0,
    "start_season" TEXT,
    "start_season_year" INTEGER,
    "broadcast_day" TEXT,
    "broadcast_time" TEXT,
    "source" TEXT,
    "average_episode_duration" INTEGER,
    "rating" TEXT,
    "background" TEXT
);

CREATE TABLE IF NOT EXISTS "main_picture" (
    "anime_id" INTEGER NOT NULL PRIMARY KEY,
    "large" TEXT,
    "medium" TEXT NOT NULL,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "pictures" (
    "anime_id" INTEGER NOT NULL PRIMARY KEY,
    "large" TEXT,
    "medium" TEXT NOT NULL,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "synonyms" (
    "anime_id" INTEGER NOT NULL PRIMARY KEY,
    "synonym" TEXT NOT NULL,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "genre" (
    "genre_id" INTEGER NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "anime_genre" (
    "anime_id" INTEGER NOT NULL,
    "genre_id" INTEGER NOT NULL,
    PRIMARY KEY("anime_id", "genre_id") ON CONFLICT IGNORE,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE,
    FOREIGN KEY("genre_id") REFERENCES "genre"("genre_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "studio" (
    "studio_id" INTEGER NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "anime_studio" (
    "anime_id" INTEGER NOT NULL,
    "studio_id" INTEGER NOT NULL,
    PRIMARY KEY("anime_id", "studio_id") ON CONFLICT IGNORE,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE,
    FOREIGN KEY("studio_id") REFERENCES "studio"("studio_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "related_anime" (
    "anime_id" INTEGER NOT NULL,
    "related_anime_id" INTEGER NOT NULL,
    "relation_type" TEXT NOT NULL,
    PRIMARY KEY("anime_id", "related_anime_id"),
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE,
    FOREIGN KEY("related_anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "related_manga" (
    "anime_id" INTEGER NOT NULL,
    "manga_id" INTEGER NOT NULL,
    "relation_type" TEXT NOT NULL,
    PRIMARY KEY("anime_id", "manga_id"),
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "recommendations" (
    "anime_id" INTEGER NOT NULL,
    "recommended_anime_id" INTEGER NOT NULL,
    "num_recommendations" INTEGER NOT NULL,
    PRIMARY KEY("anime_id", "recommended_anime_id"),
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE,
    FOREIGN KEY("recommended_anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "statistics" (
    "anime_id" INTEGER NOT NULL PRIMARY KEY,
    "num_list_users" INTEGER NOT NULL DEFAULT 0,
    "watching" INTEGER NOT NULL DEFAULT 0,
    "completed" INTEGER NOT NULL DEFAULT 0,
    "on_hold" INTEGER NOT NULL DEFAULT 0,
    "dropped" INTEGER NOT NULL DEFAULT 0,
    "plan_to_watch" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY("anime_id") REFERENCES "anime"("anime_id") ON DELETE CASCADE
);
