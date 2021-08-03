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
