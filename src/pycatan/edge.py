from .coords import Coords


class Edge:
    """An edge on a Catan board

    Args:
            edge_coords (set(Coords, Coords)): The coordinates of the two corners
                that the edge connects
            building (EdgeBuilding, optiona): The building on this edge

    Attributes:
            edge_coords (set(Coords, Coords)): The coordinates of the two corners
                that the edge connects
            building (EdgeBuilding, optional): The building on this edge
    """

    def __init__(self, edge_coords, building=None):
        self.edge_coords = edge_coords
        self.building = building

    def other_corner(self, coords: Coords):
        """Given one of the corner coords for this edge, returns the other one"""
        return [c for c in self.edge_coords if c != coords][0]
