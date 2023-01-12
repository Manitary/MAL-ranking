from collections import defaultdict, OrderedDict
import numpy as np

FILENAME = "data/parameter_1_20230112-213555.npy"

with open(FILENAME, "rb") as f:
    parameter = np.load(f)

ranking = defaultdict(set)
for i, x in enumerate(parameter):
    ranking[x].add(i)

ranking = OrderedDict(sorted(ranking.items()))


# with open(FILENAME, "rb") as f:
#     p_file = np.load(f)
#     p_list = [p_file[f"arr_{x}"] for x in range(len(p_file))]
