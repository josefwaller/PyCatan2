******************
Text game Tutorial
******************

In this tutorial, we're going to use pycatan to make a version of the game playable in the terminal.

Initializing the Game
---------------------

Our game is just going to use the beginner board, which is already provided. ::

    from pycatan import Game
    from pycatan.board import BeginnerBoard

    game = Game(BeginnerBoard())

Done! Now we have a 4 player game of catan all set up. We can show the board by simply printing it. ::

    print(game.board)

The Building Phase
------------------

First let's set up the turn order: ::

    # Building phase
    for i in range(len(game.players)) + reversed(range(len(game.players))):
        print("Player %d, choose a hex to build your settlement on" % (i + 1))
