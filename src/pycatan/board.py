from typing import Dict
from itertools import product

from .coords import Coords
from .hex import Hex
from .corner import Corner
from .edge import Edge


class Board:
    """An interface for holding the state of Catan boards.
    Uses a triangular grid to hold the tiles, corners and
    edges. The Board constructor will automatically
    generate the corners and edges from a dict of hexes,
    assuming all the hexes tile correctly

    Args:
                    hexes (dict[Coords, Hex]):
                                    The hexes on the board, keyed by their coordinates
                    harbors (dict[set[Coord, Coord], Harbor]):
                                    The harbors on the board, keyed by the two corners they are attached to

    Attributes:
                    hexes dict[Coord, Hex]:
                                    The hexes on this catan board, keyed by their coordinates
                    corners: (dict[Coords, Corner]):
                                    The corners on the board, keyed by their coordinates
                    edges: (dict[frozenset[Coords, Coords], Edge]):
                                    The edges on the board, keyed by the coordinates of the two corners they connect
                    harbors (dict[set[Coord, Coord], Harbor]):
                                    The harbors on the board, keyed by the two corners they are attached to
    """

    def __init__(self, hexes: Dict[Coords, Hex], harbors={}):
        self.hexes = hexes
        self.harbors = harbors
        # Gather the points around each hex into a set
        corner_coords = set(
            map(
                lambda x: x[0] + x[1],
                list(product(*[hexes.keys(), Hex.CONNECTED_CORNER_OFFSETS])),
            )
        )
        # Add the corners to self.corners
        self.corners = {}
        for coords in corner_coords:
            self.corners[coords] = Corner(coords)
        # Now add all the edgges inbetween the corners we just added
        self.edges = {}
        for c in self.corners:
            for offset in Corner.CONNECTED_CORNER_OFFSETS:
                coord = c + offset
                if coord in self.corners:
                    self.edges[frozenset([c, c + offset])] = Edge(set([c, c + offset]))
