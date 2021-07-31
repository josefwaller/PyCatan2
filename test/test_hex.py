from pycatan.hex import Hex
from pycatan.coords import Coords


def test_hex_holds_coords():
    h = Hex(Coords(1, 2))
    assert h.coords == Coords(1, 2)
