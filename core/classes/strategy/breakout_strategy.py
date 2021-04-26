import pandas as pd
from core.classes.strategy.strategy import Strategy
from core.classes.state import State
from core.classes.srzones.srzones import SRZones


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

        state = State()

        sr_zones = SRZones(market_data=data, width=self.params["breakout"]["zone_width"])
        support = sr_zones.support_zone
        resistance = sr_zones.resistance_zone

        state.support = support
        state.resistance = resistance
