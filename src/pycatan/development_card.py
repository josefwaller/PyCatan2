from enum import Enum
from .resource import Resource


class DevelopmentCard(Enum):
    KNIGHT = 0
    YEAR_OF_PLENTY = 1
    ROAD_BUILDING = 2
    MONOPOLY = 3
    VICTORY_POINT = 4

    @staticmethod
    def get_required_resources():
        return {Resource.WOOL: 1, Resource.GRAIN: 1, Resource.ORE: 1}
