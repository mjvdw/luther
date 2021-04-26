import pandas as pd
from tapy import Indicators
from core.utils.fractals import fractal_indicator

from .strategy import Strategy


class BreakoutStrategy(Strategy):

    def __init__(self, params: dict):
        """
        A more complex "Breakout" strategy. It isn't possible to conveniently specify the conditions for a breakout
        strategy the same as for a simpler scalping strategy, so the logic is more hardcoded. However, wherever possible
        it pulls parameters from the user-provided file.

        :param params:
        """
        super().__init__(params)

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
        """

        This function uses the tapy library. See docs here: https://pandastechindicators.readthedocs.io/en/latest/
        Also see: https://stackoverflow.com/questions/8587047/support-resistance-algorithm-technical-analysis

        :param data:
        :return:
        """

        # Calculate fractals (bullish and bearish reversals)

        # tapy requires columns named "High" and "Low" to calculate fractals.
        data["High"] = data["highEp"]
        data["Low"] = data["lowEp"]

        # Use tapy to calculate fractals.
        indicators = Indicators(data)
        indicators.fractals(column_name_high='fractals_high', column_name_low='fractals_low')
        fractals_df = indicators.df

        # TODO: Group the fractals around support and resistance zones. Do this by finding the two most recent zones, \
        #  and mark the highest as resistance and the lowest as support. The more touches each zone gets, the greater \
        #  the confidence for the trade.

        high_prices = fractals_df.loc[fractals_df["fractals_high"]]["High"]
        low_prices = fractals_df.loc[fractals_df["fractals_low"]]["Low"]

        last_resistance_price = high_prices.tail(1).values[0]
        last_support_price = low_prices.tail(1).values[0]

        # TODO: Test whether the current price falls above or below the relevant zone, returning an entry signal if it \
        #  does. Look into whether there are any other indicators I can also use to help verify a breakout.

        results = []

        return results

    @staticmethod
    def get_fractals(data: pd.DataFrame) -> pd.DataFrame:
        # This one might still work...
        # d = fractal_indicator(data)
        # return d

        indicators = Indicators(data)
        indicators.fractals(column_name_high='fractals_high', column_name_low='fractals_low')
        fractals_df = indicators.df
        return fractals_df
