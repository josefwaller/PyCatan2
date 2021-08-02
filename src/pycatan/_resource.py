from enum import Enum


class Resource(Enum):
    """A type of resource in a game of Catan."""

    LUMBER = 0
    BRICK = 1
    WOOL = 2
    GRAIN = 3
    ORE = 4
