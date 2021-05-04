from scipy.signal import argrelmin, argrelmax
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from core.classes.phemex import Phemex
from core.classes.srzones.srzones import SRZones

from core.classes.database import Database

MAX_DATA = 100
WIDTH = 50
EXTREMA_ORDER = 10
MAX_SLOPE = 4 * Phemex.SCALE_EP_BTCUSD

"""
Documentation for matplotlib-finance: https://github.com/matplotlib/mplfinance/blob/master/examples/using_lines.ipynb
"""

def attempt_three(df):
    df = df.reset_index()

    closes = df["closeEp"].values.tolist()

    peak_indexes = argrelmax(np.array(df["closeEp"]), order=EXTREMA_ORDER)
    peak_indexes = peak_indexes[0].tolist()

    valley_indexes = argrelmin(np.array(df["closeEp"]), order=EXTREMA_ORDER)
    valley_indexes = valley_indexes[0].tolist()

    def get_close_values(extremes):
        points = []
        for j in extremes:
            point = closes[j]
            points.append(point)
        return points

    peak_values = get_close_values(peak_indexes)
    valley_values = get_close_values(valley_indexes)

    plt.plot(df.index.values.tolist(), closes)
    plt.scatter(peak_indexes, peak_values, color="green")
    plt.scatter(valley_indexes, valley_values, color="red")

    def get_points_list(indexes, values):
        """
        # Put indexes and values together in a list of tuples.
        """
        points_list = []
        for i in range(len(indexes)):
            points_list.append((indexes[i], values[i]))
        return points_list

    support = get_points_list(valley_indexes, valley_values)
    resistance = get_points_list(peak_indexes, peak_values)

    ##
    # Iterate through the points to generate a line for the most recent support/resistance lines.
    # Must be at least two points in a row in order for there to be an eligible line.
    ##
    def get_slope_line_coords(data_points):
        if len(data_points) > 1:
            x2 = data_points[-1][0]
            y2 = data_points[-1][1]
            x1 = data_points[-2][0]
            y1 = data_points[-2][1]

            slope = (y2-y1)/(x2-x1)

            if abs(slope) < MAX_SLOPE and not 0:
                c = y1 - (slope * x1)
                xa = 0
                ya = (slope * xa) + c
                xb = MAX_DATA * 1.2
                yb = (slope * xb) + c
            else:
                xa = 0
                ya = y2
                xb = MAX_DATA * 1.2
                yb = y2
                slope = 0

            slope_line_coords = [[xa, xb], [ya, yb]]

        else:
            xa = 0
            ya = data_points[-1][1]
            xb = MAX_DATA * 1.2
            yb = data_points[-1][1]
            slope = 0

            slope_line_coords = [[xa, xb], [ya, yb]]

        return slope_line_coords, slope

    support_line, support_slope = get_slope_line_coords(support)
    resistance_line, resistance_slope = get_slope_line_coords(resistance)

    plt.plot(support_line[0], support_line[1], color="r", lw=15, alpha=0.2)
    plt.plot(support_line[0], support_line[1], color="r")
    plt.plot(resistance_line[0], resistance_line[1], color="g", lw=15, alpha=0.2)
    plt.plot(resistance_line[0], resistance_line[1], color="g")

    ##
    # Once initial SR lines are drawn, establish initial SR zones.
    ##
    def get_convergence_point(s_line, s_slope, r_line, r_slope):
        c_support = s_line[1][0]
        c_resistance = r_line[1][0]

        try:
            x = (c_resistance - c_support) / (s_slope - r_slope)
        except ZeroDivisionError:
            x = MAX_DATA

        if x >= MAX_DATA:
            return True
        else:
            return False

    sr_lines_converge = get_convergence_point(support_line, support_slope, resistance_line, resistance_slope)


    # TODO: Once zones are drawn, wait for confirmation of those zones when another peak/valley hits. There must be at
    #  least two (if horizontal) or three (if sloped) peaks/valleys in each zone to confirm the zone.

    # TODO: Once you have confirmed SR zones (needn't be both, can confirm one at a time), stop updating and wait for a
    #  breakout. Can update the zones to be more accurate if SR zones are continually confirmed (ie, additional peaks
    #  and valleys appearing inside the zones.

    # TODO: Now that SR zones are set and confident, monitor the close price in the market to see when it breaches those
    #  zones.

    ##
    # Plot graph.
    ##
    plt.savefig("fig.png")


if __name__ == "__main__":
    market_data = pd.read_csv(Database.MARKET_DATA_PATH, index_col=0)

    width = WIDTH  # Width in BTC
    sr_zones = SRZones(market_data=market_data, width=width)
    support = sr_zones.support_zone
    resistance = sr_zones.resistance_zone

    attempt_three(market_data.tail(MAX_DATA))
