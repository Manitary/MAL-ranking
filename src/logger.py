import logging
from pathlib import Path

LOG_DIR_PATH = Path(__file__).resolve().parent.parent / "logs"

logging.basicConfig(
    filename=LOG_DIR_PATH / "log.log",
    format="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)
