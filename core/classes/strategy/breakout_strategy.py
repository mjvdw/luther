import pandas as pd

from .strategy import Strategy


class BreakoutStrategy(Strategy):

    def __init__(self, params: dict):
        """

        :param params:
        """
        super().__init__(params)

    def check_entry_conditions(self, data: pd.DataFrame) -> list:
        """

        :param data:
        :return:
        """

        results = []

        return results
