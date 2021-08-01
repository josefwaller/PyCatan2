from typing import Set

from .coords import Coords
from .resource import Resource


class Harbor:
    """A harbor on the catan board
    Attributes:
        edge_coords (Set[Coords]): The coordinates of the edge that the harbor is attached to
        resource (Resource): The resource that the player can trade in 2-1
    Args:
        edge_coords (Set[Coords]): The coordinates of the edge that the harbor is attached to
        resource (Resource): The resource that the player can trade in 2-1
    """

    def __init__(self, edge_coords: Set[Coords], resource: Resource):
        self.edge_coords = edge_coords
        self.resource = resource
