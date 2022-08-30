#!/usr/bin/env python3

import numpy as np


class Strategy(object):

    SIMPLE_STRATEGY = "SIMPLE"
    BREAKOUT_STRATEGY = "BREAKOUT"
    SCALPING_STRATEGY = "SCALPING"
    RANDOM_STRATEGY = "RANDOM"

    def __init__(self, params: dict):
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

    @property
    def entry_patience(self) -> int:
        entry_patience = self.params["order_params"]["entry"]["entry_patience"]
        return entry_patience

    @property
    def contract_size(self) -> int:
        contract_size = self.params["contract_size"]
        return contract_size
