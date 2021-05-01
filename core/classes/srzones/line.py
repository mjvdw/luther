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
        self._recalculate_intercept(slope)
        self._slope = slope

    @property
    def intercept(self) -> int:
        return self._intercept

    @intercept.setter
    def intercept(self, intercept):
        self._intercept = intercept

    def get_value_for_timestamp(self, timestamp: int):
        """
        Calculate the y-axis value based on a timestamp received as an argument.
        :param timestamp: the timestamp for the corresponding y-axis value.
        :return: The value.
        """
        # y = mx + c
        value = (self.slope * timestamp) + self.intercept
        return value

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
        Note that the point where the line intercepts will be where x is the first timestamp available in the data.
        :param coords: Two coordinates representing the line.
        :param slope: Slope of the line is required to calculate intercept.
        :return: An integer representing the y-axis value of the line where the line intercept the y-axis
        """
        x = coords[-1][0]
        y = coords[-1][1]

        intercept = y - (slope * x)

        return intercept

    def _recalculate_intercept(self, slope: int):
        """
        If the slope is changed, this will recalculate the y-intercept based on that new slope value.
        :param slope: The new slope value.
        :return: The recalculated y-intercept.
        """
        self._intercept = self._get_line_intercept_from_coords(coords=self.coords, slope=slope)

    def value_is_above_line(self, value: float, timestamp: int) -> bool:
        """
        Test whether a given value is above the line.
        :param timestamp: The timestamp at which the given value occurred.
        :param value: The value to test against the line.
        :return: A boolean, true if value is above the line, false if it is on or below the line.
        """
        # y = mx + c
        line_value = (self.slope * timestamp) + self.intercept
        if line_value < value:
            return True
        else:
            return False

    def value_is_below_line(self, value: float, timestamp: int) -> bool:
        """
        Test whether a given value is below the line.
        :param value: The value to test against the line.
        :param timestamp: The timestamp at which the given value occurred.
        :return: A boolean, true if value is below the line, false if it is on or above the line.
        """
        # y = mx + c
        line_value = (self.slope * timestamp) + self.intercept
        if line_value > value:
            return True
        else:
            return False

    def value_is_on_line(self, value: float, timestamp: int) -> bool:
        """
        Test whether a given value is on the line.
        :param value: The value to test against the line.
        :param timestamp: The timestamp at which the given value occurred.
        :return: A boolean, true if value is on the line, false if it is above or below the line.
        """
        # y = mx + c
        line_value = (self.slope * timestamp) + self.intercept
        if line_value == value:
            return True
        else:
            return False

    def diverges_in_future(self, other_line) -> bool:
        """

        :param other_line:
        :return:
        """
        try:
            intercept_timestamp = (self.intercept - other_line.intercept) / (other_line.slope - self.slope)
        except ZeroDivisionError:
            return True

        if intercept_timestamp > self.coords[-1][0] and other_line.coords[-1][0]:
            return False
        else:
            return True
