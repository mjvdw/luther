#!/usr/bin/env python3

from .position import Position

import numpy as np
import pandas as pd


class Strategy(object):
    def __init__(self, params):
        """
        Generate useful properties by converting strategy JSON file into usable properties.
        :param params: A dictionary containing strategy parameters.
        """
        self.params = params

    @property
    def websocket_query(self) -> dict:
        """
        Generate query using strategy data in line with Phemex API documentation.
        See: https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md

        :return: Dictionary formatted correctly and containing everything required by Phemex websocket API.
        """

        query = {
            "method": "kline.subscribe",
            "params": [self.params["klines"]["symbol"], self.params["klines"]["period"]],
            "id": int(np.random.randint(1e15, 1e16, 1)[0])
        }

        return query

    @property
    def indicators(self) -> list:
        """
        The indicators to be used by this strategy, for entry and exit calculations.

        :return: A list containing the indicators and relevant parameters to calculate each using pandas_ta module.
        """
        indicators = self.params["indicators"]
        return indicators

    @property
    def conditions(self) -> dict:
        """
        The conditions under which the script will send an entry or exit order.

        :return: A dictionary with the relevant condition parameters.
        """
        conditions = self.params["conditions"]
        return conditions

    @property
    def symbol(self) -> str:
        """
        The symbol representing the currency pair this strategy relates to. Eg. BTCUSD.

        :return: A string representing the currency paid. Eg. BTCUSD.
        """
        symbol = self.params["symbol"]
        return symbol

    @property
    def currency(self) -> str:
        """
        The currency being trading in. Eg. BTC or USD.

        :return: A string representing the currency being traded by the strategy. Eg. BTC or USD.
        """
        currency = self.params["currency"]
        return currency

    @property
    def strategy_type(self) -> str:
        """
        A user-provided name identifying what type of strategy the parameters relate to.

        :return: The name given to this strategy, as a string.
        """
        strategy_type = self.params["type"]
        return strategy_type

    @property
    def order_entry_params(self) -> dict:
        """
        Order parameters provided by the user for entering into a position.

        :return: Dictionary containing the order parameters that cannot be automatically calculated or assumed.
        """
        order_entry_params = self.params["order_params"]["entry"]
        return order_entry_params

    @property
    def order_exit_params(self) -> dict:
        """
        Order parameters provided by the user for exiting a position.

        :return: Dictionary containing the order parameters that cannot be automatically calculated or assumed.
        """
        order_exit_params = self.params["order_params"]["exit"]
        return order_exit_params

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
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
        condition = self.conditions["exit"]
        exit_condition = False
        signals = []

        if position.net_pnl >= condition["take_profit"] or position.net_pnl <= condition["stop_loss"]:
            exit_condition = True
        else:
            for indicator in condition["indicators"]:
                key = indicator["key"]
                value = data[key].tail(1).values[0]
                limit = indicator["short_exit_limit"] if position.side == "Sell" \
                    else indicator["long_exit_limit"]
                condition_str = str(value) + str(limit[1]) + str(limit[0])
                if eval(condition_str):
                    exit_condition = True

        if exit_condition:
            signal = {
                "action": condition["action"],
                "confidence": 1,
                "strategy_type": self.strategy_type
            }
            signals.append(signal)

        return signals
