from pycatan.board import Intersection, Coords


def test_intersection_holds_coords():
    c = Intersection(Coords(3, 4))
    assert c.coords == Coords(3, 4)
