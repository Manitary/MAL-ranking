from collections import defaultdict, OrderedDict
import numpy

FILENAME = "parameter_random_sample_10000_12012023.npy"

with open(FILENAME, "rb") as f:
    parameter = numpy.load(f)

ranking = defaultdict(set)
for i, x in enumerate(parameter, start=1):
    ranking[x].add(i)


ranking = OrderedDict(sorted(ranking.items()))
