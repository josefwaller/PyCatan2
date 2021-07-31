from typing import Dict

from pycatan.hex_type import HexType
from pycatan.resource import Resource

MAP_HEX_TYPE_TO_RESOURCE: Dict[HexType, Resource] = {
    HexType.FOREST: Resource.LUMBER,
    HexType.HILLS: Resource.BRICK,
    HexType.MOUNTAINS: Resource.ORE,
    HexType.PASTURE: Resource.WOOL,
    HexType.FIELDS: Resource.GRAIN,
    HexType.DESERT: None,
}


def test_get_resource():
    for hex_type, resource in MAP_HEX_TYPE_TO_RESOURCE.items():
        assert hex_type.get_resource() == resource
