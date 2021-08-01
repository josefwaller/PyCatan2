from pycatan.resource import Resource
from pycatan.board import Board
from pycatan.player import Player
from pycatan.coords import Coords
from pycatan.building_type import BuildingType


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
