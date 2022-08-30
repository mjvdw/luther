from random import random, seed
import pandas as pd

from .strategy import Strategy
from ..signal import Signal
from ..user import User


class RandomStrategy(Strategy):
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

        coinflip = int(random() * 1e12)
        print(coinflip)
        print(self.conditions["enter"][0]["confidence"])

        if coinflip % 2 == 0:
            signal = {
                "action": "ENTER_LONG",
                "confidence": self.conditions["enter"][0]["confidence"],
                "strategy_type": self.strategy_type
            }
            signals.append(signal)
        else:
            signal = {
                "action": "ENTER_SHORT",
                "confidence": self.conditions["enter"][1]["confidence"],
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

        return []
