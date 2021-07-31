from typing import Set

from .coords import Coords


class Hex:
    """A hex on a Catan board

    Args:
        coords Coords: The coordinates of this hex

    Attributes:
        CONNECTED_POINTS_OFFSETS set[Coords]:
                The offsets of the connected points from a hex's coordinates
        coords Coords: The coordinates of this hex
    """

    CONNECTED_CORNER_OFFSETS: Set[Coords] = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }

    def __init__(self, coords):
        self.coords = coords
