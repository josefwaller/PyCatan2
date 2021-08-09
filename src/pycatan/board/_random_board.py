import random

from ._hex_type import HexType
from ._hex import Hex
from ._harbor import Harbor
from ._coords import Coords
from ._board import Board
from .._resource import Resource


class RandomBoard(Board):
    """A board where the hexes, numbered tokens and harbors are all shuffled randomly."""

    def __init__(self):
        hex_deck = (
            [HexType.FOREST] * 4
            + [HexType.PASTURE] * 4
            + [HexType.FIELDS] * 4
            + [HexType.HILLS] * 3
            + [HexType.MOUNTAINS] * 3
            + [HexType.DESERT]
        )
        token_deck = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
        random.shuffle(hex_deck)
        hex_coords = [
            Coords(4, -2),
            Coords(3, 0),
            Coords(2, 2),
            Coords(0, 3),
            Coords(-2, 4),
            Coords(-3, 3),
            Coords(-4, 2),
            Coords(-3, 0),
            Coords(-2, -2),
            Coords(0, -3),
            Coords(2, -4),
            Coords(3, -3),
            Coords(2, -1),
            Coords(1, 1),
            Coords(-1, 2),
            Coords(-2, 1),
            Coords(-1, -1),
            Coords(1, -2),
            Coords(0, 0),
        ]
        hexes = set()
        for h in hex_coords:
            hex_type = hex_deck.pop()
            hexes.add(
                Hex(
                    hex_type=hex_type,
                    token_number=None
                    if hex_type is HexType.DESERT
                    else token_deck.pop(0),
                    coords=h,
                )
            )
        harbor_deck = [
            Resource.BRICK,
            Resource.LUMBER,
            Resource.ORE,
            Resource.WOOL,
            Resource.GRAIN,
        ] + 4 * [None]
        random.shuffle(harbor_deck)
        harbor_coords = {
            frozenset({Coords(5, -2), Coords(5, -3)}),
            frozenset({Coords(4, 0), Coords(3, 1)}),
            frozenset({Coords(1, 3), Coords(0, 4)}),
            frozenset({Coords(-2, 5), Coords(-3, 5)}),
            frozenset({Coords(-4, 3), Coords(-4, 4)}),
            frozenset({Coords(-4, 0), Coords(-4, 1)}),
            frozenset({Coords(-3, -2), Coords(-2, -3)}),
            frozenset({Coords(1, -4), Coords(0, -4)}),
            frozenset({Coords(3, -4), Coords(4, -4)}),
        }
        harbors = set()
        for h in harbor_coords:
            harbors.add(Harbor(path_coords=h, resource=harbor_deck.pop()))
        super().__init__(hexes=hexes, harbors=harbors)


if __name__ == "__main__":
    b = RandomBoard()
    print(b)
