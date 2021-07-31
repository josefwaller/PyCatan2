class Corner:
    """A corner on the Catan board

    Args:
            coords (Coords): The coordinates of the corner
            building (CornerBuilding, optional): The building on the corner

    Attributes:
            coords (Coords): The coordinates of the corner
            building (CornerBuilding, optional): The building on the corner
    """

    def __init__(self, coords, building=None):
        self.coords = coords
        self.building = building
