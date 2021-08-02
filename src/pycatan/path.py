from .coords import Coords


class Path:
    """An path on a Catan board

    Args:
            path_coords (set(Coords, Coords)): The coordinates of the two intersections
                that the path connects
            building (PathBuilding, optiona): The building on this path

    Attributes:
            path_coords (set(Coords, Coords)): The coordinates of the two intersections
                that the path connects
            building (PathBuilding, optional): The building on this path
    """

    def __init__(self, path_coords, building=None):
        self.path_coords = path_coords
        self.building = building

    def other_intersection(self, coords: Coords):
        """Given one of the intersection coords for this path, returns the other one"""
        return [c for c in self.path_coords if c != coords][0]
