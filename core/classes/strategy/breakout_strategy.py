import pandas as pd
from tapy import Indicators

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
        :param data:
        :return:
        """

        # Calculate fractals (bullish and bearish reversals)

        # tapy requires columns named "High" and "Low" to calculate fractals.
        data["High"] = data["highEp"]
        data["Low"] = data["lowEp"]

        # Use tapy to calculate fractals.
        indicators = Indicators(data)
        indicators.fractals()  # indicators is a DataFrame containing the fractals data as boolean values for each row.

        # TODO: Group the fractals around support and resistance zones. Do this by finding the two most recent zones, \
        #  and mark the highest as resistance and the lowest as support. The more touches each zone gets, the greater \
        #  the confidence for the trade.

        # TODO: Test whether the current price falls above or below the relevant zone, returning an entry signal if it \
        #  does. Look into whether there are any other indicators I can also use to help verify a breakout.

        results = []

        return results
