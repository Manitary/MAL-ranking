"""Tests"""

import numpy as np
from pytest import fixture
from utils import setup_bradley_terry, iterate_parameter


@fixture(name="table_one_user_three_anime")
def fixture_table_one_user_three_anime() -> np.ndarray:
    """Small model table."""
    table = np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0]], dtype=int)
    yield table


@fixture(name="wikipedia_table")
def fixture_wikipedia_table() -> np.ndarray:
    """Wikipedia example table."""
    table = np.array([[0, 2, 0, 1], [3, 0, 5, 0], [0, 3, 0, 1], [4, 0, 3, 0]])
    yield table


def test_wikipedia_example_1(wikipedia_table: np.ndarray) -> None:
    """Example case from Wikipedia, 1 iteration."""
    p, mt, w = setup_bradley_terry(wikipedia_table)
    p = iterate_parameter(p=p, mt=mt, w=w)
    p = tuple((round(x, 3) for x in p))
    expected = (0.148, 0.304, 0.164, 0.384)
    assert p == expected


def test_wikipedia_example_20(wikipedia_table: np.ndarray) -> None:
    """Example case from Wikipedia, 20 iterations."""
    p, mt, w = setup_bradley_terry(wikipedia_table)
    for _ in range(20):
        p = iterate_parameter(p=p, mt=mt, w=w)
    p = tuple((round(x, 3) for x in p))
    expected = (0.139, 0.226, 0.143, 0.492)
    assert p == expected


def test_one_user_three_anime(table_one_user_three_anime: np.ndarray) -> None:
    """Test a simple case: 1 user, 3 anime ranked."""
    p, mt, w = setup_bradley_terry(table_one_user_three_anime)
    p = iterate_parameter(p=p, mt=mt, w=w)
    assert p[0] > p[1] > p[2]
