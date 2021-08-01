from enum import Enum
from .resource import Resource


class BuildingType(Enum):
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2

    def get_required_resources(self):
        if self == BuildingType.ROAD:
            return {Resource.BRICK: 1, Resource.LUMBER: 1}
        elif self == BuildingType.SETTLEMENT:
            return {
                Resource.BRICK: 1,
                Resource.LUMBER: 1,
                Resource.WOOL: 1,
                Resource.GRAIN: 1,
            }
        elif self == BuildingType.CITY:
            return {Resource.ORE: 3, Resource.GRAIN: 2}
