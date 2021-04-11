#!/usr/bin/env python3

import json
import numpy as np


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
        indicators = self.params["indicators"]
        return indicators

    @property
    def conditions(self) -> dict:
        conditions = self.params["conditions"]
        return conditions

    @property
    def symbol(self) -> str:
        symbol = self.params["symbol"]
        return symbol

    @property
    def currency(self) -> str:
        currency = self.params["currency"]
        return currency

    @property
    def strategy_type(self) -> str:
        strategy_type = self.params["type"]
        return strategy_type
