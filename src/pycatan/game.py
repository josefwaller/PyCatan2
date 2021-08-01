from typing import Dict
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

    def build_settlement(self, player: Player, coords: Coords) -> None:
        if not player.has_resources(BuildingType.SETTLEMENT.get_required_resources()):
            raise NotEnoughResourcesError(
                "Player does not have enough resources to build a settlement"
            )
        else:
            self.board.add_corner_building(player, coords, BuildingType.SETTLEMENT)

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
