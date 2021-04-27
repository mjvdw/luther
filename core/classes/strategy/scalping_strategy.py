import pandas as pd

from core.classes.strategy.strategy import Strategy
from core.classes.phemex import Phemex
from core.classes.phemex import PhemexAPIException
from core.classes.signal import Signal
from core.classes.user import User


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

    def check_exit_conditions(self, data: pd.DataFrame, user: User) -> list:
        """
        As this is a scalping strategy, this should always return True straight away. For consistency with other
        strategies, return a list of boolean values.

        :param data: Market data.
        :param user: The current open position as a Position object.
        :return: A list containing the exit signal if applicable.
        """

        condition = self.conditions["exit"]
        signals = []

        position = user.open_position

        client = User.connect()
        exit_distance = self._get_current_exit_distance(client, data)

        if exit_distance > (2 * super().order_exit_params["limit_margin_ep"]) and exit_distance != 0:
            client.cancel_all_normal_orders(super().symbol)
            action = Signal.EXIT
        elif user.is_open_positions and not user.is_unfilled_orders:
            action = Signal.EXIT
        else:
            action = Signal.WAIT

        signal = {
            "action": action,
            "confidence": 1,
            "strategy_type": self.strategy_type
        }
        signals.append(signal)

        return signals

    def _get_current_exit_distance(self, client: Phemex, data: pd.DataFrame):
        """

        :param client:
        :param data:
        :return: An integer representing the EP scaled value of the distance between the current price and the price
        at which the relevant order was entered.
        """

        orders = []
        current_price = data["closeEp"].tail(1).values[0]

        try:
            unfilled_orders = client.query_open_orders(super().symbol)["data"]["rows"]
            for unfilled_order in unfilled_orders:
                if unfilled_order["orderType"] == "Limit":
                    orders.append(unfilled_order)

            if len(orders) == 1:
                distance = abs(orders[0]["priceEp"] - current_price)
            else:
                distance = 0
            exit_distance = distance
        except PhemexAPIException as error:
            exit_distance = 0

        return exit_distance
