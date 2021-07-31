from typing import Set

from pycatan.board import Board
from pycatan.coords import Coords
from pycatan.hex import Hex
from pycatan.hex import HexType

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
    print(set(board.corners.keys()))


def test_board_propery_keys_corners():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    print(board.corners)
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
