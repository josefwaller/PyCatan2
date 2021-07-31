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
