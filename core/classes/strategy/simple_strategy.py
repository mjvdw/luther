import pandas as pd

from .strategy import Strategy
from ..position import Position


class SimpleStrategy(Strategy):
    def __init__(self, params: dict):
        """
        An subclass providing condition checking functions for "Simple" strategies. The conditions, being simple, are
        provided in the configuration file set by the user.

        :type params: Dictionary containing the strategy parameters set by the user.

        """
        super().__init__(params)

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
        """


        :param data:
        :return: A list containing
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

    def check_exit_conditions(self, data: pd.DataFrame, position: Position) -> list:
        """

        :param data:
        :param position:
        :return:
        """
        condition = self.conditions["exit"]
        signals = []
        results = []

        if position.net_pnl >= condition["take_profit"] or position.net_pnl <= condition["stop_loss"]:
            results.append(True)
        else:
            for indicator in condition["indicators"]:
                key = indicator["key"]
                value = data[key].tail(1).values[0]

                short_limit = indicator["short_exit_limit"]
                long_limit = indicator["long_exit_limit"]
                limit = short_limit if position.side == "Sell" else long_limit

                condition_str = str(value) + str(limit[1]) + str(limit[0])
                print(condition_str, eval(condition_str))
                if eval(condition_str):
                    results.append(True)

        if any(results):
            signal = {
                "action": condition["action"],
                "confidence": 1,
                "strategy_type": self.strategy_type
            }
            signals.append(signal)

        return signals
