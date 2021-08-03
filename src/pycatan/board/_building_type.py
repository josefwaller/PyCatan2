from enum import Enum
from .._resource import Resource


class BuildingType(Enum):
    """A type of building in a Catan game."""

    ROAD = 0
    """The roads"""
    SETTLEMENT = 1
    """The settlements"""
    CITY = 2
    """The cities"""

    def get_required_resources(self):
        """Get the resources required to build this building.

        Returns:
            Dict[Resource, int]: The amount of each resource required to build this building
        """
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
