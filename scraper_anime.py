"""Scrape MAL anime information.

Results are stored locally for future use after completion.
Exceptions are caught and logged to prevent failure, but not KeyboardInterrupt."""

import logging

from utils import get_all_anime

logger = logging.getLogger(__name__)


def main() -> None:
    """Do the entire calculation from scratch."""
    get_all_anime()


if __name__ == "__main__":
    main()
