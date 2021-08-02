from enum import Enum

from .._resource import Resource


class HexType(Enum):
    """The different types of hexes in the game."""

    FOREST = 0
    HILLS = 1
    PASTURE = 2
    FIELDS = 3
    MOUNTAINS = 4
    DESERT = 5

    def get_resource(self) -> Resource:
        """Get the resource the player receives when a hex of this type is activated.

        Returns:
            Resource: The resource the player would get
            None: If the player would not get a resource (i.e. a desert hex)
        """
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
