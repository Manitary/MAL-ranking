"""Tests"""

from typing import Iterator

import numpy as np
from numpy.typing import NDArray
from pytest import fixture

from models import ListNode, ListStatus, UserList, UserListEntry
from utils import create_table, iterate_parameter, setup_bradley_terry


@fixture(name="table_one_user_three_anime")
def fixture_table_one_user_three_anime() -> Iterator[NDArray[np.uint]]:
    """Small model table.

    Return the table for a single user voting A > B > C."""
    table = np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0]], dtype=np.uint)
    yield table


@fixture(name="table_two_users_four_anime")
def fixture_table_two_users_four_anime() -> Iterator[NDArray[np.uint]]:
    """Small non-trivial model table.

    Return the table for two users voting:
        A > B > C > D
        A > C > B > D"""
    table = np.array([[0, 2, 2, 2], [0, 0, 1, 2], [0, 1, 0, 2], [0, 0, 0, 0]])
    yield table


@fixture(name="wikipedia_table")
def fixture_wikipedia_table() -> Iterator[NDArray[np.uint]]:
    """Wikipedia example table."""
    table = np.array([[0, 2, 0, 1], [3, 0, 5, 0], [0, 3, 0, 1], [4, 0, 3, 0]])
    yield table


@fixture(name="sample_one_user")
def fixture_sample_one_user() -> Iterator[dict[int, UserList]]:
    """Sample containing one user."""
    sample = {
        1: [
            UserListEntry(
                node=ListNode(id=i, title="", main_picture={}),
                list_status=ListStatus(
                    status="completed",
                    score=10 - i,
                    num_watched_episodes=0,
                    is_rewatching=False,
                    updated_at="",
                ),
            )
            for i in range(3)
        ]
    }
    yield sample


def test_wikipedia_example_1(wikipedia_table: NDArray[np.uint]) -> None:
    """Example case from Wikipedia, 1 iteration."""
    p, mt, w, *_ = setup_bradley_terry(wikipedia_table, sample={}, io_map={})
    p = iterate_parameter(p=p, mt=mt, w=w)
    p = tuple((round(x, 3) for x in p))
    expected = (0.148, 0.304, 0.164, 0.384)
    assert p == expected


def test_wikipedia_example_20(wikipedia_table: NDArray[np.uint]) -> None:
    """Example case from Wikipedia, 20 iterations."""
    p, mt, w, *_ = setup_bradley_terry(wikipedia_table, sample={}, io_map={})
    for _ in range(20):
        p = iterate_parameter(p=p, mt=mt, w=w)
    p = tuple((round(x, 3) for x in p))
    expected = (0.139, 0.226, 0.143, 0.492)
    assert p == expected


def test_one_user_three_anime(table_one_user_three_anime: NDArray[np.uint]) -> None:
    """Test a simple case: 1 user, 3 anime ranked."""
    p, mt, w, *_ = setup_bradley_terry(table_one_user_three_anime, sample={}, io_map={})
    p = iterate_parameter(p=p, mt=mt, w=w)
    assert p[0] > p[1] > p[2]


def test_two_users_four_anime(table_two_users_four_anime: NDArray[np.uint]) -> None:
    """Test a simple case: 2 users, 4 anime ranked."""
    p, mt, w, *_ = setup_bradley_terry(table_two_users_four_anime, sample={}, io_map={})
    for _ in range(5):
        p = iterate_parameter(p=p, mt=mt, w=w)
        assert p[0] > p[1] == p[2] > p[3]


def test_create_table_one_user(
    sample_one_user: dict[int, UserList], table_one_user_three_anime: NDArray[np.uint]
) -> None:
    """Create a model table from one user data."""
    table = create_table(
        size=3, id_to_order={i: i for i in range(3)}, sample=sample_one_user, save=False
    )
    expected = table_one_user_three_anime
    assert np.array_equal(table, expected)
