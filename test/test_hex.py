from pycatan.hex import Hex
from pycatan.coords import Coords
from pycatan.hex_type import HexType


def test_hex_holds_coords():
    h = Hex(Coords(1, 2), HexType.FOREST, 8)
    assert h.coords == Coords(1, 2)
