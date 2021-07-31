from pycatan.board import BeginnerBoard
from pycatan.hex import Hex


def test_no_hexes_are_adjacent():
    board = BeginnerBoard()
    for hex_coord in board.hexes.keys():
        for offset in Hex.CONNECTED_CORNER_OFFSETS:
            assert hex_coord + offset not in board.hexes.keys()
