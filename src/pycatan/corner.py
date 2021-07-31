from typing import Set

from .coords import Coords


class Corner:
    """A corner on the Catan board

    Args:
        coords (Coords):
                The coordinates of the corner
        building (CornerBuilding, optional):
                The building on the corner

    Attributes:
            CONNECTED_CORNER_OFFSETS (Set[Coords]):
                    The offsets of the corners that are connected by an edge
                    i.e. to get the connected corners, add a corner's coords to these values,
                    and then filter for which coords are valid corner coords
            coords (Coords):
                    The coordinates of the corner
            building (CornerBuilding, optional):
                    The building on the corner
    """

    CONNECTED_CORNER_OFFSETS: Set[Coords] = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }

    def __init__(self, coords, building=None):
        self.coords = coords
        self.building = building
