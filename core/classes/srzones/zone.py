from core.classes.srzones.line import Line


class Zone(object):
    def __init__(self, line: Line, width: int):
        """
        A zone represented as space between two infinite lines. Provides helper functions to determine whether the lines
        making up the zone are converging, diverging or parallel, and whether a point is within the zone.
        :param line: Line object representing the centre of the zone.
        :param width: The width of the zone in the units of the y-axis / vertical plane on which the zone is drawn.
        """
        self.line = line
        self.width = width

    def is_value_in_zone(self, value) -> bool:

        return False

    def is_value_above_zone(self, value) -> bool:
        return False

    def is_value_below_zone(self, value) -> bool:
        return False
