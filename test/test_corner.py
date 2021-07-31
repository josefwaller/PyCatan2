from pycatan.corner import Corner
from pycatan.coords import Coords


def test_corner_holds_coords():
    c = Corner(Coords(3, 4))
    assert c.coords == Coords(3, 4)
