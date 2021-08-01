from typing import Dict
import pytest

from pycatan.player import Player
from pycatan.coords import Coords
from pycatan.game import Game
from pycatan.roll_yield import RollYield
from pycatan.resource import Resource
from pycatan.board import BeginnerBoard
from pycatan.building_type import BuildingType
from pycatan.errors import NotEnoughResourcesError


def get_roll_yield(lumber=0, brick=0, grain=0, ore=0, wool=0):
    """Gets a test roll yield. Does not set source so don't use in tests that test that"""
    r = RollYield()
    r.add_yield(Resource.LUMBER, lumber, None)
    r.add_yield(Resource.BRICK, brick, None)
    r.add_yield(Resource.GRAIN, grain, None)
    r.add_yield(Resource.WOOL, wool, None)
    r.add_yield(Resource.ORE, ore, None)
    return r


def test_game_defaults_to_four_players():
    g = Game(BeginnerBoard())
    assert len(g.players) == 4


def test_game_allows_variable_players():
    g = Game(BeginnerBoard(), 2)
    assert len(g.players) == 2


def test_game_add_yield_for_roll():
    g = Game(BeginnerBoard())
    g.build_settlement(
        g.players[0], Coords(-2, 0), check_resources=False, check_connection=False
    )
    g.add_yield_for_roll(6)
    assert g.players[0].has_resources({Resource.GRAIN: 1})
    g.add_yield_for_roll(4)
    assert g.players[0].has_resources({Resource.GRAIN: 2})
    g.add_yield_for_roll(3)
    assert g.players[0].has_resources({Resource.GRAIN: 2, Resource.ORE: 1})


def test_game_add_yield():
    g = Game(BeginnerBoard())
    p_zero = g.players[0]
    p_two = g.players[2]
    p_three = g.players[3]
    test_yield: Dict[Player, RollYield] = {
        p_zero: get_roll_yield(lumber=2),
        p_two: get_roll_yield(grain=1, ore=1),
        p_three: get_roll_yield(lumber=3, wool=2, brick=2),
    }
    g.add_yield(test_yield)
    assert g.players[0].has_resources({Resource.LUMBER: 2})
    assert len({v for k, v in g.players[1].resources.items() if v != 0}) == 0
    assert g.players[2].has_resources({Resource.GRAIN: 1, Resource.ORE: 1})
    assert g.players[3].has_resources(
        {Resource.LUMBER: 3, Resource.WOOL: 2, Resource.BRICK: 2}
    )


def test_game_build_settlement_free():
    g = Game(BeginnerBoard())
    g.build_settlement(
        player=g.players[0],
        coords=Coords(-1, 0),
        check_resources=False,
        check_connection=False,
    )
    assert g.board.corners[Coords(-1, 0)].building is not None
    assert g.board.corners[Coords(-1, 0)].building.owner == g.players[0]
    assert (
        g.board.corners[Coords(-1, 0)].building.building_type == BuildingType.SETTLEMENT
    )


def test_game_build_settlement_no_resources():
    g = Game(BeginnerBoard())
    with pytest.raises(NotEnoughResourcesError):
        g.build_settlement(player=g.players[0], coords=Coords(1, 0))


def test_game_build_settlement_with_resources():
    g = Game(BeginnerBoard())
    g.players[0].add_resources(BuildingType.SETTLEMENT.get_required_resources())
    g.build_settlement(player=g.players[0], coords=Coords(1, 0), check_connection=False)
    # Check the player now has 0 resources
    assert (
        len([r for r in g.players[0].resources.keys() if g.players[0].resources[r] > 0])
        == 0
    )


def test_game_build_road_free():
    g = Game(BeginnerBoard())
    g.build_road(
        g.players[0],
        edge_coords={Coords(1, -1), Coords(1, 0)},
        check_resources=False,
        check_connection=False,
    )
    assert g.board.edges[frozenset([Coords(1, -1), Coords(1, 0)])].building is not None
    assert (
        g.board.edges[frozenset([Coords(1, -1), Coords(1, 0)])].building.owner
        == g.players[0]
    )
    assert (
        g.board.edges[frozenset([Coords(1, -1), Coords(1, 0)])].building.building_type
        == BuildingType.ROAD
    )


def test_game_build_road_no_resources():
    g = Game(BeginnerBoard())
    with pytest.raises(NotEnoughResourcesError):
        g.build_road(
            g.players[0],
            edge_coords={Coords(1, -1), Coords(1, 0)},
            check_connection=False,
        )


def test_game_build_some_valid_settlements_and_roads():
    g = Game(BeginnerBoard())
    g.build_settlement(
        player=g.players[0],
        coords=Coords(1, 0),
        check_resources=False,
        check_connection=False,
    )
    g.players[0].add_resources(
        {Resource.LUMBER: 3, Resource.BRICK: 3, Resource.GRAIN: 1, Resource.WOOL: 1}
    )
    g.build_road(player=g.players[0], edge_coords={Coords(1, 0), Coords(1, -1)})
    g.build_road(player=g.players[0], edge_coords={Coords(1, -1), Coords(0, -1)})
    g.build_settlement(player=g.players[0], coords=Coords(0, -1))
