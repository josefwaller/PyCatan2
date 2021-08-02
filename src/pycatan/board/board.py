from typing import Dict, Set
from itertools import product

from .coords import Coords
from .hex import Hex
from .hex_type import HexType
from .intersection import Intersection
from .path import Path
from ..player import Player
from .building import IntersectionBuilding, PathBuilding
from .harbor import Harbor
from .building_type import BuildingType
from ..errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
    RequiresSettlementError,
    NotConnectedError,
)
from ..roll_yield import RollYield, RollYieldSource


class Board:
    """An interface for holding the state of Catan boards.
    Uses a triangular grid to hold the tiles, intersections and
    paths. The Board constructor will automatically
    generate the intersections and paths from a dict of hexes,
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
                    intersections: (Dict[Coords, Intersection]):
                        The intersections on the board, keyed by their coordinates
                    paths (Dict[frozenset[Coords], Path]):
                        The paths on the board, keyed by the coordinates of the two intersections they connect
                    harbors (Dict[frozenset[Coords], Harbor]):
                        The harbors on the board, keyed by the coords of the path they are attached to
                    robber (Set[Coords]): The location of the robber
    """

    def __init__(
        self, hexes: Set[Hex], harbors: Set[Harbor] = set(), robber: Coords = None
    ):
        self.hexes: Dict[Coords, Hex] = dict(zip((h.coords for h in hexes), hexes))
        self.harbors = {frozenset(h.path_coords): h for h in harbors}
        # Position the robber on the desert
        if robber:
            self.robber = robber
        else:
            self.robber = [
                h.coords for h in self.hexes.values() if h.hex_type == HexType.DESERT
            ][0]
        # Gather the points around each hex into a set
        intersection_coords = set(
            map(
                lambda x: x[0] + x[1],
                list(product(*[self.hexes.keys(), Hex.CONNECTED_CORNER_OFFSETS])),
            )
        )
        # Add the intersections to self.intersections
        self.intersections = {}
        for coords in intersection_coords:
            self.intersections[coords] = Intersection(coords)
        # Now add all the edgges inbetween the intersections we just added
        self.paths = {}
        for c in self.intersections:
            for offset in Intersection.CONNECTED_CORNER_OFFSETS:
                coord = c + offset
                if coord in self.intersections:
                    self.paths[frozenset([c, c + offset])] = Path(set([c, c + offset]))

    def add_path_building(
        self,
        player: Player,
        building_type: BuildingType,
        path_coords: Set[Coords],
        ensure_connected: bool = True,
    ):
        """Adds an path building to the board
        Args:
            player (Player): The player adding the building
            building_type (BuildingType): The building_type of the building being added
            path_coords (Set[Coords]): The coordinates the path to build the building on (i.e. the coordinates of the two intersections the path connects)
            ensure_connected (bool, optional): Whetehr to ensure that the path building is connected to another building. Defaults to True
        Raises:
            ValueError: If the path_coords are not valid
            CoordsBlockedError: If there is already a building on the path
            NotConnectedError: If check_connection is true and the building is not connected to anything
        """
        for c in path_coords:
            if c not in self.intersections.keys():
                raise ValueError(
                    "Invalid path: Paths must connect two intersections on the board. %s is not a intersection"
                    % c
                )

        if frozenset(path_coords) not in self.paths.keys():
            raise ValueError("Invalid path: Path does not exist")

        path: Path = self.paths[frozenset(path_coords)]
        if path.building is not None:
            raise CoordsBlockedError("There is already a building on this path")

        if ensure_connected:
            # Check if it's connected to a intersection building
            valid_buildings = set(
                filter(
                    lambda b: b is not None and b.owner is player,
                    map(lambda c: self.intersections[c].building, path_coords),
                )
            )
            if len(valid_buildings) == 0:
                # Check if it's connected to another path building
                paths_connected = set()
                for coords in path_coords:
                    for c in self.get_intersection_connected_intersections(
                        self.intersections[coords]
                    ):
                        connected_path = self.paths[frozenset({coords, c.coords})]
                        # Check if there is an path building (i.e. a road) to be connected to here
                        if (
                            connected_path.building is not None
                            and connected_path.building.owner is player
                        ):
                            # Checks that we aren't going through an enemy building to be connected
                            building = self.intersections[coords].building
                            if building is None or building.owner is player:
                                paths_connected.add(path)

                if len(paths_connected) == 0:
                    raise NotConnectedError(
                        "Path building is not connected to any other building"
                    )
        # Add the building
        self.paths[frozenset(path_coords)].building = PathBuilding(
            player, path_coords=path_coords, building_type=building_type
        )

    def add_intersection_building(
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
                        InvalidCoordsError: If `coords` is not a valid intersection
                        TooCloseToBuildingError: If the building is too close to another building
                        PositionAlreadyTakenError: If the position is already taken
        """
        if building_type == BuildingType.SETTLEMENT:
            self.assert_valid_settlement_coords(coords, player, ensure_connected)
        elif building_type == BuildingType.CITY:
            self.assert_valid_city_coords(player=player, coords=coords)
        else:
            raise ValueError(
                "Invalid building type passed to Board.add_intersection_building, receieved %s"
                % building_type
            )

        self.intersections[coords].building = IntersectionBuilding(
            player, building_type, coords
        )

        # Connect the player to a harbor if they can
        for harbor in self.harbors.values():
            if coords in harbor.path_coords and harbor not in player.connected_harbors:
                player.connected_harbors.add(harbor)

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
        # Check that the coords are referencing a intersection
        if coords not in self.intersections.keys():
            raise InvalidCoordsError("coords must be the coordinates of a intersection")
        # Check that the intersection is empty
        if self.intersections[coords].building is not None:
            raise CoordsBlockedError("There is already a building on this intersection")
        # Check that the surrounding intersections are empty
        connected_intersections: Set[
            Intersection
        ] = self.get_intersection_connected_intersections(self.intersections[coords])
        if (
            len(set(filter(lambda c: c.building is not None, connected_intersections)))
            > 0
        ):
            raise TooCloseToBuildingError(
                "There is a building that is not at least 2 paths away from this position"
            )
        if ensure_connected:
            path_coords = set(
                map(lambda c: frozenset({coords, c.coords}), connected_intersections)
            )
            paths = set(map(lambda e: self.paths[e], path_coords))
            if (
                len(
                    set(
                        filter(
                            lambda path: path.building is not None
                            and path.building.owner is player,
                            paths,
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
        # Check the coords are a intersection
        if coords not in self.intersections.keys():
            raise InvalidCoordsError("coords must be the coordinates of a intersection")
        # Check that a settlement owned by player exists here
        if (
            self.intersections[coords].building is None
            or self.intersections[coords].building.owner is not player
        ):
            raise RequiresSettlementError(
                "You must update an existing settlement owned by the player into a city"
            )

    def get_intersection_connected_intersections(
        self, intersection
    ) -> Set[Intersection]:
        """Get the intersections connected to the intersection given by an path

        Args:
                        intersection (Intersection): The intersection to get the connected intersections for

        Returns:
                        Set[Intersection]: The intersections that are connected to the intersection given
        """
        connected = set()
        for c in Intersection.CONNECTED_CORNER_OFFSETS:
            if c + intersection.coords in self.intersections.keys():
                connected.add(self.intersections[c + intersection.coords])
        return connected

    def get_connected_hex_intersections(self, hex) -> Set[Intersection]:
        return set(
            map(
                lambda offset: self.intersections[hex.coords + offset],
                Hex.CONNECTED_CORNER_OFFSETS,
            )
        )

    def get_hex_connected_to_intersection(self, intersection_coords):
        return set(
            [
                intersection_coords + c
                for c in Hex.CONNECTED_CORNER_OFFSETS
                if intersection_coords + c in self.hexes
            ]
        )

    def get_yield_for_roll(self, roll) -> Dict[Player, RollYield]:
        total_yield: Dict[Player, RollYield] = {}
        for hex in self.hexes.values():
            if hex.token_number == roll and self.robber != hex.coords:
                resource = hex.hex_type.get_resource()
                # Check around the hex for any settlements/cities
                for intersection in self.get_connected_hex_intersections(hex):
                    print(intersection.coords)
                    if intersection.building is not None:
                        owner = intersection.building.owner
                        if owner not in total_yield.keys():
                            total_yield[owner] = RollYield()
                        amount = (
                            2
                            if intersection.building.building_type is BuildingType.CITY
                            else 1
                        )
                        total_yield[owner].add_yield(
                            resource,
                            amount,
                            source=RollYieldSource(
                                resource,
                                amount,
                                intersection.building,
                                hex,
                            ),
                        )
        return total_yield

    def is_valid_hex_coords(self, coords):
        return len(set(filter(lambda x: x == coords, self.hexes.keys()))) != 0

    def calculate_player_longest_road(self, player: Player) -> int:
        """Calculate the length of the longest road segment for the player given
        Args:
            player (Player): The player to calculate the longest road for
        Returns:
            int: The length of the ongest road segment
        """
        paths = [
            e
            for e in self.paths.values()
            if e.building is not None and e.building.owner is player
        ]
        starting = [(c, [e]) for e in paths for c in e.path_coords]
        if len(starting) == 0:
            return 0

        current_longest = starting[0][1]

        potential = starting
        while len(potential) > 0:
            current = potential.pop(0)
            building = self.intersections[current[0]].building
            if building is not None and building.owner is not player:
                continue
            for path in self.get_paths_for_intersection_coords(current[0]):
                if (
                    path not in current[1]
                    and path.building is not None
                    and path.building.owner is player
                ):
                    other_intersection = path.other_intersection(current[0])
                    potential.append((other_intersection, [path] + current[1]))
                    if len(current[1]) + 1 > len(current_longest):
                        current_longest = [path] + current[1]

        return len(current_longest)

    def get_paths_for_intersection_coords(self, coords: Coords) -> Set[Path]:
        """Returns all the paths who are connected to the intersection given
        Args:
            coords: The coordinates of the intersection
        Returns:
            Set[Path]: A set of the paths attached to that intersection
        """
        return set(filter(lambda e: coords in e.path_coords, self.paths.values()))
