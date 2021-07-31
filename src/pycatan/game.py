from .player import Player


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
