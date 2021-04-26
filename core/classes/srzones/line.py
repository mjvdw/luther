class Line(object):
    def __init__(self, coords: [tuple]):
        """
        A line set up using the y = mx + c mathematical format, which m is slope and c is the y intercept.
        :param coords: A list of length 2, containing two tuples
        """
        self.coords = coords

        self._slope = self._get_line_slope_from_coords(self.coords)
        self._intercept = self._get_line_intercept_from_coords(self.coords, self.slope)

    @property
    def slope(self) -> int:
        return self._slope

    @slope.setter
    def slope(self, slope):
        self._slope = slope

    @property
    def intercept(self) -> int:
        return self._intercept

    @staticmethod
    def _get_line_slope_from_coords(coords: [tuple]) -> int:
        """
        Calculate the slope of the support or resistance line. If the line is steeper than the specified max_slope
        parameter, then make it horizontal (ie, slope of 0).
        :param coords: The list of coordinates for either peaks or valleys.
        :return: An integer representing either the slope of the line, or a horizontal line if the actual slope is too
        steep.
        """
        if len(coords) > 1:
            x2 = coords[-1][0]
            y2 = coords[-1][1]
            x1 = coords[-2][0]
            y1 = coords[-2][1]

            slope = (y2 - y1) / (x2 - x1)  # Derived from "y = mx + c"
        else:
            slope = 0

        return slope

    @staticmethod
    def _get_line_intercept_from_coords(coords: [tuple], slope: int) -> int:
        """
        Get the "y" value at the point where the line intercepts the y-axis.
        :param coords: Two coordinates representing the line.
        :param slope: Slope of the line is required to calculate intercept.
        :return: An integer representing the y-axis value of the line where the line intercept the y-axis
        """
        x = coords[-1][0]
        y = coords[-1][1]

        intercept = y - (slope * x)

        return intercept

    def recalculate_intercept(self, slope: int):
        """
        If the slope is changed, this will recalculate the y-intercept based on that new slope value.
        :param slope: The new slope value.
        :return: The recalculated y-intercept.
        """
        self._intercept = self._get_line_intercept_from_coords(coords=self.coords, slope=slope)
