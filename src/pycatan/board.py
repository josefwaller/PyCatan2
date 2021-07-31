from typing import Dict

from .coords import Coords
from .hex import Hex


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
