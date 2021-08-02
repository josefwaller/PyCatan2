from typing import Dict
import pytest

from pycatan import Player, Game, RollYield, Resource, DevelopmentCard
from pycatan.errors import NotEnoughResourcesError
from pycatan.board import Coords, BeginnerBoard, BuildingType

from .helpers import get_resource_hand, build_road_along_path


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
        g.players[0], Coords(-2, 0), cost_resources=False, ensure_connected=False
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
        cost_resources=False,
        ensure_connected=False,
    )
    assert g.board.intersections[Coords(-1, 0)].building is not None
    assert g.board.intersections[Coords(-1, 0)].building.owner == g.players[0]
    assert (
        g.board.intersections[Coords(-1, 0)].building.building_type
        == BuildingType.SETTLEMENT
    )


def test_game_build_settlement_no_resources():
    g = Game(BeginnerBoard())
    with pytest.raises(NotEnoughResourcesError):
        g.build_settlement(player=g.players[0], coords=Coords(1, 0))


def test_game_build_settlement_with_resources():
    g = Game(BeginnerBoard())
    g.players[0].add_resources(BuildingType.SETTLEMENT.get_required_resources())
    g.build_settlement(player=g.players[0], coords=Coords(1, 0), ensure_connected=False)
    # Check the player now has 0 resources
    assert (
        len([r for r in g.players[0].resources.keys() if g.players[0].resources[r] > 0])
        == 0
    )


def test_game_build_road_free():
    g = Game(BeginnerBoard())
    g.build_road(
        g.players[0],
        path_coords={Coords(1, -1), Coords(1, 0)},
        cost_resources=False,
        ensure_connected=False,
    )
    assert g.board.paths[frozenset([Coords(1, -1), Coords(1, 0)])].building is not None
    assert (
        g.board.paths[frozenset([Coords(1, -1), Coords(1, 0)])].building.owner
        == g.players[0]
    )
    assert (
        g.board.paths[frozenset([Coords(1, -1), Coords(1, 0)])].building.building_type
        == BuildingType.ROAD
    )


def test_game_build_road_no_resources():
    g = Game(BeginnerBoard())
    with pytest.raises(NotEnoughResourcesError):
        g.build_road(
            g.players[0],
            path_coords={Coords(1, -1), Coords(1, 0)},
            ensure_connected=False,
        )


def test_game_build_some_valid_settlements_and_roads():
    g = Game(BeginnerBoard())
    g.build_settlement(
        player=g.players[0],
        coords=Coords(1, 0),
        cost_resources=False,
        ensure_connected=False,
    )
    g.players[0].add_resources(
        {Resource.LUMBER: 3, Resource.BRICK: 3, Resource.GRAIN: 1, Resource.WOOL: 1}
    )
    g.build_road(player=g.players[0], path_coords={Coords(1, 0), Coords(1, -1)})
    g.build_road(player=g.players[0], path_coords={Coords(1, -1), Coords(0, -1)})
    g.build_settlement(player=g.players[0], coords=Coords(0, -1))


def test_upgrade_city_free():
    g = Game(BeginnerBoard())
    g.build_settlement(
        g.players[0], Coords(1, 0), cost_resources=False, ensure_connected=False
    )
    g.upgrade_settlement_to_city(g.players[0], Coords(1, 0), cost_resources=False)
    assert (
        g.board.intersections[Coords(1, 0)].building.building_type == BuildingType.CITY
    )


def test_update_city_not_enough_resources():
    g = Game(BeginnerBoard())
    g.build_settlement(
        g.players[0], Coords(1, 0), cost_resources=False, ensure_connected=False
    )
    with pytest.raises(NotEnoughResourcesError):
        g.upgrade_settlement_to_city(g.players[0], Coords(1, 0))


