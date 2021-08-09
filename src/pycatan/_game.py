from typing import Dict, Set, Optional
from random import shuffle

from ._player import Player
from .board._board import Board
from .board._coords import Coords
from ._roll_yield import RollYield
from .errors import NotEnoughResourcesError
from .board._building_type import BuildingType
from ._development_card import DevelopmentCard


class Game:
    """A game of Catan. Holds all the game state and game logic for interacting with the board, players and decks.

    Args:
            board: The board to use in the Catan game
            num_players: The number of players to start the game with. Defaults to 4

    Attributes:
            board (Board): The Catan board being used in this game
            players (List[Player]): The players in the game, ordered by (recommended) turn order
            longest_road_owner (Player): The player who has the longest road token, or None if no players
                have a road of at least 5 length
            largest_army_owner (Player): The player how has the largest army, or None if no players have played at least 3 knight cards
            development_card_deck (List[DevelopmentCard]): The deck of development cards
    """

    def __init__(self, board: Board, num_players: Optional[int] = 4):
        self.board = board
        self.players = [Player() for i in range(num_players)]
        self.longest_road_owner = None
        self.largest_army_owner = None
        self.development_card_deck = (
            14 * [DevelopmentCard.KNIGHT]
            + 5 * [DevelopmentCard.VICTORY_POINT]
            + 2 * [DevelopmentCard.ROAD_BUILDING]
            + 2 * [DevelopmentCard.YEAR_OF_PLENTY]
            + 2 * [DevelopmentCard.MONOPOLY]
        )

        shuffle(self.development_card_deck)

    def build_settlement(
        self,
        player: Player,
        coords: Coords,
        cost_resources: Optional[bool] = True,
        ensure_connected: Optional[bool] = True,
    ):
        """Build a settlement by the player given in the coords given, or raises an error if the input is invalid.

        Args:
            player: The player who is building the settlement
            coords: The coordinates to build the settlement at
            cost_resources: Whether to remove the resources required to build a settlement from the player's hands, and
                raise an error if they don't have them. Defaults to True
            ensure_connection: Whether to raise an error if the settlement would not be connected to a road owned by the same
                player. Defaults to True
        Raises:
            NotEnoughResourcesError: If check_resources is True and the player does not have enough resources
            NotConnectedError: If check_connection is True and the settlement would not be connected to any roads owned by the player
        """
        # Check the player has the resources
        if cost_resources and not player.has_resources(
            BuildingType.SETTLEMENT.get_required_resources()
        ):
            raise NotEnoughResourcesError(
                "Player does not have enough resources to build a settlement"
            )
        # Build the settlement
        self.board.add_intersection_building(
            player, coords, BuildingType.SETTLEMENT, ensure_connected=ensure_connected
        )
        # Remove the resources
        if cost_resources:
            player.remove_resources(BuildingType.SETTLEMENT.get_required_resources())

    def build_road(
        self,
        player: Player,
        path_coords: Set[Coords],
        cost_resources: Optional[bool] = True,
        ensure_connected: Optional[bool] = True,
    ):
        """Build a road.

        Args:
            player: The player who is building the road
            path_coords: The coordinates of the path to build a road on.
                Should be two valid connected intersection coordinates (i.e. {(1, 0), (1, -1)})
            cost_resources: Whether to remove resources from the player's hand to build the road,
                and raise an error if they don't have enough
            ensure_connected: Whether to ensure that the road is connected to another road, settlement or city
        Raises:
            NotEnoughResourcesError: If check_resources is True and the player doesn't have the cards to build the road
            NotConnectedError: If check_connection is True and the road is not connected to anything
            ValueError: If path_coords is not a set of two valid intersection coordinates
            CoordsBlockedError: If the position is already blocked by another road/other path building
        """
        # Check the player has the resources
        if cost_resources and not player.has_resources(
            BuildingType.ROAD.get_required_resources()
        ):
            raise NotEnoughResourcesError(
                "Player doesn not have the resources to build a road"
            )
        self.board.add_path_building(
            player=player,
            path_coords=path_coords,
            building_type=BuildingType.ROAD,
            ensure_connected=ensure_connected,
        )
        # Remove the resources
        if cost_resources:
            player.remove_resources(BuildingType.ROAD.get_required_resources())

        # Check if the player gets longest road
        road_length = self.board.calculate_player_longest_road(player)
        if road_length >= 5 and (
            self.longest_road_owner is None
            or road_length
            > self.board.calculate_player_longest_road(self.longest_road_owner)
        ):
            self.longest_road_owner = player

    def upgrade_settlement_to_city(
        self, player: Player, coords: Coords, cost_resources: Optional[bool] = True
    ):
        """Build a city from a settlement.

        Args:
            player: The player who is building the city
            coords: Where to build the city
            cost_resources: Whether to remove the resources from the player's hand
        Raises:
            NotEnoughResourcesError: If cost_resources is true and the player doesn't have enough resources
            ValueError: If coords is not a valid intersection
            RequiresSettlementError: If there is not a valid settlement at the intersection to upgrade
        """
        if cost_resources and not player.has_resources(
            BuildingType.CITY.get_required_resources()
        ):
            raise NotEnoughResourcesError(
                "Player does not have the resources to build a city"
            )

        self.board.add_intersection_building(
            player=player, coords=coords, building_type=BuildingType.CITY
        )

        if cost_resources:
            player.remove_resources(BuildingType.CITY.get_required_resources())

    def add_yield_for_roll(self, roll: int):
        """Add the resources to the player's hands for the dice roll given.

        Args:
            roll: The number that was rolled
        """
        self.add_yield(self.board.get_yield_for_roll(roll))

    def add_yield(self, roll_yield: Dict[Player, RollYield]):
        """Add the yield provided to the player's hands.

        Args:
            roll_yield: The yield provided by Board.get_yield_for_roll. A dictionary of RollYields mapped by
                the player who gets that yield
        """
        for p, y in roll_yield.items():
            p.add_resources(y.total_yield)

    def move_robber(self, coords: Coords):
        """Move the robber to the coords specified.

        Args:
            coords: The coordinates of the hex to move the robber to
        Raises:
            ValueError: If the coordinates are not a valid hex
        """
        if not self.board.is_valid_hex_coords(coords):
            raise ValueError("coords is no a valid hex coordinate")

        self.board.robber = coords

    def build_development_card(self, player: Player) -> DevelopmentCard:
        """Build a development card and place it in the player's hand.

        Args:
            player: The player building the development card
        Raises:
            NotEnoughResourcesError: If the player cannot afford to build a development card
        Returns:
            The card that the player built and has been added to their hand
        """
        if not player.has_resources(DevelopmentCard.get_required_resources()):
            raise NotEnoughResourcesError(
                "Player does not have enough resources to build a development card"
            )

        card = self.development_card_deck.pop(0)
        player.development_cards[card] += 1
        player.remove_resources(DevelopmentCard.get_required_resources())
        return card

    def play_development_card(self, player: Player, card: DevelopmentCard):
        """Play a development card.

        Do not actually change the game state to play the card.
        Mainly just keep track of how many knight cards each player has played and may change who has the largest army

        Args:
            player: The player playing a development card
            card: The development card thay are playing
        Raises:
            ValueError: If the player does not have the card
        """
        player.play_development_card(card)
        if card is DevelopmentCard.KNIGHT:
            player.number_played_knights += 1
            if player.number_played_knights >= 3 and (
                self.largest_army_owner is None
                or self.largest_army_owner.number_played_knights
                < player.number_played_knights
            ):
                self.largest_army_owner = player

    def get_victory_points(self, player: Player):
        """Get the number of victory points the player has.

        Args:
            player: The player to get the victory points for
        Returns:
            The number of victory points
        """
        victory_points = sum(
            list(
                map(
                    lambda c: 2 if c.building.building_type is BuildingType.CITY else 1,
                    [
                        c
                        for c in self.board.intersections.values()
                        if c.building is not None and c.building.owner is player
                    ],
                )
            )
        )
        if player is self.longest_road_owner:
            victory_points += 2
        if player is self.largest_army_owner:
            victory_points += 2

        return victory_points + player.development_cards[DevelopmentCard.VICTORY_POINT]
