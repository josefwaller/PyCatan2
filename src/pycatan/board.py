from typing import Dict, Set
from itertools import product

from .coords import Coords
from .hex import Hex
from .hex_type import HexType
from .corner import Corner
from .edge import Edge
from .player import Player
from .building import CornerBuilding, EdgeBuilding
from .harbor import Harbor
from .building_type import BuildingType
from .resource import Resource
from .errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
    RequiresSettlementError,
    NotConnectedError,
)
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
                    harbors (Set[Harbor]):
                        The harbors on the board
                    robber (Coords):
                        The inital coordinates of the robber. If None, then will automatically place the robber on the first
                        desert hex it can find, and raise an error if there are non

    Attributes:
                    hexes (Dict[Coord, Hex]):
                        The hexes on this catan board, keyed by their coordinates
                    corners: (Dict[Coords, Corner]):
                        The corners on the board, keyed by their coordinates
                    edges (Dict[frozenset[Coords], Edge]):
                        The edges on the board, keyed by the coordinates of the two corners they connect
                    harbors (Dict[frozenset[Coords], Harbor]):
                        The harbors on the board, keyed by the coords of the edge they are attached to
                    robber (Set[Coords]): The location of the robber
    """

    def __init__(self, hexes: Set[Hex], harbors=set(), robber: Coords = None):
        self.hexes: Dict[Coords, Hex] = dict(zip((h.coords for h in hexes), hexes))
        self.harbors = {frozenset(h.edge_coords): h for h in harbors}
        # Position the robber on the desert
        if robber:
            self.robber = robber
        else:
            self.robber = [
                h.coords for h in self.hexes.values() if h.hex_type == HexType.DESERT
            ][0]
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

    def add_edge_building(
        self,
        player: Player,
        building_type: BuildingType,
        edge_coords: Set[Coords],
        ensure_connected: bool = True,
    ):
        """Adds an edge building to the board
        Args:
            player (Player): The player adding the building
            building_type (BuildingType): The building_type of the building being added
            edge_coords (Set[Coords]): The coordinates the edge to build the building on (i.e. the coordinates of the two corners the edge connects)
            ensure_connected (bool, optional): Whetehr to ensure that the edge building is connected to another building. Defaults to True
        Raises:
            ValueError: If the edge_coords are not valid
            CoordsBlockedError: If there is already a building on the edge
            NotConnectedError: If check_connection is true and the building is not connected to anything
        """
        for c in edge_coords:
            if c not in self.corners.keys():
                raise ValueError(
                    "Invalid edge: Edges must connect two corners on the board. %s is not a corner"
                    % c
                )

        if frozenset(edge_coords) not in self.edges.keys():
            raise ValueError("Invalid edge: Edge does not exist")

        edge: Edge = self.edges[frozenset(edge_coords)]
        if edge.building is not None:
            raise CoordsBlockedError("There is already a building on this edge")

        if ensure_connected:
            # Check if it's connected to a corner building
            valid_buildings = set(
                filter(
                    lambda b: b is not None and b.owner is player,
                    map(lambda c: self.corners[c].building, edge_coords),
                )
            )
            if len(valid_buildings) == 0:
                # Check if it's connected to another edge building
                edges_connected = set()
                for coords in edge_coords:
                    for c in self.get_corner_connected_corners(self.corners[coords]):
                        print(coords, c.coords)
                        edges_connected.add(self.edges[frozenset([coords, c.coords])])
                if (
                    len(
                        set(
                            filter(
                                lambda e: e.building is not None
                                and e.building.owner is player,
                                edges_connected,
                            )
                        )
                    )
                    == 0
                ):
                    raise NotConnectedError(
                        "Edge building is not connected to any other building"
                    )
        # Add the building
        self.edges[frozenset(edge_coords)].building = EdgeBuilding(
            player, edge_coords=edge_coords, building_type=building_type
        )

    def add_corner_building(
        self,
        player: Player,
        coords: Coords,
        building_type: BuildingType,
        ensure_connected=True,
    ):
        """Add a settlement to the board. Does not check if the player has enough cards.

        Args:
                        player (Player): The player who owns the settlement
                        coords (Coords): The coords to put the building
                        ensure_connected (bool): Whether to ensure that the building is connected to the player's roads.
                            Defaults to True

        Raises:
                        InvalidCoordsError: If `coords` is not a valid corner
                        TooCloseToBuildingError: If the building is too close to another building
                        PositionAlreadyTakenError: If the position is already taken
        """
        if building_type == BuildingType.SETTLEMENT:
            self.assert_valid_settlement_coords(coords, player, ensure_connected)
        elif building_type == BuildingType.CITY:
            self.assert_valid_city_coords(player=player, coords=coords)
        else:
            raise ValueError(
                "Invalid building type passed to Board.add_corner_building, receieved %s"
                % building_type
            )

        self.corners[coords].building = CornerBuilding(player, building_type, coords)

    def assert_valid_settlement_coords(
        self, coords: Coords, player: Player, ensure_connected
    ) -> None:
        """Checks whether the coordinates given are a valid place to build a settlement.
            Does not return anything, but raises an error if the coordinates are not valid
        Args:
            coords (Coords): The coordinates to check
            player (Player): The player building the settlement
            ensure_connected (bool): Whether the check if the settlement will be connected by road
        Raises:
            TooCloseToBuildingError: If the building is too close to another building
            PositionAlreadyTakenError: If the position is already taken
            NotConnectedError: If `check_connection` is `True` and the settlement is not connected
        """
        # Check that the coords are referencing a corner
        if coords not in self.corners.keys():
            raise InvalidCoordsError("coords must be the coordinates of a corner")
        # Check that the corner is empty
        if self.corners[coords].building is not None:
            raise CoordsBlockedError("There is already a building on this corner")
        # Check that the surrounding corners are empty
        connected_corners: Set[Corner] = self.get_corner_connected_corners(
            self.corners[coords]
        )
        if len(set(filter(lambda c: c.building is not None, connected_corners))) > 0:
            raise TooCloseToBuildingError(
                "There is a building that is not at least 2 edges away from this position"
            )
        if ensure_connected:
            edge_coords = set(
                map(lambda c: frozenset({coords, c.coords}), connected_corners)
            )
            edges = set(map(lambda e: self.edges[e], edge_coords))
            if (
                len(
                    set(
                        filter(
                            lambda edge: edge.building is not None
                            and edge.building.owner is player,
                            edges,
                        )
                    )
                )
                == 0
            ):
                raise NotConnectedError("The settlement must be connected by road")

    def assert_valid_city_coords(self, player: Player, coords: Coords) -> None:
        """Checks whether the coordinates given are a valid place to build a city by the player given.
            Does not return anything, but raises an error
        Args:
            player (Player): The player building the city
            coords (Coords): Where to build the city
        """
        # Check the coords are a corner
        if coords not in self.corners.keys():
            raise InvalidCoordsError("coords must be the coordinates of a corner")
        # Check that a settlement owned by player exists here
        if (
            self.corners[coords].building is None
            or self.corners[coords].building.owner is not player
        ):
            raise RequiresSettlementError(
                "You must update an existing settlement owned by the player into a city"
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
            if hex.token_number == roll and self.robber != hex.coords:
                resource = hex.hex_type.get_resource()
                # Check around the hex for any settlements/cities
                for corner in self.get_connected_hex_corners(hex):
                    print(corner.coords)
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

    def is_valid_hex_coords(self, coords):
        return len(set(filter(lambda x: x == coords, self.hexes.keys()))) != 0


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
            },
            harbors=[
                Harbor(
                    edge_coords={Coords(4, 0), Coords(3, 1)}, resource=Resource.GRAIN
                ),
                Harbor(edge_coords={Coords(1, 3), Coords(0, 4)}, resource=Resource.ORE),
                Harbor(edge_coords={Coords(-2, 5), Coords(-3, 5)}, resource=None),
                Harbor(
                    edge_coords={Coords(-4, 3), Coords(-4, 4)}, resource=Resource.WOOL
                ),
                Harbor(edge_coords={Coords(-4, 0), Coords(-4, 1)}, resource=None),
                Harbor(edge_coords={Coords(-2, -3), Coords(-3, -2)}, resource=None),
                Harbor(
                    edge_coords={Coords(2, -5), Coords(3, -5)}, resource=Resource.BRICK
                ),
                Harbor(
                    edge_coords={Coords(3, -4), Coords(4, -4)}, resource=Resource.LUMBER
                ),
                Harbor(edge_coords={Coords(5, -3), Coords(5, -2)}, resource=None),
            ],
        )
