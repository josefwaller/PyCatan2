from typing import Set

from pycatan import Game, Resource, Player
from pycatan.board import Board, Coords, BuildingType, Harbor


def get_resource_hand(lumber=0, wool=0, brick=0, ore=0, grain=0):
    return {
        Resource.LUMBER: lumber,
        Resource.WOOL: wool,
        Resource.BRICK: brick,
        Resource.ORE: ore,
        Resource.GRAIN: grain,
    }


def add_free_settlement(b: Board, p: Player, c: Coords):
    b.add_intersection_building(
        p, c, building_type=BuildingType.SETTLEMENT, ensure_connected=False
    )


def add_free_city(b: Board, p: Player, c: Coords):
    add_free_settlement(b, p, c)
    b.add_intersection_building(p, c, building_type=BuildingType.CITY)


def add_free_road(b: Board, p: Player, path_coords: Coords):
    b.add_path_building(
        p,
        path_coords=path_coords,
        building_type=BuildingType.ROAD,
        ensure_connected=False,
    )


def assert_trades_equal(trade_one, trade_two):
    assert len([x for x in trade_one if x not in trade_two]) == 0
    assert len([x for x in trade_two if x not in trade_one]) == 0


def get_harbor(
    path_coords: Coords = {Coords(3, 2), Coords(2, 3)}, resource: Resource = None
):
    return Harbor(path_coords, resource)


def get_trades(resource, trade_amount):
    return [{resource: -trade_amount, res: 1} for res in Resource if res != resource]


def build_road_along_path(g: Game, p: Player, path: Set[Coords]):
    """This method charges the player for all the roads"""
    for i in range(len(path) - 1):
        g.build_road(p, path_coords={path[i], path[i + 1]}, ensure_connected=i != 0)


def add_free_road_from_path(b: Board, p: Player, path: Set[Coords]):
    for i in range(len(path) - 1):
        add_free_road(b, p, {path[i], path[i + 1]})
