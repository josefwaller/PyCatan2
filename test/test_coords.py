from pycatan.board import Coords


def test_two_coords_are_equal():
    assert Coords(1, 2) == Coords(1, 2)


def test_can_use_coord_as_key_in_dict():
    d = {Coords(0, 1): True, Coords(1, 2): False}
    assert d[Coords(0, 1)]
    assert not d[Coords(1, 2)]
