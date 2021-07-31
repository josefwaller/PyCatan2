from typing import Dict

from .resource import Resource


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
            # TBA
            pass
        for res, num in resources.items():
            self.resources[res] -= num

    def add_resources(self, resources: Dict[Resource, int]) -> None:
        """Add some resources to this player's hand

        Args:
                resources (Dict[Resource, int]): The resources to add
        """
        for res, num in resources.items():
            self.resources[res] += num
