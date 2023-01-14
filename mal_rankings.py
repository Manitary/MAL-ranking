"""Estimate the parameters of the Bradley-Terry model for a sample of MAL users."""

# from datetime import datetime
from numpy import np
from tqdm import tqdm
from utils import (
    collect_sample,
    create_table,
    setup_bradley_terry,
    iterate_parameter,
    TIMESTAMP,
)

# TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
SAMPLE_SIZE = 10000
NUM_ITERATIONS = 50


def main(
    sample_size: int = SAMPLE_SIZE,
    num_iter: int = NUM_ITERATIONS,
    save: bool = True,
) -> None:
    """Do the entire calculation from scratch."""
    sample = collect_sample(size=sample_size, save=save)
    table = create_table(sample=sample, save=save)
    p, mt, w = setup_bradley_terry(table)
    p_list = [p]
    for _ in tqdm(range(num_iter)):
        p = iterate_parameter(p=p, mt=mt, w=w)
        p_list.append(p)

    if save:
        with open(file=f"data/parameter_{sample_size}_{TIMESTAMP}.npy", mode="wb") as f:
            np.save(f, p)
        with open(
            file=f"data/parameters_{sample_size}_{TIMESTAMP}.npz", mode="wb"
        ) as f:
            np.savez(f, *p_list)
    print("Finished")


if __name__ == "__main__":
    main()
