from enum import Enum
from ._resource import Resource


class DevelopmentCard(Enum):
    """A development card in a game of Catan."""

    KNIGHT = 0
    """The knight card"""
    YEAR_OF_PLENTY = 1
    """The year of plenty card"""
    ROAD_BUILDING = 2
    """The road building card"""
    MONOPOLY = 3
    """The monopoly card"""
    VICTORY_POINT = 4
    """Generic type to represent the victory point cards (i.e. library)"""

    @staticmethod
    def get_required_resources():
        """Get the resources required to build a development card.

        Returns:
            Dict[Resource, int]: How many of each resource is required to build a development card
        """
        return {Resource.WOOL: 1, Resource.GRAIN: 1, Resource.ORE: 1}
