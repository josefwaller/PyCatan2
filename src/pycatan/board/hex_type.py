from enum import Enum

from ..resource import Resource


class HexType(Enum):
    FOREST = 0
    HILLS = 1
    PASTURE = 2
    FIELDS = 3
    MOUNTAINS = 4
    DESERT = 5

    def get_resource(self) -> Resource:
        if self == HexType.FOREST:
            return Resource.LUMBER
        elif self == HexType.HILLS:
            return Resource.BRICK
        elif self == HexType.PASTURE:
            return Resource.WOOL
        elif self == HexType.FIELDS:
            return Resource.GRAIN
        elif self == HexType.MOUNTAINS:
            return Resource.ORE
        elif self == HexType.DESERT:
            return None
