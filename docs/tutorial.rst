******************
Text game Tutorial
******************

In this tutorial, we're going to use pycatan to make a version of the game playable in the terminal.
The finished text game is available here: https://gist.github.com/josefwaller/a3c3c19b19e46150224e7a4f34bc4dbd

Initializing the Game
---------------------

Our game is just going to use the beginner board, which is already provided. ::

    from pycatan import Game
    from pycatan.board import BeginnerBoard

    game = Game(BeginnerBoard())

Done! Now we have a 4 player game of catan all set up. We can show the board by simply printing it. ::

    print(game.board)

Part 1: The Building Phase
--------------------------

.. include:: ./tutorial-pt-1-building-phase.rst


Part 2: The game loop
---------------------

.. include:: ./tutorial-pt-2-game-loop.rst

Part 3: Building new buildings
------------------------------

.. include:: ./tutorial-pt-3-building.rst

Part 4: Trading in resources
----------------------------

.. include:: ./tutorial-pt-4-trading.rst

Part 5: Development Cards
-------------------------

.. include:: ./tutorial-pt-5-development-cards.rst

Part 6: Moving the Robber
-------------------------

.. include:: ./tutorial-pt-6-move-the-robber.rst

Part 7: Victory Points
----------------------

.. include:: ./tutorial-pt-7-victory-points.rst
