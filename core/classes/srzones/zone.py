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

    def value_is_in_zone(self, value: float) -> bool:
        is_below_upper_line = self.upper_boundary_line.value_is_below_line(value)
        is_above_lower_line = self.lower_boundary_line.value_is_above_line(value)

        if is_below_upper_line and is_above_lower_line:
            return True
        else:
            return False

    def value_is_above_zone(self, value: float) -> bool:
        is_above_upper_line = self.upper_boundary_line.value_is_above_line(value)
        return is_above_upper_line

    def value_is_below_zone(self, value: float) -> bool:
        is_below_lower_line = self.lower_boundary_line.value_is_below_line(value)
        return is_below_lower_line
