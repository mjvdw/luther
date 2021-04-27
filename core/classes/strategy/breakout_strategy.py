import pandas as pd

from core.classes.strategy.strategy import Strategy
from core.classes.state import State
from core.classes.srzones.srzones import SRZones
from core.classes.srzones.zone import Zone
from core.classes.signal import Signal
from core.classes.user import User


class BreakoutStrategy(Strategy):

    def __init__(self, params: dict):
        """
        A more complex "Breakout" strategy. It isn't possible to conveniently specify the conditions for a breakout
        strategy the same as for a simpler scalping strategy, so the logic is more hardcoded. However, wherever possible
        it pulls parameters from the user-provided file.
        :param params: The user-provided parameters for the strategy.
        """
        super().__init__(params)

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
        """

        :param data:
        :return:
        """

        ##
        # STEP 1: Set up support and resistance zones.
        ##
        state = State()

        support = state.support
        resistance = state.resistance

        if not (support and resistance):
            support, resistance = self._draw_sr_zones(data)
            state.support = support
            state.resistance = resistance

        ##
        # STEP 2: Check whether there are any new extrema. If there are, determine whether to update zone.
        ##
        new_support, new_resistance = self._draw_sr_zones(data)
        zones = [new_support, new_resistance]
        is_between_sr_zones = [SRZones.value_is_between_sr_zones(support, resistance, zone.value, zone.timestamp) for
                               zone in zones]

        if not all(is_between_sr_zones):
            print("Redrawing support and resistance zones.")
            support, resistance = self._draw_sr_zones(data)
            state.support = support
            state.resistance = resistance

        if support.line.slope < resistance.line.slope:
            # Indicating that the lines are diverging.
            support.line.slope = 0
            resistance.line.slope = 0

        self._plot_zones(data, support, resistance)

        # TODO: Delete me!
        from core.classes.phemex import Phemex
        print(support.line.slope / Phemex.SCALE_EP_BTCUSD)
        print(resistance.line.slope / Phemex.SCALE_EP_BTCUSD)

        ##
        # STEP 3: Once support and resistance lines are confirmed, check current price against zones.
        ##
        last_close_price = data["lastCloseEp"].tail(1).values[0]  # Note, not "closeEp" as in other parts of script.
        price_timestamp = data["timestamp"].tail(1).values[0]

        price_between_sr = SRZones.value_is_between_sr_zones(support, resistance, last_close_price, price_timestamp)

        if price_between_sr:
            action = Signal.WAIT
            confidence = 1
        else:
            confidence = 2
            price_above_resistance_zone = resistance.value_is_above_zone(last_close_price, price_timestamp)
            if price_above_resistance_zone:
                action = Signal.ENTER_LONG
            else:
                action = Signal.ENTER_SHORT

        signal = {
            "action": action,
            "confidence": confidence,
            "strategy_type": self.strategy_type
        }

        return [signal]

    def check_exit_conditions(self, data: pd.DataFrame, user: User) -> list:
        """

        :param data:
        :param user:
        :return:
        """
        if user.is_open_positions and not user.is_unfilled_orders:
            action = Signal.SET_EXIT_LIMIT
        else:
            action = Signal.WAIT

        signal = {
            "action": action,
            "confidence": 1,
            "strategy_type": self.strategy_type
        }

        return [signal]

    def _draw_sr_zones(self, data: pd.DataFrame) -> (Zone, Zone):
        """
        Helper method to draw new support and resistance zones.
        :param data: data required to draw the support and resistance zones.
        """
        sr_zones = SRZones(market_data=data, width=self.params["breakout"]["zone_width"])
        support = sr_zones.support_zone
        resistance = sr_zones.resistance_zone
        return support, resistance

    def _plot_zones(self, data, support, resistance):
        """
        Helper method to produce a plot to show the strategy's working.
        :param data:
        :param support:
        :param resistance:
        :return:
        """
        from scipy.signal import argrelmin, argrelmax
        import numpy as np
        import matplotlib.pyplot as plt

        plt.figure()

        sr_zones = SRZones(market_data=data, width=self.params["breakout"]["zone_width"])
        df = data.tail(sr_zones.max_periods)
        df = df.reset_index()

        closes = df["closeEp"].values.tolist()

        peak_indexes = argrelmax(np.array(df["closeEp"]), order=sr_zones.extrema_order)
        peak_indexes = peak_indexes[0].tolist()

        valley_indexes = argrelmin(np.array(df["closeEp"]), order=sr_zones.extrema_order)
        valley_indexes = valley_indexes[0].tolist()

        def get_close_values(extremes):
            points = []
            for j in extremes:
                point = closes[j]
                points.append(point)
            return points

        peak_values = get_close_values(peak_indexes)
        valley_values = get_close_values(valley_indexes)

        plt.plot(df.index.values.tolist(), closes, color="b")
        plt.scatter(peak_indexes, peak_values, color="g")
        plt.scatter(valley_indexes, valley_values, color="r")

        def get_points_list(indexes, values):
            """
            # Put indexes and values together in a list of tuples.
            """
            points_list = []
            for i in range(len(indexes)):
                points_list.append((indexes[i], values[i]))
            return points_list

        s = get_points_list(valley_indexes, valley_values)
        r = get_points_list(peak_indexes, peak_values)

        ##
        # Iterate through the points to generate a line for the most recent support/resistance lines.
        # Must be at least two points in a row in order for there to be an eligible line.
        ##
        def get_slope_line_coords(data_points, slope):
            if len(data_points) > 1:
                x2 = data_points[-1][0]
                y2 = data_points[-1][1]
                x1 = data_points[-2][0]
                y1 = data_points[-2][1]

                if abs(slope) < sr_zones.max_slope and not 0:
                    c = y1 - (slope * x1)
                    xa = 0
                    ya = (slope * xa) + c
                    xb = sr_zones.max_periods * 1.2
                    yb = (slope * xb) + c
                else:
                    xa = 0
                    ya = y2
                    xb = sr_zones.max_periods * 1.2
                    yb = y2
                    slope = 0

                slope_line_coords = [[xa, xb], [ya, yb]]

            else:
                xa = 0
                ya = data_points[-1][1]
                xb = sr_zones.max_periods * 1.2
                yb = data_points[-1][1]
                slope = 0

                slope_line_coords = [[xa, xb], [ya, yb]]

            return slope_line_coords, slope

        support_line, support_slope = get_slope_line_coords(s, support.line.slope)
        resistance_line, resistance_slope = get_slope_line_coords(r, resistance.line.slope)

        plt.plot(support_line[0], support_line[1], color="r", lw=5, alpha=0.2)
        plt.plot(support_line[0], support_line[1], color="r")
        plt.plot(resistance_line[0], resistance_line[1], color="g", lw=5, alpha=0.2)
        plt.plot(resistance_line[0], resistance_line[1], color="g")

        plt.savefig("fig.png", dpi=150)
