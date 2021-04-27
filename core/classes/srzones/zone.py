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

    @property
    def upper_boundary_line(self):
        upper_boundary_line = self.line
        upper_boundary_line.intercept += self.width / 2
        return upper_boundary_line

    @property
    def lower_boundary_line(self):
        lower_boundary_line = self.line
        lower_boundary_line.intercept -= self.width / 2
        return lower_boundary_line

    @property
    def timestamp(self):
        """
        Get the latest extrema timestamp for the line forming this zone.
        :return: the latest timestamp for the line forming this zone.
        """
        timestamp = self.line.coords[-1][0]
        return timestamp

    @property
    def value(self):
        """
        Get the latest value for the extrema forming this zone.
        :return: the latest value of the extrema forming this zone.
        """
        value = self.line.coords[-1][1]
        return value

    def value_is_in_zone(self, value: float, timestamp: int) -> bool:
        is_below_upper_line = self.upper_boundary_line.value_is_below_line(value, timestamp)
        is_above_lower_line = self.lower_boundary_line.value_is_above_line(value, timestamp)

        if is_below_upper_line and is_above_lower_line:
            return True
        else:
            return False

    def value_is_above_zone(self, value: float, timestamp: int) -> bool:
        is_above_upper_line = self.upper_boundary_line.value_is_above_line(value, timestamp)
        return is_above_upper_line

    def value_is_below_zone(self, value: float, timestamp: int) -> bool:
        is_below_lower_line = self.lower_boundary_line.value_is_below_line(value, timestamp)
        return is_below_lower_line
