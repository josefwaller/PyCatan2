from typing import Set
import pytest

from pycatan.board import Board, BeginnerBoard
from pycatan.coords import Coords
from pycatan.hex import Hex, HexType
from pycatan.building_type import BuildingType
from pycatan.player import Player
from pycatan.errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
    NotConnectedError,
    RequiresSettlementError,
)
from .helpers import get_resource_hand, add_free_settlement, add_free_city

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


def test_board_generates_corners_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_corners = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }
    assert set(board.corners.keys()) == expected_corners


def test_board_generates_corners_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_corners = set()
    for hex_coords in SMALL_BOARD_COORDS:
        for offset in Hex.CONNECTED_CORNER_OFFSETS:
            expected_corners.add(hex_coords + offset)

    assert set(board.corners.keys()) == expected_corners


def test_board_propery_keys_corners():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, corner in board.corners.items():
        assert key == corner.coords


def test_board_generates_edges_one_hex():
    board = generate_board_from_hex_coords(ONE_HEX_COORDS)
    expected_edges = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    assert set(board.edges.keys()) == expected_edges


def test_board_generates_edges_many_hexes():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    expected_edges_offsets = set(
        (
            frozenset((Coords(1, 0), Coords(0, 1))),
            frozenset((Coords(0, 1), Coords(-1, 1))),
            frozenset((Coords(-1, 1), Coords(-1, 0))),
            frozenset((Coords(-1, 0), Coords(0, -1))),
            frozenset((Coords(0, -1), Coords(1, -1))),
            frozenset((Coords(1, -1), Coords(1, 0))),
        )
    )
    expected_edges = set()
    for offset in expected_edges_offsets:
        for h in SMALL_BOARD_COORDS:
            expected_edges.add(frozenset([h + o for o in offset]))

    assert set(board.edges.keys()) == expected_edges


def test_board_properly_keys_edges():
    board = generate_board_from_hex_coords(SMALL_BOARD_COORDS)
    for key, edge in board.edges.items():
        assert edge.coords == set(key)


def test_cannot_build_in_middle_of_hex():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(InvalidCoordsError):
        board.add_corner_building(player, Coords(0, 0), BuildingType.SETTLEMENT)


def test_cannot_build_on_top_of_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(CoordsBlockedError):
        board.add_corner_building(
            player, Coords(1, -1), BuildingType.SETTLEMENT, ensure_connected=False
        )
        board.add_corner_building(player, Coords(1, -1), BuildingType.SETTLEMENT)


def test_cannot_build_too_close_to_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(TooCloseToBuildingError):
        board.add_corner_building(
            player, Coords(-2, 2), BuildingType.SETTLEMENT, ensure_connected=False
        )
        board.add_corner_building(player, Coords(-3, 2), BuildingType.SETTLEMENT)


def test_cannot_add_isloated_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(NotConnectedError):
        board.add_corner_building(player, Coords(1, 0), BuildingType.SETTLEMENT)


def test_can_add_settlement():
    board = BeginnerBoard()
    player = Player()
    board.add_corner_building(
        player, Coords(1, 0), BuildingType.SETTLEMENT, ensure_connected=False
    )
    assert board.corners[Coords(1, 0)].building is not None
    assert board.corners[Coords(1, 0)].building.building_type == BuildingType.SETTLEMENT


def test_get_connected_corners():
    board = BeginnerBoard()
    assert board.get_corner_connected_corners(board.corners[Coords(1, -1)]) == {
        board.corners[Coords(2, -2)],
        board.corners[Coords(0, -1)],
        board.corners[Coords(1, 0)],
    }
    assert board.get_corner_connected_corners(board.corners[Coords(-3, 2)]) == {
        board.corners[Coords(-2, 2)],
        board.corners[Coords(-3, 1)],
        board.corners[Coords(-4, 3)],
    }


def test_board_get_yield():
    board = BeginnerBoard()
    player = Player()
    board.add_corner_building(
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
    board.add_corner_building(
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
        board.add_edge_building(
            player=player,
            edge_coords={Coords(1, 0), Coords(1, -1)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_between_unconnected_corners():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(ValueError):
        board.add_edge_building(
            player=player,
            edge_coords={Coords(0, -1), Coords(0, 1)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_to_middle_of_hex():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(ValueError):
        board.add_edge_building(
            player=player,
            edge_coords={Coords(0, -2), Coords(0, 0)},
            building_type=BuildingType.ROAD,
        )


def test_cannot_add_road_on_top_of_other():
    board = BeginnerBoard()
    player = Player()
    edge_coords = {Coords(1, 0), Coords(0, 1)}
    board.add_edge_building(
        player=player,
        edge_coords=edge_coords,
        building_type=BuildingType.ROAD,
        ensure_connected=False,
    )
    with pytest.raises(CoordsBlockedError):
        board.add_edge_building(
            player=player, edge_coords=edge_coords, building_type=BuildingType.ROAD
        )


def test_cannot_add_city_invalid_coords():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(InvalidCoordsError):
        board.add_corner_building(player, Coords(0, 0), building_type=BuildingType.CITY)


def test_cannot_add_city_without_settlement():
    board = BeginnerBoard()
    player = Player()
    with pytest.raises(RequiresSettlementError):
        board.add_corner_building(player, Coords(1, 0), building_type=BuildingType.CITY)


def test_cannot_add_city_on_top_of_other_player_settlement():
    board = BeginnerBoard()
    pOne = Player()
    pTwo = Player()
    board.add_corner_building(
        pOne,
        Coords(1, 0),
        building_type=BuildingType.SETTLEMENT,
        ensure_connected=False,
    )
    with pytest.raises(RequiresSettlementError):
        board.add_corner_building(pTwo, Coords(1, 0), building_type=BuildingType.CITY)


def test_can_add_city():
    b = BeginnerBoard()
    p = Player()
    add_free_city(b, p, Coords(0, -1))
    assert b.corners[Coords(0, -1)].building.building_type == BuildingType.CITY


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
    for edge_coords, harbor in b.harbors.items():
        assert harbor.edge_coords == edge_coords
