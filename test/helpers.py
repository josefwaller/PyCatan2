from pycatan.resource import Resource
from pycatan.board import Board
from pycatan.player import Player
from pycatan.coords import Coords
from pycatan.building_type import BuildingType
from pycatan.harbor import Harbor


def get_resource_hand(lumber=0, wool=0, brick=0, ore=0, grain=0):
    return {
        Resource.LUMBER: lumber,
        Resource.WOOL: wool,
        Resource.BRICK: brick,
        Resource.ORE: ore,
        Resource.GRAIN: grain,
    }


def add_free_settlement(b: Board, p: Player, c: Coords):
    b.add_corner_building(
        p, c, building_type=BuildingType.SETTLEMENT, ensure_connected=False
    )


def add_free_city(b: Board, p: Player, c: Coords):
    add_free_settlement(b, p, c)
    b.add_corner_building(p, c, building_type=BuildingType.CITY)


def assert_trades_equal(trade_one, trade_two):
    assert len([x for x in trade_one if x not in trade_two]) == 0
    assert len([x for x in trade_two if x not in trade_one]) == 0


def get_harbor(
    edge_coords: Coords = {Coords(3, 2), Coords(2, 3)}, resource: Resource = None
):
    return Harbor(edge_coords, resource)


def get_trades(resource, trade_amount):
    return [{resource: -trade_amount, res: 1} for res in Resource if res != resource]
