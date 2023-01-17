"""Estimate the parameters of the Bradley-Terry model for a sample of MAL users."""

import re
import gc
import glob
import argparse
import pickle
from itertools import count
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

SAMPLE_PATH = "data/samples/sample_*.json"
SAVE_EVERY = 50
# MAX_DELTA = 0.001


def step_iteration(
    p: np.ndarray,
    mt: np.ndarray,
    w: np.ndarray,
    num_iter: int,
) -> tuple(np.ndarray, list[np.ndarray]):
    """Iterate the parameter num_iter times.

    Display the max delta of a single parameter between first and last iteration."""
    p_list = [np.copy(p)]
    old_p = np.copy(p)
    for _ in tqdm(range(num_iter)):
        p = iterate_parameter(p=p, mt=mt, w=w)
        p_list.append(np.copy(p))
    delta = np.abs(old_p - p)
    print(
        f"""Iteration max delta: {np.amax(delta)}
    at position {np.argmax(delta)}"""
    )
    return p, p_list


def endless_iteration(
    datum: tuple[np.ndarray, np.ndarray, np.ndarray],
    num_iter: int,
    timestamp: str,
    sample_size: int,
    start=0,
) -> None:
    """Iterate endlessly the parameter computation.

    Interrupt manually.
    Results are stored every num_iter iterations.
    """
    p, mt, w = datum
    for i in count(start=1):
        marker = start + i * num_iter
        p, p_list = step_iteration(p=p, mt=mt, w=w, num_iter=num_iter)
        with open(f"data/{timestamp}_{sample_size}/parameter_{marker}.npy", "wb") as f:
            np.save(f, p)
        with open(f"data/{timestamp}_{sample_size}/parameters_{marker}.npz", "wb") as f:
            np.savez(f, *p_list)


def main(
    sample_path: str = SAMPLE_PATH,
    num_iter: int = SAVE_EVERY,
    save: bool = True,
    timestamp: str = TIMESTAMP,
) -> None:
    """Do the entire calculation from scratch."""
    sample = load_samples(glob.glob(sample_path))
    id_to_order = load_id_to_order_map()
    table = create_table(
        size=len(id_to_order), id_to_order=id_to_order, sample=sample, save=save
    )
    p, mt, w = setup_bradley_terry(matrix=table)
    # Force initial table deletion
    del table
    gc.collect()
    with open(f"data/{timestamp}_{len(sample)}/mt", "wb") as f:
        pickle.dump(mt, f)
    with open(f"data/{timestamp}_{len(sample)}/w", "wb") as f:
        pickle.dump(w, f)
    endless_iteration(
        datum=(p, mt, w),
        num_iter=num_iter,
        timestamp=timestamp,
        sample_size=len(sample),
    )


def resume(timestamp: str, num_iter: int = SAVE_EVERY) -> None:
    """Resume computation of the parameters from the last available iteration."""
    with open(glob.glob(f"data/{timestamp}_*/mt"), "rb") as f:
        mt = pickle.load(f)
    with open(glob.glob(f"data/{timestamp}_*/w"), "rb") as f:
        w = pickle.load(f)

    filename = sorted(glob.glob(f"data/{timestamp}_*/parameter_*.npy"))[-1]
    size = re.findall(r"_(\d+)\\parameter", filename)
    num = re.findall(r"_(\d+)\.npy", filename)
    with open(filename, "rb") as f:
        p = pickle.load(f)
    endless_iteration(
        datum=(p, mt, w),
        num_iter=num_iter,
        timestamp=timestamp,
        sample_size=size,
        start=num,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--number",
        metavar="N",
        type=int,
        default=SAVE_EVERY,
        help=f"number of iterations before saving partial data, default={SAVE_EVERY}",
    )
    parser.add_argument(
        "-r",
        "--resume",
        metavar="R",
        type=str,
        default="",
        help="data folder, default has type YYMMDD-HHMMSS_num",
    )
    args = parser.parse_args()
    if args.resume:
        resume(timestamp=args.resume, num_iter=args.number)
    else:
        main(num_iter=args.number)
