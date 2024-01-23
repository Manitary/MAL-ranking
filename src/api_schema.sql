CREATE TABLE IF NOT EXISTS "api_call" (
    "endpoint" TEXT NOT NULL,
    "element_id" INTEGER NOT NULL,
    "response" INTEGER,
    "timestamp" TEXT,
    PRIMARY KEY("endpoint", "element_id") ON CONFLICT REPLACE
);
