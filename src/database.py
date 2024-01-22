import sqlite3
from pathlib import Path

DB_DIR_PATH = Path(__file__).resolve().parent.parent / "data"
SCRIPT_PATH = Path(__file__).resolve().parent
CREATE_TABLE = SCRIPT_PATH / "schema.sql"


def create_tables(db_name: str = "anime") -> None:
    path = DB_DIR_PATH / f"{db_name}.sqlite"
    conn = sqlite3.connect(path)
    with CREATE_TABLE.open(encoding="utf-8") as f:
        queries = f.read()
    conn.executescript(queries)
