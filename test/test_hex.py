from pycatan.board import Hex, Coords, HexType


def test_hex_holds_coords():
    h = Hex(Coords(1, 2), HexType.FOREST, 8)
    assert h.coords == Coords(1, 2)
