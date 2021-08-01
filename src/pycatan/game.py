from typing import Dict, Set
from .player import Player
from .coords import Coords
from .roll_yield import RollYield
from .errors import NotEnoughResourcesError
from .building_type import BuildingType


class Game:
    """A game of Catan. Holds all the game state and game logic
    for interacting with the board, players and decks

    Args:
            board (Board): The board to use in the Catan game
            num_players (int, optional): The number of players to start hte game with. Defaults to 4

    Attributes:
            board (Board): The Catan board being used in this game
            players: List[Player]: The players in the game, ordered by (recommended) turn order
    """

    def __init__(self, board, num_players=4):
        self.board = board
        self.players = [Player() for i in range(num_players)]

    def build_settlement(
        self,
        player: Player,
        coords: Coords,
        check_resources: bool = True,
        check_connection: bool = True,
    ) -> None:
        """Builds a settlement by the player given in the coords given, or raises an error
        Args:
            player (Player): The player who is building the settlement
            coords (Coords): The coordinates to build the settlement at
            check_resources (bool, optional): Whether to remove the resources required to build a settlement from the player's hands, and
                raise an error if they don't have them. Defaults to True
            check_connection (bool, optional): Whether to raise an error if the settlement would not be connected to a road owned by the same
                player. Defaults to True
        Raises:
            NotEnoughResourcesError: If check_resources is True and the player does not have enough resources
            NotConnectedError: If check_connection is True and the settlement would not be connected to any roads owned by the player
        """
        # Check the player has the resources
        if check_resources and not player.has_resources(
            BuildingType.SETTLEMENT.get_required_resources()
        ):
            raise NotEnoughResourcesError(
                "Player does not have enough resources to build a settlement"
            )
        # Build the settlement
        self.board.add_corner_building(
            player, coords, BuildingType.SETTLEMENT, check_connection=check_connection
        )
        # Remove the resources
        if check_resources:
            player.remove_resources(BuildingType.SETTLEMENT.get_required_resources())

    def build_road(
        self,
        player: Player,
        edge_coords: Set[Coords],
        check_resources: bool = True,
        check_connection: bool = True,
    ):
        # Check the player has the resources
        if check_resources and not player.has_resources(
            BuildingType.ROAD.get_required_resources()
        ):
            raise NotEnoughResourcesError(
                "Player doesn not have the resources to build a road"
            )
        self.board.add_edge_building(
            player=player,
            edge_coords=edge_coords,
            building_type=BuildingType.ROAD,
            check_connection=check_connection,
        )
        # Remove the resources
        if check_resources:
            player.remove_resources(BuildingType.ROAD.get_required_resources())

    def add_yield_for_roll(self, roll) -> None:
        """Compute what resources players would receive if `roll` was rolled, and
        then add those resources to the player's hands.
        Equivalent to Game.add_yield(Game.board.get_yield_for_roll(roll))

        Args:
            roll: The number that was rolled
        """
        self.add_yield(self.board.get_yield_for_roll(roll))

    def add_yield(self, roll_yield: Dict[Player, RollYield]) -> None:
        """Add the yield provided to all the player's hands

        Args:
            roll_yield: The yield provided by Board.get_yield_for_roll. A dictionary of RollYields mapped by
                the player who gets that yield
        """
        for p, y in roll_yield.items():
            p.add_resources(y.total_yield)
