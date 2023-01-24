"""Estimate the parameters of the Bradley-Terry model for a sample of MAL users."""

import re
import glob
import argparse
import pickle
import json
from pathlib import Path
from itertools import count
from collections import Counter
import numpy as np
from tqdm import tqdm
from utils import (
    create_table,
    setup_bradley_terry,
    iterate_parameter,
    load_samples,
    get_anime_ids_from_sample,
    TIMESTAMP,
)

SAMPLE_PATH = "data/samples/sample_*.json"
ANIME_PATH = "data/anime"
SAVE_EVERY = 50


def step_iteration(
    p: np.ndarray,
    mt: np.ndarray,
    w: np.ndarray,
    num_iter: int,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Iterate the parameter num_iter times.

    Display the max delta of a single parameter between first and last iteration."""
    p_list = [np.copy(p)]
    for _ in tqdm(range(num_iter)):
        p = iterate_parameter(p=p, mt=mt, w=w)
        p_list.append(np.copy(p))
    delta = np.abs(p - p_list[0])
    last_delta = np.abs(p_list[-1] - p_list[-2])
    print(
        f"""Iteration max delta: {np.amax(delta)} at position {np.argmax(delta)}
Last step max delta: {np.amax(last_delta)} at position {np.argmax(delta)}"""
    )
    return p, p_list, delta, last_delta


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
        p, p_list, _, last_delta = step_iteration(p=p, mt=mt, w=w, num_iter=num_iter)
        with open(f"data/{timestamp}_{sample_size}/parameter_{marker}.npy", "wb") as f:
            np.save(f, p)
        with open(f"data/{timestamp}_{sample_size}/parameters_{marker}.npz", "wb") as f:
            np.savez(f, *p_list)
        with open(f"data/{timestamp}_{sample_size}/last_delta_{marker}.npy", "wb") as f:
            np.save(f, last_delta)
        with open(f"data/{timestamp}_{sample_size}/error_pct_{marker}.npy", "wb") as f:
            np.save(
                f, np.divide(last_delta, p, out=np.zeros_like(p), where=p != 0) * 100
            )


def initialise(
    sample_path: str = SAMPLE_PATH,
    save: bool = True,
    timestamp: str = TIMESTAMP,
    cutoff: int = 0,
    curb: int = 0,
) -> None:
    """Do the entire calculation from scratch."""
    sample = load_samples(*glob.glob(sample_path))
    sample_anime_ids = get_anime_ids_from_sample(sample)
    id_to_order = {j: i for i, j in enumerate(sorted(sample_anime_ids))}
    Path(f"data/{timestamp}_{len(sample)}").mkdir(parents=True, exist_ok=True)
    with open(f"data/{timestamp}_{len(sample)}/cutoff", "w", encoding="utf8") as f:
        f.write(str(cutoff))
    with open(f"data/{timestamp}_{len(sample)}/map_id_order", "wb") as f:
        pickle.dump(id_to_order, f)
    order_to_id = dict(enumerate(sorted(sample_anime_ids)))
    with open(f"data/{timestamp}_{len(sample)}/map_order_id", "wb") as f:
        pickle.dump(order_to_id, f)
    table = create_table(
        size=len(id_to_order), id_to_order=id_to_order, sample=sample, save=save
    )
    p, mt, w, _, new_to_old = setup_bradley_terry(
        matrix=table,
        sample=sample,
        io_map=id_to_order,
        curb=curb,
        cutoff=cutoff,
    )
    reduced_order_to_id = {i: order_to_id[new_to_old[i]] for i in range(p.shape[0])}
    reduced_id_to_order = {j: i for i, j in reduced_order_to_id.items()}
    with open(f"data/{timestamp}_{len(sample)}/reduced_map_id_order", "wb") as f:
        pickle.dump(reduced_id_to_order, f)
    with open(f"data/{timestamp}_{len(sample)}/reduced_map_order_id", "wb") as f:
        pickle.dump(reduced_order_to_id, f)
    with open(f"data/{timestamp}_{len(sample)}/mt.npy", "wb") as f:
        np.save(f, mt)
    with open(f"data/{timestamp}_{len(sample)}/w.npy", "wb") as f:
        np.save(f, w)
    with open(f"data/{timestamp}_{len(sample)}/p.npy", "wb") as f:
        np.save(f, p)


def iterate(timestamp: str, num_iter: int = SAVE_EVERY) -> None:
    """Resume computation of the parameters from the last available iteration."""
    with open(glob.glob(f"data/{timestamp}_*/mt.npy")[0], "rb") as f:
        mt = np.load(f)
    with open(glob.glob(f"data/{timestamp}_*/w.npy")[0], "rb") as f:
        w = np.load(f)
    filenames = sorted(glob.glob(f"data/{timestamp}_*/parameter_*.npy"))
    if filenames:
        filename = filenames[-1]
        size = re.findall(r"_(\d+)\\parameter", filename)[0]
        num = int(re.findall(r"_(\d+)\.npy", filename)[0])
        with open(filename, "rb") as f:
            p = np.load(f)
    else:
        filename = glob.glob(f"data/{timestamp}_*/p.npy")[0]
        size = re.findall(r"_(\d+)\\p", filename)[0]
        num = 0
        with open(filename, "rb") as f:
            p = np.load(f)
    endless_iteration(
        datum=(p, mt, w),
        num_iter=num_iter,
        timestamp=timestamp,
        sample_size=size,
        start=num,
    )


def extract_list_from_parameter(
    p: np.ndarray, f: dict[int, int], mal: dict[int, dict]
) -> list[tuple[int, float]]:
    """Transform the parameter vector into a list of dictionaries (ID, title, parameter)."""
    return sorted(
        (
            {"mal_ID": f[i], "title": mal[f[i]]["title"], "parameter": v}
            for i, v in enumerate(p)
            if f[i] in mal
        ),
        key=lambda x: x["parameter"],
        reverse=True,
    )


def convert_parameter_for_website(
    p: np.ndarray,
    mt: np.ndarray,
    f: dict[int, int],
    mal: dict[int, dict],
    sample: dict,
    e: np.ndarray,
) -> None:
    """Compute data used for the website from the results."""
    counter = Counter()
    for _, user_list in sample.items():
        for entry in user_list:
            if entry["list_status"]["status"] in {"completed", "dropped"}:
                counter[entry["node"]["id"]] += 1
    return sorted(
        (
            {
                "mal_ID": f[i],
                "parameter": v,
                "num_comparisons": int(np.sum(mt[i])),
                "num_lists": counter[f[i]],
                "pct_lists": counter[f[i]] / len(sample) * 100,
                "rel_error_pct": float(e[i]),
            }
            for i, v in enumerate(p)
            if f[i] in mal
        ),
        key=lambda x: x["parameter"],
        reverse=True,
    )


def extract_list_for_website(timestamp: str, sample_path: str = SAMPLE_PATH) -> None:
    """Compute most recent data making it usable for the website."""
    sample = load_samples(*glob.glob(sample_path))
    with open("data/anime", "rb") as f:
        anime = pickle.load(f)
    path = glob.glob(f"data/{timestamp}_*")[0]
    num = int(re.findall(r"_(\d+)$", path)[0])
    list_p = sorted(glob.glob(f"{path}/parameter_*.npy"), key=lambda x: (len(x), x))[-1]
    list_e = sorted(glob.glob(f"{path}/error_pct_*.npy"), key=lambda x: (len(x), x))[-1]
    with open(list_p, "rb") as f:
        p = np.load(f)
    with open(list_e, "rb") as f:
        e = np.load(f)
    with open(f"{path}/mt.npy", "rb") as f:
        mt = np.load(f)
    with open(f"{path}/reduced_map_order_id", "rb") as f:
        map_order_id = pickle.load(f)
    with open(f"{path}/cutoff", "r", encoding="utf8") as f:
        cutoff = int(f.read())
    with open(f"docs/data/{num}_{cutoff}.json", "w", encoding="utf8") as f:
        json.dump(
            convert_parameter_for_website(
                p=p, mt=mt, f=map_order_id, mal=anime, sample=sample, e=e
            ),
            f,
        )


def extract_list(timestamp: str) -> None:
    """Compute the sorted list of anime IDs from the computed parameters."""
    path = glob.glob(f"data/{timestamp}_*")[0]
    with open("data/anime", "rb") as f:
        mal = pickle.load(f)
    with open(f"{path}/reduced_map_order_id", "rb") as f:
        map_order_id = pickle.load(f)
    for p_path in tqdm(glob.glob(f"{path}/parameter_*.npy")):
        num = int(re.findall(r"parameter_(\d+).npy", p_path)[0])
        with open(p_path, "rb") as f:
            p = np.load(f)
        with open(f"{path}/list_{num}.json", "w", encoding="utf8") as f:
            json.dump(extract_list_from_parameter(p, map_order_id, mal), f)


def extract_mal_info(
    source_path: str = "data/anime", destination_path: str = "docs/data/anime.json"
) -> None:
    """Create a JSON copy of a reduced dictionary with selected entries."""
    with open(source_path, "rb") as f:
        anime = pickle.load(f)
    new_anime = {
        anime_id: {
            "title": entry["title"],
            "picture": entry["main_picture"]["medium"]
            if "main_picture" in entry
            else None,
            "title_en": entry["alternative_titles"]["en"]
            if "alternative_titles" in entry and "en" in entry["alternative_titles"]
            else None,
            "score": entry["mean"] if "mean" in entry else None,
            "rank": entry["rank"] if "rank" in entry else None,
            "popularity": entry["popularity"] if "popularity" in entry else None,
        }
        for anime_id, entry in anime.items()
    }
    with open(destination_path, "w", encoding="utf8") as f:
        json.dump(new_anime, f)


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
        "-p",
        "--prepare",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--iterate",
        metavar="I",
        type=str,
        default="",
        help="timestamp on the data folder, by default it has type YYMMDD-HHMMSS",
    )
    parser.add_argument(
        "-c",
        "--cutoff",
        metavar="C",
        type=int,
        default=0,
        help="cutoff of total comparisons to include an entry, default=0",
    )
    parser.add_argument(
        "-f",
        "--filter",
        metavar="F",
        type=int,
        default=0,
        help="pre-filter by number of lists with the anime",
    )
    parser.add_argument(
        "-l",
        "--list",
        metavar="L",
        type=str,
        default="",
        help="timestamp on the data folder, by default it has type YYMMDD-HHMMSS",
    )
    parser.add_argument(
        "-w",
        "--website",
        action="store_true",
    )
    args = parser.parse_args()
    if args.prepare:
        initialise(cutoff=args.cutoff, curb=args.filter)
    elif args.iterate:
        iterate(timestamp=args.iterate, num_iter=args.number)
    elif args.list:
        if args.website:
            extract_list_for_website(timestamp=args.list)
        else:
            extract_list(timestamp=args.list)
