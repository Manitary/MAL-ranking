import json
import time
from itertools import combinations
import numpy

SOURCE_FILE = "random_sample_10000_12012023.txt"
MATRIX_FILE = f"matrix_{SOURCE_FILE[:-4]}"
PARAMETER_FILE = f"parameter_{SOURCE_FILE[:-4]}"
MAL_ANIME_NUM = 54220


def update_parameter(
    p: numpy.ndarray, mt: numpy.ndarray, w: numpy.ndarray
) -> numpy.ndarray:
    d = numpy.fromiter(
        iter=(1 if w[i] == 0 else sum(mt[i] / (p[i] + p)) for i in range(p.shape[0])),
        dtype=float,
    )
    new = w / d
    return new / sum(new)


def main() -> None:
    print(f"loading data from {SOURCE_FILE}")
    with open(file=SOURCE_FILE, mode="r", encoding="utf8") as f:
        data: dict = json.loads(f.read())

    matrix = numpy.zeros((MAL_ANIME_NUM, MAL_ANIME_NUM), dtype=int)

    print("generating matrix")
    for strnum, info in data.items():
        print("Processing", int(strnum))
        if not info["list"]:
            continue
        for a1, a2 in combinations(info["list"], 2):
            if "status" not in a1["list_status"] or "status" not in a2["list_status"]:
                continue
            if (
                a1["list_status"]["status"] == "plan_to_watch"
                or a2["list_status"]["status"] == "plan_to_watch"
            ):
                continue
            n1 = a1["node"]["id"] - 1
            n2 = a2["node"]["id"] - 1
            s1 = a1["list_status"]["score"]
            s2 = a2["list_status"]["score"]
            if s1 == 0 and a1["list_status"]["status"] == "dropped":
                s1 = 0.1
            if s2 == 0 and a2["list_status"]["status"] == "dropped":
                s2 = 0.1
            if s1 > 0 and s2 > 0:
                if s1 > s2:
                    matrix[n1, n2] += 1
                elif s1 < s2:
                    matrix[n2, n1] += 1

    with open(MATRIX_FILE, "wb") as f:
        numpy.save(f, matrix)

    print("sum with transpose")
    matrix_t = matrix + matrix.transpose()
    print("calculating W")
    w = numpy.sum(matrix, axis=1)
    print("initialising parameter")
    parameter = numpy.fromiter(iter=(0 if x == 0 else 1 for x in w), dtype=float)

    print("starting iterative process")
    for i in range(50):
        t1 = time.perf_counter()
        parameter = update_parameter(p=parameter, mt=matrix_t, w=w)
        t2 = time.perf_counter()
        print(i, t2 - t1)

    with open(PARAMETER_FILE, "wb") as f:
        numpy.save(f, parameter)

    print("done")


if __name__ == "__main__":
    main()
