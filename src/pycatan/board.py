from typing import Dict, Set
from itertools import product

from .coords import Coords
from .hex import Hex
from .hex_type import HexType
from .corner import Corner
from .edge import Edge
from .player import Player
from .building import CornerBuilding
from .building_type import BuildingType


class Board:
    """An interface for holding the state of Catan boards.
    Uses a triangular grid to hold the tiles, corners and
    edges. The Board constructor will automatically
    generate the corners and edges from a dict of hexes,
    assuming all the hexes tile correctly

    Args:
            hexes (Set[Hex]):
                    The hexes on the board, keyed by their coordinates
            harbors (Dict[set[Coord, Coord], Harbor]):
                    The harbors on the board, keyed by the two corners they are attached to

    Attributes:
            hexes (Dict[Coord, Hex]):
                    The hexes on this catan board, keyed by their coordinates
            corners: (Dict[Coords, Corner]):
                    The corners on the board, keyed by their coordinates
            edges: (Dict[frozenset[Coords, Coords], Edge]):
                    The edges on the board, keyed by the coordinates of the two corners they connect
            harbors (Dict[Set[Coord, Coord], Harbor]):
                    The harbors on the board, keyed by the two corners they are attached to
    """

    def __init__(self, hexes: Set[Hex], harbors={}):
        self.hexes: Dict[Coords, Hex] = dict(zip((h.coords for h in hexes), hexes))
        self.harbors = harbors
        # Gather the points around each hex into a set
        corner_coords = set(
            map(
                lambda x: x[0] + x[1],
                list(product(*[self.hexes.keys(), Hex.CONNECTED_CORNER_OFFSETS])),
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

    def add_settlement(self, owner: Player, coords: Coords):
        """Add a settlement to the board

        Args:
                player (Player): The player who owns the settlement
                coords (Coords): The coords to put the building

        Raises:
                InvalidCoordsError: If `coords` is not a valid corner
                TooCloseToBuildingError: If the building is too close to another
                PositionAlreadyTakenError: If the position is already taken
        """
        self.corners[coords].building = CornerBuilding(
            owner, BuildingType.SETTLEMENT, coords
        )


class BeginnerBoard(Board):
    """The beginner board, as outlined in the Catan rules"""

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
            }
        )
