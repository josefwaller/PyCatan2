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
from .errors import InvalidCoordsError, TooCloseToBuildingError, CoordsBlockedError
from .roll_yield import RollYield, RollYieldSource


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
        """Add a settlement to the board. Does not check if the player has enough cards.

        Args:
                        player (Player): The player who owns the settlement
                        coords (Coords): The coords to put the building

        Raises:
                        InvalidCoordsError: If `coords` is not a valid corner
                        TooCloseToBuildingError: If the building is too close to another
                        PositionAlreadyTakenError: If the position is already taken
        """
        if coords not in self.corners.keys():
            raise InvalidCoordsError("coords must be the coordinates of a corner")

        elif self.corners[coords].building is not None:
            print(self.corners[coords].building)
            raise CoordsBlockedError("There is already a building on this corner")

        elif (
            len(
                set(
                    filter(
                        lambda c: c.building is not None,
                        self.get_corner_connected_corners(self.corners[coords]),
                    )
                )
            )
            > 0
        ):
            raise TooCloseToBuildingError(
                "There is a building that is not at least 2 edges away from this position"
            )

        else:
            self.corners[coords].building = CornerBuilding(
                owner, BuildingType.SETTLEMENT, coords
            )

    def get_corner_connected_corners(self, corner) -> Set[Corner]:
        """Get the corners connected to the corner given by an edge

        Args:
                        corner (Corner): The corner to get the connected corners for

        Returns:
                        Set[Corner]: The corners that are connected to the corner given
        """
        connected = set()
        for c in Corner.CONNECTED_CORNER_OFFSETS:
            if c + corner.coords in self.corners.keys():
                connected.add(self.corners[c + corner.coords])
        return connected

    def get_connected_hex_corners(self, hex) -> Set[Corner]:
        return set(
            map(
                lambda offset: self.corners[hex.coords + offset],
                Hex.CONNECTED_CORNER_OFFSETS,
            )
        )

    def get_yield_for_roll(self, roll) -> Dict[Player, RollYield]:
        total_yield: Dict[Player, RollYield] = {}
        for hex in self.hexes.values():
            if hex.token_number == roll:
                resource = hex.hex_type.get_resource()
                # Check around the hex for any settlements/cities
                for corner in self.get_connected_hex_corners(hex):
                    if corner.building is not None:
                        owner = corner.building.owner
                        if owner not in total_yield.keys():
                            total_yield[owner] = RollYield()
                        amount = (
                            2
                            if corner.building.building_type is BuildingType.CITY
                            else 1
                        )
                        total_yield[owner].add_yield(
                            resource,
                            amount,
                            source=RollYieldSource(
                                resource,
                                amount,
                                corner.building,
                                hex,
                            ),
                        )
        return total_yield


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