def test_update_city_costs_resources():
    g = Game(BeginnerBoard())
    g.build_settlement(
        g.players[0], Coords(1, 0), cost_resources=False, ensure_connected=False
    )
    g.players[0].add_resources(
        {Resource.LUMBER: 2, Resource.BRICK: 2, Resource.ORE: 3, Resource.GRAIN: 3}
    )
    g.upgrade_settlement_to_city(g.players[0], Coords(1, 0))
    assert (
        g.board.intersections[Coords(1, 0)].building.building_type == BuildingType.CITY
    )
    assert g.players[0].resources == get_resource_hand(lumber=2, brick=2, grain=1)


def test_move_robber_valid():
    g = Game(BeginnerBoard())
    g.move_robber(Coords(2, -1))
    assert g.board.robber == Coords(2, -1)


def test_move_robber_invalid_path():
    g = Game(BeginnerBoard())
    with pytest.raises(ValueError):
        g.move_robber(Coords(1, 0))


def test_move_robber_invalid_offboard():
    g = Game(BeginnerBoard())
    with pytest.raises(ValueError):
        g.move_robber(Coords(20, 0))


def test_can_get_longest_road():
    g = Game(BeginnerBoard())
    assert g.longest_road_owner is None
    g.players[0].add_resources(get_resource_hand(lumber=3, brick=3))
    coords = (Coords(1, 0), Coords(0, 1), Coords(0, 2), Coords(-1, 3))
    g.build_road(
        g.players[0], path_coords={coords[0], coords[1]}, ensure_connected=False
    )
    assert g.longest_road_owner is None
    g.build_road(g.players[0], path_coords={coords[1], coords[2]})
    assert g.longest_road_owner is None
    g.build_road(g.players[0], path_coords={coords[2], coords[3]})
    assert g.longest_road_owner is g.players[0]


def test_can_steal_longest_road():
    g = Game(BeginnerBoard())
    paths = (
        (Coords(1, 0), Coords(0, 1), Coords(0, 2), Coords(-1, 3)),
        (Coords(-3, 1), Coords(-3, 2), Coords(-2, 2), Coords(-2, 3)),
        (Coords(-3, 1), Coords(-2, 0)),
    )
    g.players[0].add_resources(get_resource_hand(lumber=3, brick=3))
    g.players[1].add_resources(get_resource_hand(lumber=4, brick=4))
    build_road_along_path(g, g.players[0], paths[0])
    assert g.longest_road_owner is g.players[0]
    # Being tied for longest doesn't take away longest road
    build_road_along_path(g, g.players[1], paths[1])
    assert g.longest_road_owner is g.players[0]
    # But you can steal it
    build_road_along_path(g, g.players[1], paths[2])
    assert g.longest_road_owner is g.players[1]


def test_can_build_dev_card():
    g = Game(BeginnerBoard())
    g.players[0].add_resources(get_resource_hand(wool=1, grain=1, ore=1))
    g.build_development_card(g.players[0])
    assert g.players[0].resources == get_resource_hand()
    assert len([d for d, n in g.players[0].development_cards.items() if n > 0]) == 1


def test_cant_build_dev_card_no_resources():
    g = Game(BeginnerBoard())
    with pytest.raises(NotEnoughResourcesError):
        g.build_development_card(g.players[0])


def test_can_get_largest_army():
    g = Game(BeginnerBoard())
    g.players[0].development_cards[DevelopmentCard.KNIGHT] = 3
    g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is None
    g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is None
    g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[0]


