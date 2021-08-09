from typing import Dict, Set, Optional, FrozenSet
from itertools import product

from ._coords import Coords
from ._hex import Hex
from ._hex_type import HexType
from ._intersection import Intersection
from ._path import Path
from .._player import Player
from ._building import IntersectionBuilding, PathBuilding
from ._harbor import Harbor
from ._building_type import BuildingType
from .._resource import Resource
from ..errors import (
    InvalidCoordsError,
    TooCloseToBuildingError,
    CoordsBlockedError,
    RequiresSettlementError,
    NotConnectedError,
)
from .._roll_yield import RollYield, RollYieldSource


class Board:
    """An interface for holding the state of Catan boards.

    Uses a triangular grid to hold the tiles, intersections and
    paths. The Board constructor will automatically
    generate the intersections and paths from a dict of hexes,
    assuming all the hexes tile correctly.

    Args:
                    hexes:
                        The hexes on the board, keyed by their coordinates
                    harbors:
                        The harbors on the board
                    robber:
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
        ensure_connected: Optional[bool] = True,
    ):
        """Add an path building to the board.

        Do not check if the player has enough resources, or any other checks other than the building's location being valid.

        Args:
            player: The player adding the building
            building_type: The building_type of the building being added
            path_coords: The coordinates the path to build the building on (i.e. the coordinates of the two intersections the path connects)
            ensure_connected: Whetehr to ensure that the path building is connected to another building. Defaults to True
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

        if building_type is BuildingType.ROAD:
            self.assert_valid_road_coords(player, path_coords, ensure_connected)

        # Add the building
        self.paths[frozenset(path_coords)].building = PathBuilding(
            player, path_coords=path_coords, building_type=building_type
        )

    def assert_valid_road_coords(
        self,
        player: Player,
        path_coords: Set[Coords],
        ensure_connected: Optional[bool] = True,
    ):
        """Assert that a given edge is a valid place for the player to build a road.

        Args:
            player: The player
            path_coords: The coordinates of the two intersections connected by the path
            ensure_connected: Whether to assert that the path is connected to the player's existing roads or settlements
        """
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
                        "Road is not connected to any other building"
                    )

    def add_intersection_building(
        self,
        player: Player,
        coords: Coords,
        building_type: BuildingType,
        ensure_connected: Optional[bool] = True,
    ):
        """Add an intersection building to the board.

        Args:
            player: The player who owns the settlement
            coords: The coords to put the building
            ensure_connected: Whether to ensure that the building is connected to the player's roads. Defaults to True
        Raises:
            InvalidCoordsError: If coords is not a valid intersection
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
        self, coords: Coords, player: Player, ensure_connected: Optional[bool]
    ) -> None:
        """Check whether the coordinates given are a valid place to build a settlement.

        Does not return anything, but raises an error if the coordinates are not valid.

        Args:
            coords: The coordinates to check
            player: The player building the settlement
            ensure_connected: Whether the check if the settlement will be connected by road
        Raises:
            TooCloseToBuildingError: If the building is too close to another building
            PositionAlreadyTakenError: If the position is already taken
            NotConnectedError: If `check_connection` is `True` and the settlement is not connected
        """
        # Check that the coords are referencing a intersection
        if coords not in self.intersections:
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

    def assert_valid_city_coords(self, player: Player, coords: Coords):
        """Check whether the coordinates given are a valid place to build a city by the player given.

        Args:
            player: The player building the city
            coords: Where to build the city
        """
        # Check the coords are a intersection
        if coords not in self.intersections.keys():
            raise InvalidCoordsError("coords must be the coordinates of a intersection")
        # Check that a settlement owned by player exists here
        if (
            self.intersections[coords].building is None
            or self.intersections[coords].building.owner is not player
            or self.intersections[coords].building.building_type
            is not BuildingType.SETTLEMENT
        ):
            raise RequiresSettlementError(
                "You must update an existing settlement owned by the player into a city"
            )

    def is_valid_settlement_coords(
        self, player: Player, coords: Coords, ensure_connected: Optional[bool]
    ) -> bool:
        """Check whether the given coordinates are a valid place for the player to build a settlement.

        Args:
            player: The player
            coords: The coordinates to check
            ensure_connected: Whetehr to ensure that the settlement will be connected to the player's roads
        Returns:
            Whether the coordinates are a valid settlement location for the player
        """
        try:
            self.assert_valid_settlement_coords(
                player=player, coords=coords, ensure_connected=ensure_connected
            )
        except:  # noqa: E722
            return False
        return True

    def is_valid_city_coords(self, player: Player, coords: Coords) -> bool:
        """Check whether the coordinates given are valid city coordinates.

        Args:
            player: The player
            coords: The coordinates to check
        Returns:
            Whether the coords are a valid place for the player to build a city
        """
        try:
            self.assert_valid_city_coords(player=player, coords=coords)
        except:  # noqa: E722
            return False
        return True

    def is_valid_road_coords(
        self,
        player: Player,
        path_coords: Set[Coords],
        ensure_connected: Optional[bool] = True,
    ) -> bool:
        """Check whether the path coordinates given are valid road coordinate for the player given.

        Args:
            player: The player
            path_coords: The coordinates of the path
            ensure_connected: Whether to ensure that the road is connected to the player's existing roads/buildings. Defaults to True
        Returns:
            Whether the player can build a road on this path
        """
        try:
            self.assert_valid_road_coords(
                player, path_coords, ensure_connected=ensure_connected
            )
        except:  # noqa: E722
            return False
        return True

    def get_valid_settlement_coords(
        self, player: Player, ensure_connected: Optional[bool] = True
    ) -> Set[Coords]:
        """Get all the valid settlement coordinates for the player to build a settlement.

        Args:
            player: The player to check for valid settlement coordinates
            ensure_connected: Whether to ensure the coordinates are connected to the player's roads
        Returns:
            The coordinates of all the valid settlement intersections
        """
        return set(
            [
                i
                for i in self.intersections.keys()
                if self.is_valid_settlement_coords(player, i, ensure_connected)
            ]
        )

    def get_valid_city_coords(self, player: Player) -> Set[Coords]:
        """Get all the valid city coordinates for the player to build a city.

        Args:
            player (Player): The player building the city
        Returns
            The coordinates of all the valid city locations
        """
        return set(
            [
                i
                for i in self.intersections.keys()
                if self.is_valid_city_coords(player, i)
            ]
        )

    def get_valid_road_coords(
        self,
        player: Player,
        ensure_connected: Optional[bool] = True,
        connected_intersection: Optional[Coords] = None,
    ) -> Set[FrozenSet[Coords]]:
        """Get all the valid coordinates for the player to build a road.

        Args:
            player: The player building the road
            ensure_connected:
                Whether to only return the path coordinates that are connected to the player's existing roads/settlements. Defaults to True
            connected_intersection: The coords of an intersection that the potential road must be attached to. Defaults to None
        Returns:
            The coordinates of all the paths where the player can build a road.
        """
        to_return = set()
        for path_coords in self.paths.keys():
            if self.is_valid_road_coords(
                player=player,
                ensure_connected=ensure_connected,
                path_coords=path_coords,
            ):
                if not connected_intersection or connected_intersection in path_coords:
                    to_return.add(path_coords)

        return to_return

    def get_intersection_connected_intersections(
        self, intersection: Intersection
    ) -> Set[Intersection]:
        """Get all the intersections connected to the intersection given by an path.

        Args:
            intersection: The intersection to get the connected intersections for

        Returns:
            The intersections that are connected to the intersection given
        """
        connected = set()
        for c in Intersection.CONNECTED_CORNER_OFFSETS:
            if c + intersection.coords in self.intersections.keys():
                connected.add(self.intersections[c + intersection.coords])
        return connected

    def get_connected_hex_intersections(self, hex: Hex) -> Set[Intersection]:
        """Get all of the intersections that are connected to the hex.

        Args:
            hex: The hex

        Returns:
            All 6 intersections that are around this hex
        """
        return set(
            map(
                lambda offset: self.intersections[hex.coords + offset],
                Hex.CONNECTED_CORNER_OFFSETS,
            )
        )

    def get_hexes_connected_to_intersection(
        self, intersection_coords: Coords
    ) -> Set[Coords]:
        """Get all the hexes' coordinates that are connected to the intersection with the coordinates provided.

        Args:
            intersection_coords: The coords of an intersection
        Returns:
            The hexes connected to the intersection
        """
        return set(
            [
                intersection_coords + c
                for c in Hex.CONNECTED_CORNER_OFFSETS
                if intersection_coords + c in self.hexes
            ]
        )

    def get_yield_for_roll(self, roll: int) -> Dict[Player, RollYield]:
        """Calculate the resources given out for a particular roll.

        Args:
            roll: The number rolled
        Returns:
            The RollYield object containing the information for what each player gets, keyed by the player
        """
        total_yield: Dict[Player, RollYield] = {}
        for hex in self.hexes.values():
            if hex.token_number == roll and self.robber != hex.coords:
                resource = hex.hex_type.get_resource()
                # Check around the hex for any settlements/cities
                for intersection in self.get_connected_hex_intersections(hex):
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

    def is_valid_hex_coords(self, coords: Coords) -> bool:
        """Check whether the coordinates given are valid hex coordinates.

        Args:
            coords: The coordinates
        Returns:
            Whether there is a hex at those coordinates
        """
        return len(set(filter(lambda x: x == coords, self.hexes.keys()))) != 0

    def calculate_player_longest_road(self, player: Player) -> int:
        """Calculate the length of the longest road segment for the player given.

        Args:
            player: The player to calculate the longest road for
        Returns:
            The length of the ongest road segment
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
        """Get all the paths who that connected to the intersection given.

        Args:
            coords: The coordinates of the intersection
        Returns:
            A set of the paths attached to that intersection
        """
        return set(filter(lambda e: coords in e.path_coords, self.paths.values()))

    def get_hex_resources_for_intersection(self, coords: Coords) -> Dict[Resource, int]:
        """Get the associated resources for the hexes around the intersection at the coords given.

        Args:
            coords: The coordinates of an intersection
        Returns:
            The amounts of resources from the hexes around this intersection
        """
        resources = [
            self.hexes[h].hex_type.get_resource()
            for h in self.get_hexes_connected_to_intersection(coords)
        ]
        return {res: resources.count(res) for res in resources if res is not None}

    def get_players_on_hex(self, coords: Coords) -> Set[Player]:
        """Get all the players who have a building on the edge of the given hex.

        Args:
            coords: The coords of the hex
        Returns:
            The players with a building on the edge of the hex
        """
        return set(
            [
                i.building.owner
                for i in self.get_connected_hex_intersections(self.hexes[coords])
                if i.building is not None
            ]
        )

    def __str__(self):
        from ._board_renderer import BoardRenderer

        return BoardRenderer(self).get_board_as_string()

    def __repl__(self):
        return self.__str__()
