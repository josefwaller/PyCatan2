from typing import Set, Optional

from ._coords import Coords
from ._building import IntersectionBuilding


class Intersection:
    """A intersection on the Catan board.

    Args:
        coords:
                The coordinates of the intersection.
        building:
                The building on the intersection.

    Attributes:
            CONNECTED_CORNER_OFFSETS (Set[Coords]):
                    The offsets of the intersections that are connected by an path.
                    i.e. to get the connected intersections, add a intersection's coords to these values,
                    and then filter for which coords are valid intersection coords.
            coords (Coords):
                    The coordinates of the intersection.
            building (IntersectionBuilding, optional):
                    The building on the intersection.
    """

    CONNECTED_CORNER_OFFSETS: Set[Coords] = {
        Coords(1, 0),
        Coords(0, 1),
        Coords(-1, 1),
        Coords(-1, 0),
        Coords(0, -1),
        Coords(1, -1),
    }

    def __init__(self, coords: Coords, building: Optional[IntersectionBuilding] = None):
        self.coords = coords
        self.building = building
