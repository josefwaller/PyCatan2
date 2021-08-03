pycatan
=======

.. toctree::
    :hidden:
    :maxdepth: 1

    tutorial
    reference

A python module for simmulating games of The Settlers of Catan::

    >>> from pycatan import Game
    >>> from pycatan.board import BeginnerBoard
    >>> game = Game(BeginnerBoard())
    >>> print(game.board)


                     3:1         2:1
                      .--'--.--'--.--'--.
                      | 10  |  2  |  9  | 2:1
                   .--'--.--'--.--'--.--'--.
               2:1 | 12  |  6  |  4  | 10  |
                .--'--.--'--.--'--.--'--.--'--.
                |  9  | 11  |   R |  3  |  8  | 3:1
                '--.--'--.--'--.--'--.--'--.--'
               2:1 |  8  |  3  |  4  |  5  |
                   '--.--'--.--'--.--'--.--'
                      |  5  |  6  | 11  | 2:1
                      '--.--'--.--'--.--'
                     3:1         3:1

    >>>
