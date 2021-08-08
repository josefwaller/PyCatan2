from enum import Enum


class Resource(Enum):
    """A type of resource in a game of Catan."""

    LUMBER = 0
    """The lumber resource"""
    BRICK = 1
    """The brick resource"""
    WOOL = 2
    """The wool resource"""
    GRAIN = 3
    """The grain resource"""
    ORE = 4
    """The ore resource"""

    def __repl__(self):
        return {
            Resource.LUMBER: "Lumber",
            Resource.BRICK: "Brick",
            Resource.WOOL: "Wool",
            Resource.GRAIN: "Grain",
            Resource.ORE: "Ore",
        }[self]

    def __str__(self):
        return self.__repl__()
