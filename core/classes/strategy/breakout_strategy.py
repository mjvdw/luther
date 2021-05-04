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

        latest_timestamp = data["timestamp"].tail(1).values[0]
        last_saved_timestamp = max(support.timestamp, resistance.timestamp) if (support and resistance) else 0

        if not (support and resistance) or (latest_timestamp - last_saved_timestamp) > 300:  # 300 seconds = 5 minutes.
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
            state.support = new_support
            support = new_support
            state.resistance = new_resistance
            resistance = new_resistance
            # from core.classes.slack import Slack
            # Slack().send(f"Drawing SR Zones. Support at level {support.value} and resistance at {resistance.value}.")

        if support.line.diverges_in_future(resistance.line):
            if support.line.slope < 0 and resistance.line.slope < 0:
                support.line.slope = 0
            elif support.line.slope > 0 and resistance.line.slope > 0:
                resistance.line.slope = 0
            else:
                support.line.slope = 0
                resistance.line.slope = 0

        # self._plot_zones(data, support, resistance)

        ##
        # STEP 3: Once support and resistance lines are confirmed, check current price against zones.
        ##
        last_close_price = data["lastCloseEp"].tail(1).values[0]
        price_timestamp = data["timestamp"].tail(1).values[0]

        price_between_sr = SRZones.value_is_between_sr_zones(support, resistance, last_close_price, price_timestamp)

        if price_between_sr:
            action = Signal.WAIT
            # TODO: DELETE ME
            # action = Signal.ENTER_LONG
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

    def check_exit_conditions(self, user: User) -> list:
        """
        Check whether the exit conditions are met. In a breakout strategy, where the limit exit order is placed
        immediately, this will return an exit signal immediately after an order is placed, and then a wait signal from
        that point on, until that limit exit order is filled.
        :param user: The current user.
        :return: a list of signals (in this case, always of length 1).
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

        import matplotlib.pyplot as plt

        plt.figure()

        sr_zones = SRZones(market_data=data, width=self.params["breakout"]["zone_width"])
        df = data.tail(sr_zones.max_periods)

        closes = df["closeEp"].values.tolist()

        # peak_indexes = [resistance.line.coords[i][0] for i in range(len(resistance.line.coords))]
        # peak_values = [resistance.line.coords[j][1] for j in range(len(resistance.line.coords))]
        #
        # valley_indexes = [support.line.coords[k][0] for k in range(len(support.line.coords))]
        # valley_values = [support.line.coords[m][1] for m in range(len(support.line.coords))]

        plt.plot(df.index.values.tolist(), closes, color="b")
        # plt.scatter(peak_indexes, peak_values, color="g")
        # plt.scatter(valley_indexes, valley_values, color="r")

        open_timestamp = df["timestamp"].head(1).values[0]
        close_timestamp = df["timestamp"].tail(1).values[0]

        diff = close_timestamp - open_timestamp
        extended_timestamp = close_timestamp + (0.2 * diff)

        support_line = [[open_timestamp, extended_timestamp],
                        [support.line.get_value_for_timestamp(open_timestamp),
                         support.line.get_value_for_timestamp(extended_timestamp)]]

        resistance_line = [[open_timestamp, extended_timestamp],
                           [resistance.line.get_value_for_timestamp(open_timestamp),
                            resistance.line.get_value_for_timestamp(extended_timestamp)]]

        plt.plot(support_line[0], support_line[1], color="r", lw=5, alpha=0.2)
        plt.plot(support_line[0], support_line[1], color="r")
        plt.plot(resistance_line[0], resistance_line[1], color="g", lw=5, alpha=0.2)
        plt.plot(resistance_line[0], resistance_line[1], color="g")

        plt.savefig("fig.png", dpi=150)
        plt.close()
