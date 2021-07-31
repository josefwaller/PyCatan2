from pycatan.game import Game
from pycatan.board import BeginnerBoard


def test_game_defaults_to_four_players():
    g = Game(BeginnerBoard())
    assert len(g.players) == 4


def test_game_allows_variable_players():
    g = Game(BeginnerBoard(), 2)
    assert len(g.players) == 2
