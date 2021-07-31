from typing import Set
import pytest

from pycatan.board import Board, BeginnerBoard
from pycatan.coords import Coords
from pycatan.hex import Hex, HexType
from pycatan.building_type import BuildingType
from pycatan.player import Player
from pycatan.errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
)

ONE_HEX_COORDS = {Coords(0, 0)}
SMALL_BOARD_COORDS = {
    Coords(0, 0),
    Coords(2, -1),
    Coords(1, 1),
    Coords(-1, 2),
    Coords(-2, 1),
    Coords(-1, -1),
    Coords(1, -2),
}


def generate_board_from_hex_coords(coords: Set[Coords]):
    hexes = set()
    for c in coords:
        hexes.add(Hex(c, HexType.FOREST, 6))
    return Board(hexes)


def test_board_generates_corners_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_corners = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }
    assert set(board.corners.keys()) == expected_corners


def test_board_generates_corners_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_corners = set()
    for hex_coords in SMALL_BOARD_COORDS:
        for offset in Hex.CONNECTED_CORNER_OFFSETS:
            expected_corners.add(hex_coords + offset)

    assert set(board.corners.keys()) == expected_corners


def test_board_propery_keys_corners():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, corner in board.corners.items():
        assert key == corner.coords


def test_board_generates_edges_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_edges = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    assert set(board.edges.keys()) == expected_edges


def test_board_generates_edges_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_edges_offsets = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    expected_edges = set()
    for offset in expected_edges_offsets:
        for h in SMALL_BOARD_COORDS:
            expected_edges.add(frozenset([h + o for o in offset]))

    assert set(board.edges.keys()) == expected_edges


def test_board_properly_keys_edges():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, edge in board.edges.items():
        assert edge.coords == set(key)


def test_cannot_build_in_middle_of_hex():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(InvalidCoordsError):
        board.add_settlement(player, Coords(0, 0))


def test_cannot_build_on_top_of_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(CoordsBlockedError):
        board.add_settlement(player, Coords(1, -1))
        board.add_settlement(player, Coords(1, -1))


def test_cannot_build_too_close_to_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(TooCloseToBuildingError):
        board.add_settlement(player, Coords(-2, 2))
        board.add_settlement(player, Coords(-3, 2))


def test_can_add_settlement():
    board = BeginnerBoard()
    player = Player()
    board.add_settlement(player, Coords(1, 0))
    assert board.corners[Coords(1, 0)].building is not None
    assert board.corners[Coords(1, 0)].building.building_type == BuildingType.SETTLEMENT


def test_get_connected_corners():
    board = BeginnerBoard()
    assert board.get_corner_connected_corners(board.corners[Coords(1, -1)]) == {
        board.corners[Coords(2, -2)],
        board.corners[Coords(0, -1)],
        board.corners[Coords(1, 0)],
    }
    assert board.get_corner_connected_corners(board.corners[Coords(-3, 2)]) == {
        board.corners[Coords(-2, 2)],
        board.corners[Coords(-3, 1)],
        board.corners[Coords(-4, 3)],
    }
