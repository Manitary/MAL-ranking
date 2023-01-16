"""Estimate the parameters of the Bradley-Terry model for a sample of MAL users."""

import glob
from numpy import np
from tqdm import tqdm
from utils import (
    create_table,
    setup_bradley_terry,
    iterate_parameter,
    load_id_to_order_map,
    load_samples,
    TIMESTAMP,
)

NUM_ITERATIONS = 50
SAMPLE_PATH = "data/sample_*.json"


def main(
    sample_path: str = SAMPLE_PATH,
    num_iter: int = NUM_ITERATIONS,
    save: bool = True,
    timestamp: str = TIMESTAMP,
) -> None:
    """Do the entire calculation from scratch."""
    sample = load_samples(glob.glob(sample_path))
    id_to_order = load_id_to_order_map()
    table = create_table(
        size=len(id_to_order), id_to_order=id_to_order, sample=sample, save=save
    )
    p, mt, w = setup_bradley_terry(table)
    # Force initial table deletion if necessary
    # import gc
    # del table
    # gc.collect()
    p_list = [p]
    for _ in tqdm(range(num_iter)):
        p = iterate_parameter(p=p, mt=mt, w=w)
        p_list.append(p)

    if save:
        with open(file=f"data/parameter_{timestamp}_{len(sample)}.npy", mode="wb") as f:
            np.save(f, p)
        with open(
            file=f"data/parameters_{timestamp}_{len(sample)}.npz", mode="wb"
        ) as f:
            np.savez(f, *p_list)
    print("Finished")


if __name__ == "__main__":
    main()
