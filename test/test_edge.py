from pycatan.edge import Edge
from pycatan.coords import Coords


def test_edge_holds_coords():
    e = Edge({Coords(3, 4), Coords(4, 4)})
    assert e.coords == {Coords(3, 4), Coords(4, 4)}
    assert e.coords == {Coords(4, 4), Coords(3, 4)}
