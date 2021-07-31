from typing import Set

from pycatan.board import Board
from pycatan.coords import Coords
from pycatan.hex import Hex


def generate_board_from_hex_coords(coords: Set[Coords]):
    hexes = {}
    for c in coords:
        hexes[c] = Hex(c)
    return Board(hexes)


def test_board_generates_corners_one_hex():
    board = generate_board_from_hex_coords({Coords(0, 0)})
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
    hexes = {
        Coords(0, 0),
        Coords(2, -1),
        Coords(1, -1),
        Coords(-1, 2),
        Coords(-2, 1),
        Coords(-1, 1),
        Coords(1, -2),
    }
    board = generate_board_from_hex_coords(hexes)
    expected_corners = set()
    for hex_coords in hexes:
        for offset in Hex.CONNECTED_CORNER_OFFSETS:
            expected_corners.add(hex_coords + offset)

    assert set(board.corners.keys()) == expected_corners


def test_board_propery_keys_corners():
    board = generate_board_from_hex_coords({Coords(0, 0)})
    print(board.corners)
    for key, corner in board.corners.items():
        assert key == corner.coords


def test_board_generates_edges():
    board = Board({Coords(0, 0): Hex(Coords(0, 0))})
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


def test_board_properly_keys_edges():
    board = Board({Coords(0, 0): Hex(Coords(0, 0))})
    for (key, edge) in board.edges:
        assert edge.coords == key
