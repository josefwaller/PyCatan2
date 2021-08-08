import pytest
import random

from pycatan import Player, Resource
from pycatan.errors import NotEnoughResourcesError

from .helpers import (
    get_resource_hand,
    assert_trades_equal,
    get_harbor,
    get_trades,
)


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
    p.add_resources(get_resource_hand(lumber=30, brick=20, ore=25))
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


def test_player_get_trades():
    p = Player()
    assert len(p.get_possible_trades()) == 0
    p.add_resources({Resource.LUMBER: 4})
    assert_trades_equal(p.get_possible_trades(), get_trades(Resource.LUMBER, 4))


def test_player_get_trades_multiple_trades():
    p = Player()
    p.add_resources({Resource.GRAIN: 4, Resource.BRICK: 4})
    assert_trades_equal(
        p.get_possible_trades(),
        get_trades(Resource.GRAIN, 4) + get_trades(Resource.BRICK, 4),
    )


def test_player_get_trades_harbor():
    p = Player()
    p.add_resources(get_resource_hand(brick=2))
    p.connected_harbors.add(get_harbor(resource=Resource.BRICK))
    assert_trades_equal(p.get_possible_trades(), get_trades(Resource.BRICK, 2))


def test_player_get_trades_multiple_harbors():
    p = Player()
    p.add_resources(get_resource_hand(lumber=2, ore=2, grain=2))
    for r in [Resource.LUMBER, Resource.ORE, Resource.GRAIN]:
        p.connected_harbors.add(get_harbor(resource=r))
    assert_trades_equal(
        p.get_possible_trades(),
        get_trades(Resource.LUMBER, 2)
        + get_trades(Resource.ORE, 2)
        + get_trades(Resource.GRAIN, 2),
    )


def test_player_get_trades_generic_harbor():
    p = Player()
    p.add_resources(get_resource_hand(wool=3, lumber=3))
    p.connected_harbors.add(get_harbor())
    assert_trades_equal(
        p.get_possible_trades(),
        get_trades(Resource.WOOL, 3) + get_trades(Resource.LUMBER, 3),
    )


def test_player_get_trades_mixed():
    p = Player()
    p.add_resources(get_resource_hand(lumber=4, wool=2, brick=2))
    p.connected_harbors.add(get_harbor(resource=Resource.WOOL))
    assert_trades_equal(
        p.get_possible_trades(),
        get_trades(Resource.LUMBER, 4) + get_trades(Resource.WOOL, 2),
    )


def test_player_get_trades_best_deal():
    p = Player()
    p.add_resources(get_resource_hand(lumber=4))
    assert_trades_equal(p.get_possible_trades(), get_trades(Resource.LUMBER, 4))
    p.connected_harbors.add(get_harbor())
    assert_trades_equal(p.get_possible_trades(), get_trades(Resource.LUMBER, 3))
    p.connected_harbors.add(get_harbor(resource=Resource.LUMBER))
    assert_trades_equal(p.get_possible_trades(), get_trades(Resource.LUMBER, 2))


def test_player_get_random_resource():
    random.seed(18)
    p = Player()
    p.add_resources(get_resource_hand(lumber=4, brick=5))
    assert p.get_random_resource() == Resource.LUMBER
    assert p.get_random_resource() == Resource.LUMBER
    assert p.get_random_resource() == Resource.BRICK
    assert p.get_random_resource() == Resource.BRICK
    assert p.get_random_resource() == Resource.LUMBER
    p.remove_resources(get_resource_hand(lumber=4, brick=5))
    assert p.get_random_resource() is None
