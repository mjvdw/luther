import pandas as pd
import numpy as np
from scipy.signal import argrelmin, argrelmax
from core.classes.srzones.line import Line
from core.classes.srzones.zone import Zone
from core.classes.phemex import Phemex


class SRZones(object):
    def __init__(self,
                 market_data: pd.DataFrame,
                 width: int,
                 max_periods: int = 300,
                 extrema_order: int = 20,
                 max_slope: int = 8
                 ):
        """
        Generates support and resistance line, saves them, and provides functions to interact with those lines.
        :param market_data: A DataFrame containing OCHL market data.
        :param width: The width of the support and resistance zones.
        :param max_periods: The number of periods to use. Due to Phemex API limits, max number is 1000.
        :param extrema_order: Order to use for calculating extrema (see scipy.signal.argrelmin and argrelmax docs).
        :param max_slope: Scaled down number representing the maximum allowable slope of the SR lines (somewhat
        arbitrary at this stage)
        """
        self.market_data = market_data
        self.width = width * Phemex.SCALE_EP_BTCUSD
        self.max_periods = max_periods if max_periods <= 1000 else 1000
        self.extrema_order = extrema_order
        self.max_slope = max_slope * Phemex.SCALE_EP_BTCUSD  # Making the slope a more manageable number by scaling.

    @property
    def support_zone(self) -> Zone:
        """
        Return a Zone object defining the upper and lower bounds for support zone.
        :return: Zone object defining upper and lower bounds for support zone.
        """
        support_zone = self._get_zone_from_coords(coords=self._get_extrema_coords()["valleys"])
        return support_zone

    @property
    def resistance_zone(self) -> Zone:
        """
        Return a Zone object defining the upper and lower bounds for resistance zone.
        :return: Zone object defining upper and lower bounds for resistance zone.
        """
        resistance_zone = self._get_zone_from_coords(coords=self._get_extrema_coords()["peaks"])
        return resistance_zone

    @staticmethod
    def value_is_between_sr_zones(support: Zone, resistance: Zone, value: float, timestamp: int) -> bool:
        """
        Check whether a given value is between the support and resistance zones.
        :param support: Zone object representing the support zone.
        :param resistance: Zone object representing the resistance zone.
        :param value: the value to check.
        :param timestamp: the timestamp related to the value.
        :return: A boolean indicating whether value is between zones.
        """
        is_above_support = support.lower_boundary_line.value_is_above_line(value, timestamp)
        is_below_resistance = resistance.upper_boundary_line.value_is_below_line(value, timestamp)

        if is_above_support and is_below_resistance:
            return True
        else:
            return False

    def value_is_below_support(self, value: float, timestamp: int) -> bool:
        """
        Check whether a given value is below the support level (indicating a breakout downwards).
        :param value: the value to check.
        :param timestamp: the timestamp at which the value occurs.
        :return: A boolean indicating whether the value is below the support zone.
        """
        is_below_support = self.support_zone.value_is_below_zone(value, timestamp)
        return is_below_support

    def value_is_above_resistance(self, value: float, timestamp: int) -> bool:
        """
        Check whether a given value is above the resistance level (indicating a breakout upwards).
        :param value: the value to check.
        :param timestamp: the timestamp at which the value occurs.
        :return: A boolean indicating whether the value is above the resistance zone.
        """
        is_above_resistance = self.support_zone.value_is_above_zone(value, timestamp)
        return is_above_resistance

    def _get_extrema_coords(self) -> dict:
        """
        Calculate the maxima and minima for the given market data, and return a list of tuple coordinates.
        :return: a dictionary containing two lists of coordinates represented by (x, y) tuples (one for each peaks and
        valleys).
        """

        df = pd.DataFrame(self.market_data)  # Do not manipulate original market_data.

        closes = df["closeEp"].values.tolist()
        del closes[-5:]

        indexes = df.index.tolist()
        del indexes[-5:]

        peak_indexes = argrelmax(np.array(closes), order=self.extrema_order)[0].tolist()
        valley_indexes = argrelmin(np.array(closes), order=self.extrema_order)[0].tolist()

        peaks = [(indexes[index], closes[index]) for index in peak_indexes]
        valleys = [(indexes[index], closes[index]) for index in valley_indexes]

        extrema_coords = {
            "peaks": peaks,
            "valleys": valleys
        }

        return extrema_coords

    def _get_zone_from_coords(self, coords):
        """
        Generate a line, and create a Zone object with the line at the centre.
        :param coords: list of coordinates presenting either peaks or valleys.
        :return: a Zone object representing either a support or resistance zone.
        """

        line = Line(coords)

        # If the line is steeper than specified by the max_slope parameter, then set to horizontal through last point.
        line.slope = line.slope if abs(line.slope) <= self.max_slope else 0

        zone = Zone(line=line, width=self.width)

        return zone

    @property
    def last_minima_timestamp(self):
        """
        Helper function to get the timestamp for the most recent minima.
        :return: the timestamp for the most recent minima.
        """
        last_minima_timestamp = self._get_extrema_coords()["valleys"][-1][0]
        return last_minima_timestamp

    @property
    def last_maxima_timestamp(self):
        """
        Helper function to get the timestamp fot the most recent maxima.
        :return: the timestamp for the most recent maxima.
        """
        last_maxima_timestamp = self._get_extrema_coords()["peaks"][-1][0]
        return last_maxima_timestamp
