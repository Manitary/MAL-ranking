"""Scrape MAL anime information.

Results are stored locally for future use after completion.
Exceptions are caught and logged to prevent failure, but not KeyboardInterrupt."""

from utils import get_all_anime


def main() -> None:
    """Do the entire calculation from scratch."""
    get_all_anime()


if __name__ == "__main__":
    main()