def test_can_steal_largest_army():
    g = Game(BeginnerBoard())
    g.players[0].development_cards[DevelopmentCard.KNIGHT] = 5
    g.players[1].development_cards[DevelopmentCard.KNIGHT] = 4
    for i in range(3):
        g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[0]
    for i in range(3):
        g.play_development_card(g.players[1], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[0]
    g.play_development_card(g.players[1], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[1]
    g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[1]
    g.play_development_card(g.players[0], DevelopmentCard.KNIGHT)
    assert g.largest_army_owner is g.players[0]


def test_get_victory_points_starts_at_zero():
    g = Game(BeginnerBoard())
    for p in g.players:
        assert g.get_victory_points(p) == 0


def test_get_victory_points_gets_settlements():
    g = Game(BeginnerBoard())
    p = g.players[0]
    g.build_settlement(p, Coords(1, 0), ensure_connected=False, cost_resources=False)
    assert g.get_victory_points(p) == 1


def test_get_victory_points_cities():
    g = Game(BeginnerBoard())
    p = g.players[0]
    g.build_settlement(p, Coords(1, 0), ensure_connected=False, cost_resources=False)
    g.upgrade_settlement_to_city(p, Coords(1, 0), cost_resources=False)
    assert g.get_victory_points(p) == 2


def test_get_victory_points_longest_road():
    g = Game(BeginnerBoard())
    p = g.players[0]
    p.add_resources(get_resource_hand(lumber=5, brick=5))
    build_road_along_path(
        g,
        p,
        (
            Coords(1, 0),
            Coords(0, 1),
            Coords(-1, 1),
            Coords(-1, 0),
            Coords(0, -1),
            Coords(1, -1),
        ),
    )
    assert g.get_victory_points(p) == 2


def test_get_victory_points_largest_army():
    g = Game(BeginnerBoard())
    p = g.players[0]
    p.development_cards[DevelopmentCard.KNIGHT] = 5
    for i in range(5):
        g.play_development_card(p, DevelopmentCard.KNIGHT)
    assert g.get_victory_points(p) == 2


def test_get_victory_points_development_cards():
    g = Game(BeginnerBoard())
    p = g.players[0]
    p.development_cards[DevelopmentCard.VICTORY_POINT] = 3
    assert g.get_victory_points(p) == 3


def test_get_victory_points_complicated():
    g = Game(BeginnerBoard())
    g.players[0].add_resources(
        get_resource_hand(lumber=9, brick=9, grain=4, wool=2, ore=3)
    )
    build_road_along_path(
        g,
        g.players[0],
        (
            Coords(1, 0),
            Coords(0, 1),
            Coords(-1, 1),
            Coords(-1, 0),
            Coords(0, -1),
            Coords(1, -1),
            Coords(1, 0),
        ),
    )
    g.build_settlement(g.players[0], Coords(1, 0))
    g.build_settlement(g.players[0], Coords(-1, 0))
    g.upgrade_settlement_to_city(g.players[0], Coords(-1, 0))
    assert g.get_victory_points(g.players[0]) == 5
    g.players[1].development_cards[DevelopmentCard.VICTORY_POINT] = 4
    g.players[1].development_cards[DevelopmentCard.KNIGHT] = 3
    for i in range(3):
        g.play_development_card(g.players[1], DevelopmentCard.KNIGHT)
    g.players[1].add_resources(
        get_resource_hand(lumber=4, brick=4, grain=6, ore=6, wool=2)
    )
    g.build_settlement(g.players[1], Coords(2, -2), ensure_connected=False)
    build_road_along_path(
        g, g.players[1], (Coords(2, -2), Coords(2, -3), Coords(3, -4))
    )
    g.build_settlement(g.players[1], Coords(3, -4))
    g.upgrade_settlement_to_city(g.players[1], Coords(2, -2))
    g.upgrade_settlement_to_city(g.players[1], Coords(3, -4))
    assert g.get_victory_points(g.players[1]) == 10
    g.players[2].add_resources(get_resource_hand(lumber=13, brick=13))
    build_road_along_path(
        g,
        g.players[2],
        (
            Coords(2, 0),
            Coords(2, 1),
            Coords(1, 2),
            Coords(0, 2),
            Coords(-1, 3),
            Coords(-2, 3),
            Coords(-2, 2),
            Coords(-3, 2),
            Coords(-3, 1),
            Coords(-2, 0),
            Coords(-2, -1),
            Coords(-1, -2),
            Coords(0, -2),
            Coords(1, -3),
        ),
    )
    g.players[2].development_cards[DevelopmentCard.KNIGHT] = 5
    for i in range(5):
        g.play_development_card(g.players[2], DevelopmentCard.KNIGHT)
    assert g.get_victory_points(g.players[2]) == 4
    assert g.get_victory_points(g.players[1]) == 8
    assert g.get_victory_points(g.players[0]) == 3
