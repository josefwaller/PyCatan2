from pycatan.coord import Coord


def test_two_coords_are_equal():
    assert Coord(1, 2) == Coord(1, 2)


def test_can_use_coord_as_key_in_dict():
    d = {Coord(0, 1): True, Coord(1, 2): False}
    assert d[Coord(0, 1)]
    assert not d[Coord(1, 2)]
