class InvalidCoordsError(Exception):
    """Generic error for when the coordinates passed are invalid for some reason"""

    pass


class RequiresSettlementError(InvalidCoordsError):
    """Error for when trying to build a city that is not on top of an existing settlement"""

    pass


class TooCloseToBuildingError(InvalidCoordsError):
    """Error for when a building is to close to the one the player is tring to build"""

    pass


class CoordsBlockedError(InvalidCoordsError):
    """Error for when the coordinates are blocked already"""

    pass


class NotEnoughResourcesError(Exception):
    """Error when the player doesn't have enough resources to do this action"""
