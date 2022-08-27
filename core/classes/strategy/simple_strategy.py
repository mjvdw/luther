import pandas as pd

from .strategy import Strategy
from ..signal import Signal
from ..user import User


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
                left = data[param[0]].tail(1).values[0] if type(
                    param[0]) == str else param[0]
                right = data[param[1]].tail(1).values[0] if type(
                    param[1]) == str else param[1]

                # Comparison expression string to be evaluated.
                expression = str(left) + param[2] + str(right)
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

    def check_exit_conditions(self, data: pd.DataFrame, user: User) -> list:
        """
        Iterate through each condition as provided by the user and check whether the current market data meets all of
        those condition.

        :param data: Market data.
        :param user: The current open position as a Position object.
        :return: A list containing the exit signal if applicable.
        """
        condition = self.conditions["exit"]
        signals = []
        results = []

        position = user.open_position

        if user.is_open_positions and not user.is_unfilled_orders:
            results.append(True)
            action = Signal.SET_EXIT_LIMIT
        elif position.net_pnl <= condition["stop_loss"]:
            client = user.connect()
            client.cancel_all_normal_orders(self.symbol)
            action = Signal.EXIT
            results.append(True)
        else:
            action = Signal.EXIT
            for indicator in condition["indicators"]:
                # Test each parameter within one set of conditions.
                side_key = "long_exit_limit" if position.side == "Buy" else "short_exit_limit"
                param = indicator[side_key]

                left = data[param[0]].tail(1).values[0] if type(
                    param[0]) == str else param[0]
                right = data[param[1]].tail(1).values[0] if type(
                    param[1]) == str else param[1]
                compare_operator = param[2]

                condition_str = str(left) + str(compare_operator) + str(right)
                if eval(condition_str):
                    results.append(True)

        if any(results):
            signal = {
                "action": action,
                "confidence": 1,
                "strategy_type": self.strategy_type
            }
            signals.append(signal)

        return signals
