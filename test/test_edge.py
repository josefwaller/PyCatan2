from pycatan.path import Path
from pycatan.coords import Coords


def test_path_holds_coords():
    e = Path({Coords(3, 4), Coords(4, 4)})
    assert e.path_coords == {Coords(3, 4), Coords(4, 4)}
    assert e.path_coords == {Coords(4, 4), Coords(3, 4)}
