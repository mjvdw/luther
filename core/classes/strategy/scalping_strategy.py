import pandas as pd

from .strategy import Strategy
from ..position import Position


class ScalpingStrategy(Strategy):
    def __init__(self, params: dict):
        """
        An subclass providing condition checking functions for "Scalping" strategies. Essentially, the script will try
        to enter and exit trades as fast as possible to get the Phemex maker rebate.

        :type params: Dictionary containing the strategy parameters set by the user.

        """
        super().__init__(params)

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
        """
        Iterate through each condition as provided by the user and check whether the current market data meets all of
        those condition.

        :param data: Market Data.
        :return: A list containing all possible signals.
        """
        signals = []

        for condition in self.conditions["enter"]:
            # Test each set of conditions.
            params = condition["params"]
            results = []

            for param in params:
                # Test each parameter within one set of conditions.
                left = data[param[0]].tail(1).values[0] if type(param[0]) == str else param[0]
                right = data[param[1]].tail(1).values[0] if type(param[1]) == str else param[1]

                expression = str(left) + param[2] + str(right)  # Comparison expression string to be evaluated.
                passed = eval(expression)  # Result of evaluation.
                results.append(passed)

            if all(results):
                signal = {
                    "action": condition["action"],
                    "confidence": condition["confidence"],
                    "strategy_type": self.strategy_type
                }
                signals.append(signal)

        return signals

    def check_exit_conditions(self, data: pd.DataFrame = None, position: Position = None) -> list:
        """
        As this is a scalping strategy, this should always return True straight away. For consistency with other
        strategies, return a list of boolean values.

        :param data: Market data.
        :param position: The current open position as a Position object.
        :return: A list containing the exit signal if applicable.
        """
        condition = self.conditions["exit"]
        signals = []

        signal = {
            "action": condition["action"],
            "confidence": 1,
            "strategy_type": self.strategy_type
        }
        signals.append(signal)

        return signals
