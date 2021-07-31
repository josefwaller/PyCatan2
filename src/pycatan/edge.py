class Edge:
    """An edge on a Catan board

    Args:
            coords (set(Coords, Coords)): The coordinates of the two corners
                that the edge connects
            building (EdgeBuilding, optiona): The building on this edge

    Attributes:
            coords (set(Coords, Coords)): The coordinates of the two corners
                that the edge connects
            building (EdgeBuilding, optional): The building on this edge
    """

    def __init__(self, coords, building=None):
        self.coords = coords
        self.building = building
