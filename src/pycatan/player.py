from typing import Dict, List

from .resource import Resource
from .errors import NotEnoughResourcesError
from .development_card import DevelopmentCard


class Player:
    """A Player in a Catan game

    Attributes:
            resources (Dict[Resource, int]): How many of each resource this player has
            development_cards (Dict[DevelopmentCard, int]): How many of each development card this player has
            connected_harbors (Set[Harbor]): The harbors this player is connected to. Used to determin the valid trades
    """

    def __init__(self):
        self.resources: Dict[Resource, int] = {res: 0 for res in Resource}
        self.development_cards = {d: 0 for d in DevelopmentCard}
        self.connected_harbors = set()

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
        # Use this map to avoid including a worse deal
        has_two_to_one = {res: False for res in Resource}
        # Add 2:1 harbor trades
        for harbor in self.connected_harbors:
            # Generic harbors willbe handled with the 4:1 trades
            if harbor.resource is None:
                continue
            has_two_to_one[harbor.resource] = True
            if self.has_resources({harbor.resource: 2}):
                for r in Resource:
                    if r != harbor.resource:
                        trades.append({harbor.resource: -2, r: 1})

        # Add 3:1 and 4:1 trades
        has_generic_harbor = (
            len([h for h in self.connected_harbors if h.resource is None]) != 0
        )
        for res in Resource:
            if has_two_to_one[res]:
                continue
            amount = 3 if has_generic_harbor else 4
            if self.has_resources({res: amount}):
                # Add the 4-1 trades
                for r in Resource:
                    if r != res:
                        trades.append({res: -amount, r: 1})
        # Filter out duplicates
        return [dict(t) for t in {tuple(d.items()) for d in trades}]
