"""Scrape MAL users' list information.

Take as optional argument the size of the sample to scrape.
By default, the results are stored locally for future use, and partial results are saved
even when interrupted, as it is a very time-consuming process."""

import argparse
from utils import collect_sample

SAMPLE_SIZE = 10000


def main(sample_size: int, save: bool = True) -> None:
    """Do the entire calculation from scratch."""
    collect_sample(size=sample_size, save=save)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--number",
        metavar="N",
        type=int,
        default=SAMPLE_SIZE,
        help=f"sample size, default={SAMPLE_SIZE}",
    )
    parser.add_argument(
        "-s",
        "--save",
        metavar="S",
        type=bool,
        default=True,
        help="save results, default=True",
    )
    args = parser.parse_args()
    main(sample_size=args.number, save=args.save)
