from typing import Dict
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
    def get_required_resources() -> Dict[Resource, int]:
        """Get the resources required to build a development card.

        Returns:
            How many of each resource is required to build a development card
        """
        return {Resource.WOOL: 1, Resource.GRAIN: 1, Resource.ORE: 1}

    def __str__(self):
        return {
            DevelopmentCard.KNIGHT: "Knight",
            DevelopmentCard.YEAR_OF_PLENTY: "Year of Plenty",
            DevelopmentCard.ROAD_BUILDING: "Road Building",
            DevelopmentCard.VICTORY_POINT: "Victory Point",
            DevelopmentCard.MONOPOLY: "Monopoly",
        }[self]

    def __repl__(self):
        return self.__str__()
