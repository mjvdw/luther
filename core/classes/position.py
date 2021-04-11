import pandas as pd
from .market import Market
from .phemex import Phemex


class Position(object):
    def __init__(self, position_details: dict):
        """
        An object representing an open position on the Phemex trading platform. Contains details about the trade, and
        using the clOrdId can link to database with exit parameters.

        :param position_details:
        """
        self.position_details = position_details

        self._market_data = pd.read_csv(Market.MARKET_DATA_PATH, index_col=0)

    @property
    def entry_price(self) -> int:
        """
        The price at which this position was entered. Often used to calculate whether the position is profitable.

        :return: The scaled entry price for the position.
        """
        price = self.position_details["avgEntryPriceEp"]
        return price

    @property
    def size(self) -> int:
        """
        The size of the position, measured in the number of contracts (aligning to the other side of the currency pair).
        For example, in the BTCUSD currency pair, 100 "contracts", is the equivalent of US$100 of BTC.

        :return: The size of the position, measured in the number of contracts, equivalent to the number of US dollars.
        """
        size = self.position_details["size"]
        return size

    @property
    def side(self) -> str:
        """
        A string showing whether the position is long ("Buy") or short ("Sell).

        :return: String with value either "Buy" or "Sell" representing whether the position is long or short.
        """
        side = self.position_details["side"]
        return side

    @property
    def gross_pnl(self) -> float:
        """
        Get the current profit and loss for the position by reference to the current close price, before fees.

        :return: A number representing the profit or loss of the current position (percent, before multiply by 100)
        before fees.
        """

        current_price = self._market_data["closeEp"].tail(1).values[0]
        price_change = current_price - self.entry_price
        side_multiplier = -1 if self.side == "Sell" else 1  # Convert negative values to positive for shorts.
        gross_pnl = (price_change / self.entry_price) * side_multiplier

        return gross_pnl

    @property
    def net_pnl(self) -> float:
        """

        :return:
        """

        # TODO: Accurately determine the appropriate fee. Currently assuming the worst case scenario, which is when
        #  script triggers market buy (and taker fee).

        net_pnl = self.gross_pnl - (Phemex.TAKER_FEE * 2)

        return net_pnl

    @property
    def net_pnl_btc(self) -> float:
        """
        A property showing the predicted profit or loss in Bitcoin

        :return: A number to 8 decimal paces, representing the expected change in Bitcoin balance in users wallet if
        trade were to close at the time this method is called.
        """

        current_price = self._market_data["closeEp"].tail(1).values[0]
        net_pnl_usd = self.net_pnl * self.size
        net_pnl_btc = net_pnl_usd / (current_price / Phemex.SCALE_EP_BTCUSD)

        return net_pnl_btc
