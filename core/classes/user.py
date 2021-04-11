import os

from .phemex import Client
from .phemex import PhemexAPIException
from .strategy import Strategy
from .position import Position


class User(object):

    TEST_NET: bool = True

    def __init__(self, strategy: Strategy):
        """
        An object representing the user, and providing utility methods to access information about the user's open
        trades, positions or wallet balances, and allowing the script to send data to open new trades or positions.
        """
        self.strategy = strategy

    @property
    def open_positions(self) -> list:
        """
        Check whether there is an open position currently trading. If there is, return the position details wrapped
        in a Position object. Raise an error if there are none.

        :return: A Position object containing details about the current open position.
        """

        client = User.connect()
        positions = []

        if self._is_open_positions(client):
            all_open_positions = client.query_account_n_positions(self.strategy.currency)["data"]["positions"]
            for position_details in all_open_positions:
                position = Position(position_details)
                positions.append(position)
        else:
            raise PhemexAPIException("No open positions.")

        return positions

    @classmethod
    def connect(cls) -> Client:
        """
        Utility function providing a client object to connect to the Phemex API.

        :return: Client object containing functions to send and retrieve data through Phemex API.
        """
        if cls.TEST_NET:
            api_id = os.environ.get('TEST_PHEMEX_API_ID')
            api_secret = os.environ.get('TEST_PHEMEX_API_SECRET')
            test_net = True
        else:
            api_id = os.environ.get('PHEMEX_API_ID')
            api_secret = os.environ.get('PHEMEX_API_SECRET')
            test_net = False

        client = Client(api_id, api_secret, test_net)

        return client

    def is_trading(self) -> bool:
        """
        Determine whether the user is trading by checking whether there are any open orders or positions.

        :return: A boolean representing whether the user is trading.
        """

        client = User.connect()
        is_trading = self._is_open_positions(client) or self._is_unfilled_orders(client)

        return is_trading

    def _is_open_positions(self, client: Client) -> bool:
        """
        Query the users account for any open positions. The Phemex API returns an empty position if there are none,
        so test for whether that position's size is 0.

        :param client: An object representing the connection to Phemex API.
        :return: A boolean representing whether there are any open positions.
        """
        num_positions = 0
        try:
            open_positions = client.query_account_n_positions(self.strategy.currency)["data"]["positions"]
            for position in open_positions:
                if position["size"] > 0:
                    num_positions += 1
            is_open_positions = num_positions > 0
        except PhemexAPIException:
            is_open_positions = False

        return is_open_positions

    def _is_unfilled_orders(self, client: Client) -> bool:
        """
        Query whether there are any unfilled orders. The Phemex API returns an error if there are none, so set to
        return False if there is a PhemexAPIException.

        :param client: An object representing the connection to Phemex API.
        :return: A boolean representing whether there are any open unfilled orders.
        """
        num_unfilled_orders = 0
        try:
            open_orders = client.query_open_orders(self.strategy.symbol)["data"]["rows"]
            for order in open_orders:
                if order["ordStatus"] == Client.ORDER_STATUS_NEW:
                    num_unfilled_orders += 1
            is_unfilled_orders = num_unfilled_orders > 0
        except PhemexAPIException:
            is_unfilled_orders = False

        return is_unfilled_orders
