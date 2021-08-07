class Coords:
    """
    A class used to represent coordinates on the Catan board.

    Stores a coordinate on a triangular grid, so that each
    hex and point both has a unique coord.

    Args:
            q (int): The q coordinate
            r (int): The r coordinate
    """

    def __init__(self, q, r):
        self.q = q
        self.r = r

    def __hash__(self):
        return hash((self.q, self.r))

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r

    def __add__(self, other):
        return Coords(self.q + other.q, self.r + other.r)

    def __sub__(self, other):
        return Coords(self.q - other.q, self.r - other.r)

    def __str__(self):
        return "(q: %d, r:%d)" % (self.q, self.r)

    def __repr__(self):
        return self.__str__()
