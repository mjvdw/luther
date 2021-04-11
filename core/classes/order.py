import pandas as pd
import uuid

from .strategy import Strategy
from .signal import Signal
from .user import User


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

        self._order_params = None
        self._generate_order_parameters()

    def send(self):
        """
        Send order parameters to the Phemex API and save order details to CSV via pandas module.

        """

        print(self._order_params)

        # TODO: Set leverage.
        # TODO: Send order parameters via Phemex API.
        # TODO: Save phemex response to CSV for future reference.

    def _generate_order_parameters(self):
        """
        Interpret the signal passed to the Order object and generate appropriate order parameters for that signal.

        """

        if self.signal.action == Signal.ENTER_LONG or self.signal.action == Signal.ENTER_SHORT:
            params = self._generate_entry_parameters()
        elif self.signal.action == Signal.EXIT:
            params = self._generate_exit_parameters()
        else:
            raise TypeError(f"Invalid signal sent: {self.signal.action}")

        self._order_params = params

    def _generate_entry_parameters(self) -> dict:
        """
        Using the user-provided parameters, generate a dictionary representing order to enter a position in the
        appropriate format for the Phemex API.

        :return: A dictionary with the required parameters for the Phemex API.
        """

        side = "Buy" if self.signal.action == Signal.ENTER_LONG else "Sell"
        side_multiplier = -1 if side == "Sell" else 1  # Utility variable to convert parameters between longs/shorts.

        current_price = self.data["closeEp"].tail(1).values[0]
        # If order type is Market, the price is irrelevant, so calculate on the assumption it will be a Limit order.
        price = current_price - (side_multiplier * self.strategy.order_entry_params["limit_margin_ep"])

        user = User(self.strategy)
        leverage = self.signal.confidence
        # Quantity must be no more than half the wallet balance, otherwise it isn't possible to exit the order
        # by submitting an order in the opposite direction. Therefore a 0.5 multiplier is hardcoded in.
        quantity = user.wallet_balance * self.strategy.order_entry_params["wallet_ratio"] * 0.5 * leverage

        ord_type = self.strategy.order_entry_params["ord_type"]
        time_in_force = "PostOnly" if ord_type == "Limit" else "GoodTillCancel"

        take_profit = (1 + (self.strategy.order_entry_params["safety_tp"] * side_multiplier)) * current_price
        stop_loss = (1 - (self.strategy.order_entry_params["safety_sl"] * side_multiplier)) * current_price

        params = {
            "actionBy": "FromOrderPlacement",
            "symbol": self.strategy.symbol,
            "clOrdID": str(uuid.uuid4()),
            "side": side,
            "priceEp": price,
            "orderQty": quantity,
            "ordType": ord_type,
            "reduceOnly": False,
            "triggerType": "ByLastPrice",
            "timeInForce": time_in_force,
            "takeProfitEp": take_profit,
            "stopLossEp": stop_loss,
            "pegOffsetValueEp": 0,
            "pegPriceType": "UNSPECIFIED"
        }

        return params

    def _generate_exit_parameters(self) -> dict:
        """
        Using the user-provided parameters, generate a dictionary representing order to exit a position in the
        appropriate format for the Phemex API.

        :return: A dictionary with the required parameters for the Phemex API.
        """

        user = User(self.strategy)
        position = user.open_position

        side = "Buy" if position.side == "Sell" else "Sell"
        side_multiplier = -1 if side == "Sell" else 1  # Utility variable to convert parameters between longs/shorts.

        current_price = self.data["closeEp"].tail(1).values[0]
        # If order type is Market, the price is irrelevant, so calculate on the assumption it will be a Limit order.
        price = current_price - (side_multiplier * self.strategy.order_exit_params["limit_margin_ep"])

        ord_type = self.strategy.order_exit_params["ord_type"]
        time_in_force = "PostOnly" if ord_type == "Limit" else "GoodTillCancel"

        params = {
            "actionBy": "FromOrderPlacement",
            "symbol": self.strategy.symbol,
            "clOrdID": str(uuid.uuid4()),
            "side": side,
            "priceEp": price,
            "orderQty": position.size,
            "ordType": ord_type,
            "reduceOnly": False,
            "triggerType": "ByLastPrice",
            "timeInForce": time_in_force,
            "takeProfitEp": 0,
            "stopLossEp": 0,
            "pegOffsetValueEp": 0,
            "pegPriceType": "UNSPECIFIED"
        }

        return params
