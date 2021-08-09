# pycatan

[![PyPi](https://img.shields.io/pypi/v/pycatan.svg)](https://pypi.org/project/pycatan/#description)
[![Read The Docs](https://readthedocs.org/projects/pycatan/badge)](https://pycatan.readthedocs.io/en/latest/index.html)
[![Tests](https://github.com/josefwaller/PyCatan2/actions/workflows/tests.yaml/badge.svg)](https://github.com/josefwaller/PyCatan2/actions/workflows/tests.yaml)

A python module for running games of The Settlers of Catan.

```
from pycatan import Game
from pycatan.board import RandomBoard

import random

game = Game(RandomBoard())

pOne = game.players[0]
settlement_coords = game.board.get_valid_settlement_coords(player = pOne, ensure_connected = False)
game.build_settlement(player = pOne, coords = random.choice(list(settlement_coords)), cost_resources = False, ensure_connected = False)
print(game.board)
```

produces:
```


                 3:1         2:1
                  .--'--.--'--.--'--.
                  |  5  |  2  |  6  | 2:1
               .--'--.--'--.--'--.--'--.
           2:1 | 10  |  9  |  4  |  3  |
            .--'--.--'--.--'--.--'--.--'--.
            |  8  | 11  |   R |  5  |  8  | 3:1
            '--.--'--.--s--.--'--.--'--.--'
           3:1 |  4  |  3  |  6  | 10  |
               '--.--'--.--'--.--'--.--'
                  | 11  | 12  |  9  | 3:1
                  '--.--'--.--'--.--'
                 2:1         2:1
```

**pycatan does**

* Game state (who has what resources and what buildings on what tiles)
* Gives out resources for a given roll
* Prints the board (it looks better with colour)
* Determine all the valid places to build a settlement/city/road
* Determine all the valid trades a player can do (4:1 and 2:1 with harbor)

**pycatan does not**
* Track turn order
* Handle playing development cards (though it gives you utility functions that help a lot - see the [text game tutorial on read the docs](https://pycatan.readthedocs.io/en/latest/tutorial.html#part-5-development-cards))
* Handle trades between players

PyCatan is built to be expandable. It provides all the game logic but doesn't force you to play the exact game.
It would be easy to add expansions such as a `Settlement Builder` development card or a board that is 3 tiles high and 30 tiles long.
