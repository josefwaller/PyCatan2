import pytest

from pycatan.player import Player
from pycatan.resource import Resource
from pycatan.errors import NotEnoughResourcesError


def test_player_starts_with_empty_hand():
    p = Player()
    for num in p.resources.values():
        assert num == 0


def test_player_can_add_resources():
    p = Player()
    p.add_resources({Resource.LUMBER: 10})
    assert p.resources[Resource.LUMBER] == 10
    p.add_resources({Resource.GRAIN: 5})
    assert p.resources[Resource.GRAIN] == 5
    p.add_resources({Resource.GRAIN: 7, Resource.LUMBER: 3})
    assert p.resources[Resource.LUMBER] == 13
    assert p.resources[Resource.GRAIN] == 12


def test_player_can_remove_resources():
    p = Player()
    p.add_resources(
        {
            Resource.LUMBER: 30,
            Resource.BRICK: 20,
            Resource.ORE: 25,
        }
    )
    p.remove_resources({Resource.LUMBER: 5})
    assert p.resources == {
        Resource.LUMBER: 25,
        Resource.BRICK: 20,
        Resource.ORE: 25,
        Resource.GRAIN: 0,
        Resource.WOOL: 0,
    }
    p.remove_resources({Resource.LUMBER: 15, Resource.BRICK: 3})
    assert p.resources == {
        Resource.LUMBER: 10,
        Resource.BRICK: 17,
        Resource.ORE: 25,
        Resource.GRAIN: 0,
        Resource.WOOL: 0,
    }
    p.remove_resources({Resource.LUMBER: 10, Resource.BRICK: 8, Resource.ORE: 23})
    assert p.resources == {
        Resource.LUMBER: 0,
        Resource.BRICK: 9,
        Resource.ORE: 2,
        Resource.GRAIN: 0,
        Resource.WOOL: 0,
    }


def test_player_has_resources():
    p = Player()
    p.add_resources({Resource.LUMBER: 10, Resource.GRAIN: 5})
    assert p.has_resources(
        {
            Resource.LUMBER: 10,
            Resource.GRAIN: 5,
        }
    )
    assert not p.has_resources(
        {
            Resource.LUMBER: 11,
        }
    )
    p.remove_resources({Resource.LUMBER: 5})
    assert not p.has_resources(
        {
            Resource.LUMBER: 10,
            Resource.GRAIN: 5,
        }
    )


def test_player_remove_resources_should_raise():
    p = Player()
    with pytest.raises(NotEnoughResourcesError):
        p.remove_resources({Resource.LUMBER: 1})

    p.add_resources({Resource.LUMBER: 3, Resource.GRAIN: 2})
    with pytest.raises(NotEnoughResourcesError):
        p.remove_resources({Resource.LUMBER: 3, Resource.GRAIN: 3})
