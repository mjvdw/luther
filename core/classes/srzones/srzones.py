import pandas as pd
import numpy as np
from scipy.signal import argrelmin, argrelmax
from core.classes.srzones.line import Line
from core.classes.srzones.zone import Zone
from core.classes.phemex import Phemex


class SRZones(object):
    def __init__(self,
                 market_data:
                 pd.DataFrame,
                 width: int,
                 max_periods: int = 1000,
                 extrema_order: int = 10,
                 max_slope: int = 4
                 ):
        """
        Generates support and resistance line, saves them, and provides functions to interact with those lines.
        :param market_data: A DataFrame containing OCHL market data.
        :param max_periods: The number of periods to use. Due to Phemex API limits, max number is 1000.
        :param extrema_order: Order to use for calculating extrema (see scipy.signal.argrelmin and argrelmax docs).
        """
        self.market_data = market_data
        self.width = width
        self.max_periods = max_periods if max_periods <= 1000 else 1000
        self.extrema_order = extrema_order
        self.max_slope = max_slope * Phemex.SCALE_EP_BTCUSD  # Making the slope a more manageable number by scaling.

    @property
    def support_zone(self) -> Zone:
        """
        Return a Zone object containing the upper and lower bounds for support zone.
        :return: Zone object containing upper and lower bounds for support zone.
        """
        support_zone = self._get_zone_from_coords(self._get_extrema_coords()["valleys"])
        return support_zone

    @property
    def resistance_zone(self) -> Zone:
        """
        Return a Zone object containing the upper and lower bounds for resistance zone.
        :return: Zone object containing upper and lower bounds for resistance zone.
        """
        resistance_zone = self._get_zone_from_coords(self._get_extrema_coords()["peaks"])
        return resistance_zone

    def _get_extrema_coords(self) -> dict:
        """
        Calculate the maxima and minima for the given market data, and return a list of tuple coordinates.
        :return: a dictionary containing two lists of coordinates represented by (x, y) tuples (one for each peaks and
        valleys).
        """

        df = self.market_data  # Do not manipulate original market_data.
        df = df.reset_index()  # Instead of using timestamp, use 1..n index style, for easier maths.

        closes = df["closeEp"].values.tolist()

        peak_indexes = argrelmax(np.array(df["closeEp"]), order=self.extrema_order)[0].tolist()
        valley_indexes = argrelmin(np.array(df["closeEp"]), order=self.extrema_order)[0].tolist()

        peaks = [(index, closes[index]) for index in peak_indexes]
        valleys = [(index, closes[index]) for index in valley_indexes]

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
        line.recalculate_intercept(line.slope)

        zone = Zone(line=line, width=self.width)

        return zone

