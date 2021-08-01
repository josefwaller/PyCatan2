from typing import Dict, List

from .resource import Resource
from .errors import NotEnoughResourcesError


class Player:
    """A Player in a Catan game

    Attributes:
            resources (Dict[Resource, int]): How many of each resource this player has
            development_cards (Dict[DevelopmentCard, int]): How many of each development card this player has
    """

    def __init__(self):
        self.resources: Dict[Resource, int] = {res: 0 for res in Resource}
        self.development_cards = {}

    def has_resources(self, resources: Dict[Resource, int]) -> bool:
        """Check if the player has the resources given

        Args:
                resources (Dict[Resource, int]): The resources to check that the player has

        Returns:
                bool: True if the player has the resources, false otherwise
        """
        for res, num in resources.items():
            if self.resources[res] < num:
                return False
        return True

    def remove_resources(self, resources: Dict[Resource, int]) -> None:
        """Remove the given resources from the player's hand

        Args:
                resources (Dict[Resource, int]): The resources to remove

        Raises:
                NotEnoughResourcesError: If the player does not have the resources
        """
        if not self.has_resources(resources):
            raise NotEnoughResourcesError(
                "The player does not have the resources to remove"
            )

        for res, num in resources.items():
            self.resources[res] -= num

    def add_resources(self, resources: Dict[Resource, int]) -> None:
        """Add some resources to this player's hand

        Args:
                resources (Dict[Resource, int]): The resources to add
        """
        for res, num in resources.items():
            self.resources[res] += num

    def get_possible_trades(self) -> List[Dict[Resource, int]]:
        """Get a list of the possible trades for this player
        Returns: A set of the possible trades for this player, where negative numbers mean the player would
            give away those resources and positive numbers mean the player would receive those resources
        """
        trades = []
        for res in Resource:
            if self.has_resources({res: 4}):
                # Add the 4-1 trades
                for r in Resource:
                    if r != res:
                        trades.append({res: -4, r: 1})
        return trades
