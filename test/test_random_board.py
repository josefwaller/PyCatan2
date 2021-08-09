from pycatan.board import RandomBoard, HexType


def test_has_right_amount_hex_types():
    b = RandomBoard()
    assert len(b.hexes) == 19
    hex_types = [h.hex_type for h in b.hexes.values()]
    assert hex_types.count(HexType.FOREST) == 4
    assert hex_types.count(HexType.FIELDS) == 4
    assert hex_types.count(HexType.PASTURE) == 4
    assert hex_types.count(HexType.HILLS) == 3
    assert hex_types.count(HexType.MOUNTAINS) == 3
    assert hex_types.count(HexType.DESERT) == 1


def test_has_right_amount_numbered_tokens():
    b = RandomBoard()
    nums = [h.token_number for h in b.hexes.values()]
    for i in [2, 12]:
        assert nums.count(i) == 1
    for i in [3, 4, 5, 6, 8, 9, 10, 11]:
        assert nums.count(i) == 2
