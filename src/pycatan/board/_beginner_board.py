from ._board import Board
from ._hex import Hex
from ._coords import Coords
from ._hex_type import HexType
from ._harbor import Harbor
from .._resource import Resource


class BeginnerBoard(Board):
    """The beginner board, as outlined in the Catan rules."""

    def __init__(self):
        super().__init__(
            hexes={
                Hex(Coords(4, -2), HexType.MOUNTAINS, 10),
                Hex(Coords(3, 0), HexType.PASTURE, 2),
                Hex(Coords(2, 2), HexType.FOREST, 9),
                Hex(Coords(3, -3), HexType.FIELDS, 12),
                Hex(Coords(2, -1), HexType.HILLS, 6),
                Hex(Coords(1, 1), HexType.PASTURE, 4),
                Hex(Coords(0, 3), HexType.HILLS, 10),
                Hex(Coords(2, -4), HexType.FIELDS, 9),
                Hex(Coords(1, -2), HexType.FOREST, 11),
                Hex(Coords(0, 0), HexType.DESERT),
                Hex(Coords(-1, 2), HexType.FOREST, 3),
                Hex(Coords(-2, 4), HexType.MOUNTAINS, 8),
                Hex(Coords(0, -3), HexType.FOREST, 8),
                Hex(Coords(-1, -1), HexType.MOUNTAINS, 3),
                Hex(Coords(-2, 1), HexType.FIELDS, 4),
                Hex(Coords(-3, 3), HexType.PASTURE, 5),
                Hex(Coords(-2, -2), HexType.HILLS, 5),
                Hex(Coords(-3, 0), HexType.FIELDS, 6),
                Hex(Coords(-4, 2), HexType.PASTURE, 11),
            },
            harbors=[
                Harbor(
                    path_coords={Coords(4, 0), Coords(3, 1)}, resource=Resource.GRAIN
                ),
                Harbor(path_coords={Coords(1, 3), Coords(0, 4)}, resource=Resource.ORE),
                Harbor(path_coords={Coords(-2, 5), Coords(-3, 5)}, resource=None),
                Harbor(
                    path_coords={Coords(-4, 3), Coords(-4, 4)}, resource=Resource.WOOL
                ),
                Harbor(path_coords={Coords(-4, 0), Coords(-4, 1)}, resource=None),
                Harbor(path_coords={Coords(-2, -3), Coords(-3, -2)}, resource=None),
                Harbor(
                    path_coords={Coords(2, -5), Coords(1, -4)}, resource=Resource.BRICK
                ),
                Harbor(
                    path_coords={Coords(3, -4), Coords(4, -4)}, resource=Resource.LUMBER
                ),
                Harbor(path_coords={Coords(5, -3), Coords(5, -2)}, resource=None),
            ],
        )
