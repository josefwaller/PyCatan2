from typing import Set
import pytest

from pycatan.board import Board, BeginnerBoard, Coords, Hex, HexType, BuildingType
from pycatan import Player, Resource
from pycatan.errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
    NotConnectedError,
    RequiresSettlementError,
)
from .helpers import (
    get_resource_hand,
    add_free_settlement,
    add_free_city,
    add_free_road,
    add_free_road_from_path,
)

ONE_HEX_COORDS = {Coords(0, 0)}
SMALL_BOARD_COORDS = {
    Coords(0, 0),
    Coords(2, -1),
    Coords(1, 1),
    Coords(-1, 2),
    Coords(-2, 1),
    Coords(-1, -1),
    Coords(1, -2),
}


def generate_board_from_hex_coords(coords: Set[Coords]):
    hexes = set()
    for c in coords:
        hexes.add(Hex(c, HexType.FOREST, 6))
    return Board(hexes, harbors={}, robber=list(coords)[0])


def test_board_generates_intersections_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_intersections = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }
    assert set(board.intersections.keys()) == expected_intersections


def test_board_generates_intersections_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_intersections = set()
    for hex_coords in SMALL_BOARD_COORDS:
        for offset in Hex.CONNECTED_CORNER_OFFSETS:
            expected_intersections.add(hex_coords + offset)

    assert set(board.intersections.keys()) == expected_intersections


def test_board_propery_keys_intersections():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, intersection in board.intersections.items():
        assert key == intersection.coords


def test_board_generates_paths_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_paths = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    assert set(board.paths.keys()) == expected_paths


def test_board_generates_paths_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_paths_offsets = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    expected_paths = set()
    for offset in expected_paths_offsets:
        for h in SMALL_BOARD_COORDS:
            expected_paths.add(frozenset([h + o for o in offset]))

    assert set(board.paths.keys()) == expected_paths


def test_board_properly_keys_paths():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, path in board.paths.items():
        assert path.path_coords == set(key)


def test_cannot_build_in_middle_of_hex():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(InvalidCoordsError):
        board.add_intersection_building(player, Coords(0, 0), BuildingType.SETTLEMENT)


def test_cannot_build_on_top_of_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(CoordsBlockedError):
        board.add_intersection_building(
            player, Coords(1, -1), BuildingType.SETTLEMENT, ensure_connected=False
        )
        board.add_intersection_building(player, Coords(1, -1), BuildingType.SETTLEMENT)


def test_cannot_build_too_close_to_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(TooCloseToBuildingError):
        board.add_intersection_building(
            player, Coords(-2, 2), BuildingType.SETTLEMENT, ensure_connected=False
        )
        board.add_intersection_building(player, Coords(-3, 2), BuildingType.SETTLEMENT)


def test_cannot_add_isloated_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(NotConnectedError):
        board.add_intersection_building(player, Coords(1, 0), BuildingType.SETTLEMENT)


def test_can_add_settlement():
    board = BeginnerBoard()
    player = Player()
    board.add_intersection_building(
        player, Coords(1, 0), BuildingType.SETTLEMENT, ensure_connected=False
    )
    assert board.intersections[Coords(1, 0)].building is not None
    assert (
        board.intersections[Coords(1, 0)].building.building_type
        == BuildingType.SETTLEMENT
    )


def test_get_connected_intersections():
    board = BeginnerBoard()
    assert board.get_intersection_connected_intersections(
        board.intersections[Coords(1, -1)]
    ) == {
        board.intersections[Coords(2, -2)],
        board.intersections[Coords(0, -1)],
        board.intersections[Coords(1, 0)],
    }
    assert board.get_intersection_connected_intersections(
        board.intersections[Coords(-3, 2)]
    ) == {
        board.intersections[Coords(-2, 2)],
        board.intersections[Coords(-3, 1)],
        board.intersections[Coords(-4, 3)],
    }


def test_board_get_yield():
    board = BeginnerBoard()
    player = Player()
    board.add_intersection_building(
        player,
        coords=Coords(2, 0),
        building_type=BuildingType.SETTLEMENT,
        ensure_connected=False,
    )
    assert board.get_yield_for_roll(6)[player].total_yield == get_resource_hand(brick=1)
    assert board.get_yield_for_roll(2)[player].total_yield == get_resource_hand(wool=1)
    assert board.get_yield_for_roll(4)[player].total_yield == get_resource_hand(wool=1)


