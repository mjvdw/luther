import pandas as pd
from core.classes.strategy.strategy import Strategy
from core.classes.state import State
from core.classes.srzones.srzones import SRZones
from core.classes.srzones.zone import Zone


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
        # STEP 2: Check whether there are any new extrema. If there have, determine whether to update zone.
        ##
        new_support, new_resistance = self._draw_sr_zones(data)

        new_minima_outside_zone = not new_support.value_is_in_zone(new_support.value, new_support.timestamp)
        new_maxima_outside_zone = not new_resistance.value_is_in_zone(new_resistance.value, new_resistance.timestamp)

        print(new_minima_outside_zone, new_maxima_outside_zone)

    def _draw_sr_zones(self, data: pd.DataFrame) -> (Zone, Zone):
        """
        Helper function to draw new support and resistance zones.
        :param data: data required to draw the support and resistance zones.
        """
        sr_zones = SRZones(market_data=data, width=self.params["breakout"]["zone_width"])
        support = sr_zones.support_zone
        resistance = sr_zones.resistance_zone
        return support, resistance
