import pandas as pd

from .strategy import Strategy
from .signal import Signal


class Order(object):
    def __init__(self, data: pd.DataFrame, signal: Signal, strategy: Strategy):
        """
        An object representing a trade order to be sent to the Phemex API. Use to generate trade parameters in the
        format required by the Phemex API, by process the user-provided strategy.

        :param signal: A Signal object with trade side (buy/sell) and confidence (leverage) data.
        :param strategy: A Strategy object with details required for setting entry and exit parameters.
        """
        self.data = data
        self.signal = signal
        self.strategy = strategy

    def send(self):
        """
        Send order parameters to the Phemex API and save order details to CSV.

        """
        pass
