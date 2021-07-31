from .player import Player
from .building_type import BuildingType
from .coords import Coords


class Building:
    """A building on the Catan board

    Attributes:
            owner (Player): The player who owns this building
            building_type (BuildingType): The type of building this is

    Args:
            owner (Player): The player who owns this building
            building_type (BuildingType): The type of building this is
    """

    def __init__(self, owner: Player, building_type: BuildingType):
        self.owner = owner
        self.building_type = building_type


class CornerBuilding(Building):
    """A building that is built on a corner.
    I.e. a settlement or a city

    Attributes:
            owner (Player): The player who owns this building
            building_type (BuildingType): The type of building this is
            coords (Coords): The coords the building is at

    Args:
            owner (Player): The player who owns this building
            building_type (BuildingType): The type of building this is
            coords (Coords): The coords the building is at
    """

    def __init__(self, owner: Player, building_type: BuildingType, coords: Coords):
        super().__init__(owner, building_type)
        self.coords = coords
