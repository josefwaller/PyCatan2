from pycatan.hex import Hex
from pycatan.coord import Coord


def test_hex_holds_coords():
    h = Hex(Coord(1, 2))
    assert h.coord == Coord(1, 2)