def test_board_get_yield_multiple_hexes():
    board = Board(
        {
            Hex(coords=Coords(0, 0), hex_type=HexType.FOREST, token_number=6),
            Hex(coords=Coords(1, 1), hex_type=HexType.FOREST, token_number=6),
            Hex(coords=Coords(-1, 2), hex_type=HexType.HILLS, token_number=6),
            Hex(coords=Coords(-2, 1), hex_type=HexType.DESERT),
        }
    )
    player = Player()
    board.add_intersection_building(
        player,
        coords=Coords(0, 1),
        building_type=BuildingType.SETTLEMENT,
        ensure_connected=False,
    )
    assert board.get_yield_for_roll(6)[player].total_yield == get_resource_hand(
        lumber=2, brick=1
    )


def test_cannot_add_isolated_road():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(NotConnectedError):
        board.add_path_building(
            player=player,
            path_coords={Coords(1, 0), Coords(1, -1)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_between_unconnected_intersections():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(ValueError):
        board.add_path_building(
            player=player,
            path_coords={Coords(0, -1), Coords(0, 1)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_to_middle_of_hex():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(ValueError):
        board.add_path_building(
            player=player,
            path_coords={Coords(0, -2), Coords(0, 0)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_on_top_of_other():
    board = BeginnerBoard()
    player = Player()
    path_coords = {Coords(1, 0), Coords(0, 1)}
    board.add_path_building(
        player=player,
        path_coords=path_coords,
        building_type=BuildingType.ROAD,
        ensure_connected=False,
    )
    with pytest.raises(CoordsBlockedError):
        board.add_path_building(
            player=player, path_coords=path_coords, building_type=BuildingType.ROAD
        )


def test_cannot_add_city_invalid_coords():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(InvalidCoordsError):
        board.add_intersection_building(
            player, Coords(0, 0), building_type=BuildingType.CITY
        )


def test_cannot_add_city_without_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(RequiresSettlementError):
        board.add_intersection_building(
            player, Coords(1, 0), building_type=BuildingType.CITY
        )


def test_cannot_add_city_on_top_of_other_player_settlement():
    board = BeginnerBoard()
    pOne = Player()
    pTwo = Player()
    board.add_intersection_building(
        pOne,
        Coords(1, 0),
        building_type=BuildingType.SETTLEMENT,
        ensure_connected=False,
    )
    with pytest.raises(RequiresSettlementError):
        board.add_intersection_building(
            pTwo, Coords(1, 0), building_type=BuildingType.CITY
        )


def test_can_add_city():
    b = BeginnerBoard()
    p = Player()
    add_free_city(b, p, Coords(0, -1))
    assert b.intersections[Coords(0, -1)].building.building_type == BuildingType.CITY


def test_city_adds_twice_yield_for_city():
    b = BeginnerBoard()
    p = Player()
    add_free_city(b, p, Coords(-1, 0))
    assert b.get_yield_for_roll(4)[p].total_yield == get_resource_hand(grain=2)


def test_city_adds_twice_many_hexes():
    b = BeginnerBoard()
    p = Player()
    add_free_city(b, p, Coords(0, 2))
    assert b.get_yield_for_roll(3)[p].total_yield == get_resource_hand(lumber=2)
    assert b.get_yield_for_roll(10)[p].total_yield == get_resource_hand(brick=2)
    assert b.get_yield_for_roll(4)[p].total_yield == get_resource_hand(wool=2)


def test_city_add_twice_many_cities():
    b = BeginnerBoard()
    p = Player()
    add_free_city(b, p, Coords(1, 0))
    add_free_city(b, p, Coords(2, -2))
    add_free_city(b, p, Coords(3, -1))
    assert b.get_yield_for_roll(6)[p].total_yield == get_resource_hand(brick=6)


def test_robber_stop_yield():
    b = BeginnerBoard()
    p = Player()
    add_free_settlement(b, p, Coords(1, 0))
    b.robber = Coords(1, 1)
    assert not b.get_yield_for_roll(4)


def test_robber_doesnt_stop_yield_after_leaving():
    b = BeginnerBoard()
    p = Player()
    add_free_settlement(b, p, Coords(1, 0))
    b.robber = Coords(1, 1)
    b.robber = Coords(0, 0)
    assert b.get_yield_for_roll(4)[p].total_yield == get_resource_hand(wool=1)


def test_is_valid_hex_coords():
    b = BeginnerBoard()
    assert b.is_valid_hex_coords(Coords(0, 0))
    assert b.is_valid_hex_coords(Coords(1, 1))
    assert b.is_valid_hex_coords(Coords(2, -1))
    assert b.is_valid_hex_coords(Coords(-1, -1))
    assert not b.is_valid_hex_coords(Coords(1, -1))
    assert not b.is_valid_hex_coords(Coords(2, -2))
    assert not b.is_valid_hex_coords(Coords(-2, 2))
    assert not b.is_valid_hex_coords(Coords(-2, 0))


def test_board_properly_keys_harbors():
    b = BeginnerBoard()
    for path_coords, harbor in b.harbors.items():
        assert harbor.path_coords == path_coords


def test_board_adds_harbors_to_players():
    b = BeginnerBoard()
    p = Player()
    add_free_settlement(b, p, Coords(1, 0))
    assert len(p.connected_harbors) == 0
    add_free_settlement(b, p, Coords(3, 2))
    assert len(p.connected_harbors) == 0
    add_free_settlement(b, p, Coords(4, 0))
    assert len([h for h in p.connected_harbors if h.resource == Resource.GRAIN]) == 1
    add_free_settlement(b, p, Coords(3, -4))
    assert len([h for h in p.connected_harbors if h.resource == Resource.GRAIN]) == 1
    assert len([h for h in p.connected_harbors if h.resource == Resource.LUMBER]) == 1


def test_get_longest_road():
    b = BeginnerBoard()
    p = Player()
    assert b.calculate_player_longest_road(p) == 0
    add_free_road(b, p, path_coords={Coords(1, 0), Coords(0, 1)})
    assert b.calculate_player_longest_road(p) == 1
    add_free_road(b, p, path_coords={Coords(0, 2), Coords(0, 1)})
    add_free_road(b, p, path_coords={Coords(0, 2), Coords(-1, 3)})
    add_free_road(b, p, path_coords={Coords(0, 2), Coords(1, 2)})
    add_free_road(b, p, path_coords={Coords(1, 2), Coords(2, 1)})
    assert b.calculate_player_longest_road(p) == 4


def test_get_longest_road_complicated():
    b = BeginnerBoard()
    p = Player()
    road_paths = (
        (
            Coords(1, -3),
            Coords(2, -3),
            Coords(3, -4),
            Coords(4, -4),
            Coords(4, -3),
            Coords(5, -3),
        ),
        (
            Coords(-1, 4),
            Coords(-1, 3),
            Coords(0, 2),
            Coords(0, 1),
            Coords(1, 0),
            Coords(1, -1),
            Coords(0, -1),
            Coords(-1, 0),
            Coords(-1, 1),
        ),
        (
            Coords(-4, 0),
            Coords(-3, -1),
            Coords(-2, -1),
            Coords(-1, -2),
            Coords(0, -2),
            Coords(1, -3),
            Coords(1, -4),
        ),
    )
    # Add the first road path
    add_free_road_from_path(b, p, road_paths[0])
    assert b.calculate_player_longest_road(p) == 5
    # Add the second path
    add_free_road_from_path(b, p, road_paths[1])
    assert b.calculate_player_longest_road(p) == 8
    # Add the third path
    add_free_road_from_path(b, p, road_paths[2])
    assert b.calculate_player_longest_road(p) == 10


def test_calculate_longest_road_multiple_players():
    b = BeginnerBoard()
    p1 = Player()
    p2 = Player()
    road_paths = (
        (
            Coords(5, -2),
            Coords(5, -3),
            Coords(4, -3),
            Coords(4, -4),
            Coords(3, -4),
            Coords(3, -5),
        ),
        (Coords(3, -4), Coords(2, -3), Coords(2, -2), Coords(1, -1), Coords(1, 0)),
        (Coords(2, -2), Coords(3, -2), Coords(3, -1), Coords(4, -1), Coords(5, -2)),
    )
    # Add the first road
    add_free_road_from_path(b, p1, road_paths[0])
    assert b.calculate_player_longest_road(p1) == 5
    assert b.calculate_player_longest_road(p2) == 0
    # Add the second path
    add_free_road_from_path(b, p2, road_paths[1])
    assert b.calculate_player_longest_road(p1) == 5
    assert b.calculate_player_longest_road(p2) == 4
    # Add the third path
    add_free_road_from_path(b, p2, road_paths[2])
    assert b.calculate_player_longest_road(p1) == 5
    assert b.calculate_player_longest_road(p2) == 6


def test_allow_building_road_only_connected_to_settlement():
    b = BeginnerBoard()
    p = Player()
    add_free_settlement(b, p, Coords(1, 0))
    b.add_path_building(p, BuildingType.ROAD, path_coords={Coords(1, 0), Coords(0, 1)})
    assert b.paths[frozenset({Coords(1, 0), Coords(0, 1)})].building.owner == p


def test_can_break_longest_road_with_settlement():
    b = BeginnerBoard()
    p1 = Player()
    p2 = Player()
    path = (Coords(1, -1), Coords(1, 0), Coords(0, 1), Coords(0, 2), Coords(-1, 3))
    add_free_road_from_path(b, p1, path)
    assert b.calculate_player_longest_road(p1) == 4
    add_free_settlement(b, p2, Coords(0, 1))
    assert b.calculate_player_longest_road(p1) == 2


def test_cannot_build_road_through_enemy_settlement():
    b = BeginnerBoard()
    p1 = Player()
    p2 = Player()
    add_free_road(b, p1, {Coords(1, 0), Coords(0, 1)})
    add_free_settlement(b, p2, Coords(0, 1))
    with pytest.raises(NotConnectedError):
        b.add_path_building(
            p1,
            building_type=BuildingType.ROAD,
            path_coords={Coords(0, 1), Coords(0, 2)},
        )


def test_board_into_string(snapshot):
    snapshot.assert_match(str(BeginnerBoard()), "beginner_board.txt")


def test_board_prints_nicely(snapshot, capsys):
    print(BeginnerBoard())
    snapshot.assert_match(capsys.readouterr().out, "beginner_board.txt")


def test_board_is_valid_settlement_position():
    b = BeginnerBoard()
    p = Player()
    b.add_intersection_building(
        player=p,
        coords=Coords(1, 0),
        ensure_connected=False,
        building_type=BuildingType.SETTLEMENT,
    )
    assert not b.is_valid_settlement_coords(p, Coords(1, 1), ensure_connected=False)


def test_get_valid_settlement_coords():
    b = BeginnerBoard()
    p = Player()
    assert len(b.get_valid_settlement_coords(p, ensure_connected=False)) == len(
        b.intersections
    )
    assert len(b.get_valid_settlement_coords(p)) == 0
    b.add_intersection_building(
        player=p,
        coords=Coords(1, 0),
        ensure_connected=False,
        building_type=BuildingType.SETTLEMENT,
    )
    assert (
        len(b.get_valid_settlement_coords(p, ensure_connected=False))
        == len(b.intersections) - 4
    )


def test_get_valid_settlement_coords_connected():
    b = BeginnerBoard()
    p = Player()
    assert not b.get_valid_settlement_coords(p)
    b.add_path_building(
        player=p,
        path_coords={Coords(1, 0), Coords(0, 1)},
        ensure_connected=False,
        building_type=BuildingType.ROAD,
    )
    assert b.get_valid_settlement_coords(p) == {Coords(0, 1), Coords(1, 0)}


def test_get_valid_settlement_coords_too_close():
    b = BeginnerBoard()
    p = Player()
    b.add_path_building(
        player=p,
        path_coords={Coords(1, 0), Coords(0, 1)},
        building_type=BuildingType.ROAD,
        ensure_connected=False,
    )
    b.add_intersection_building(
        player=p, coords=Coords(1, 0), building_type=BuildingType.SETTLEMENT
    )
    assert not b.get_valid_settlement_coords(p)
    b.add_path_building(
        player=p,
        path_coords={Coords(0, 1), Coords(-1, 1)},
        building_type=BuildingType.ROAD,
    )
    assert b.get_valid_settlement_coords(p) == {Coords(-1, 1)}
