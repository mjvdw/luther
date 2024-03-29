import uuid

import pandas as pd

from ..phemex import Phemex
from ..signal import Signal
from ..strategy.strategy import Strategy
from ..user import User


# from ..slack import Slack


class NewOrder(object):
    def __init__(self, data: pd.DataFrame, signal: Signal, strategy: Strategy, user: User):
        """
        An object representing a trade order to be sent to the Phemex API. Use to generate trade parameters in the
        format required by the Phemex API, by process the user-provided strategy.

        :param signal: A Signal object with trade side (buy/sell) and confidence (leverage) data.
        :param strategy: A Strategy object with details required for setting entry and exit parameters.
        """
        self.data = data
        self.signal = signal
        self.strategy = strategy
        self.user = user

        self.order_params = None
        self._generate_order_parameters()

    def send(self):
        """
        Send order parameters to the Phemex API and save order details to CSV via pandas module.

        """

        client = User.connect()

        # Set leverage.
        if self.signal.action != self.signal.EXIT:
            client.change_leverage(
                symbol=self.strategy.symbol, leverage=self.signal.confidence)

        # Send order parameters via Phemex API.
        r = client.place_order(self.order_params)
        # Slack().send(f"Order response: {r}")

        # TODO: Save phemex response to CSV for future reference.

    @property
    def entry_price_ep(self):
        """
        Scaled entry price for this order.
        :return: Scaled entry price for this order.
        """
        return self.order_params["priceEp"]

    @property
    def entry_price(self):
        """
        Un-scaled entry price for this order.
        :return: Un-scaled entry price for this order.
        """
        return self.entry_price_ep / Phemex.SCALE_EP

    def _generate_order_parameters(self):
        """
        Interpret the signal passed to the Order object and generate appropriate order parameters for that signal.

        """

        if self.signal.action == Signal.ENTER_LONG or self.signal.action == Signal.ENTER_SHORT:
            params = self._generate_entry_parameters()
        elif self.signal.action == Signal.EXIT or self.signal.action == Signal.SET_EXIT_LIMIT:
            params = self._generate_exit_parameters()
        else:
            raise TypeError(f"Invalid signal sent: {self.signal.action}")

        self.order_params = params

    def _generate_entry_parameters(self) -> dict:
        """
        Using the user-provided parameters, generate a dictionary representing order to enter a position in the
        appropriate format for the Phemex API.

        :return: A dictionary with the required parameters for the Phemex API.
        """

        side = "Buy" if self.signal.action == Signal.ENTER_LONG else "Sell"
        # Utility variable to convert parameters between longs/shorts.
        side_multiplier = -1 if side == "Sell" else 1

        # Convert to int because type returned by DataFrame is not JSON Serializable.
        current_price = float(self.data["closeEp"].tail(1).values[0])

        # If order type is Market, the price is irrelevant, so calculate on the assumption it will be a Limit order.
        price = current_price - \
            (side_multiplier *
             self.strategy.order_entry_params["limit_margin_ep"])

        user = User(self.strategy)
        leverage = self.signal.confidence
        # Quantity must be no more than half the wallet balance, otherwise it isn't possible to exit the order
        # by submitting an order in the opposite direction. Therefore a 0.5 multiplier is hardcoded in.
        wallet_ratio = self.strategy.order_entry_params["wallet_ratio"]

        value = user.wallet_balance * wallet_ratio * 0.5 * leverage

        if self.strategy.currency == "BTC":
            # Because trading in BTC to USD. Value is always USD.
            quantity = value * (current_price / Phemex.SCALE_EP)
        else:
            # Because trading in USD to coin. Value is always USD.
            quantity = value / (current_price / Phemex.SCALE_EP)

        quantity = int(quantity / self.strategy.contract_size)

        ord_type = self.strategy.order_entry_params["ord_type"]
        time_in_force = "PostOnly" if ord_type == "Limit" else "GoodTillCancel"

        tp = self.strategy.order_entry_params["safety_tp"]
        sl = self.strategy.order_entry_params["safety_sl"]

        take_profit = (1 + (tp * side_multiplier)) * \
            current_price if tp else None
        stop_loss = (1 - (sl * side_multiplier)) * \
            current_price if sl else None

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
        # Utility variable to convert parameters between longs/shorts.
        side_multiplier = -1 if side == "Sell" else 1

        # Convert to int because type returned by DataFrame is not JSON Serializable.
        current_price = int(self.data["closeEp"].tail(1).values[0])

        # If order type is Market, the price is irrelevant, so calculate on the assumption it will be a Limit order.
        if self.strategy.strategy_type == Strategy.SCALPING_STRATEGY:
            # Ensures that the limit order is always a sufficient distance from current price to be accepted.
            if position.side == "Sell":
                relative_price = position.entry_price if current_price >= position.entry_price else current_price
            else:
                relative_price = position.entry_price if current_price <= position.entry_price else current_price
        else:
            relative_price = current_price

        if self.signal.action == Signal.SET_EXIT_LIMIT:
            price = relative_price - (relative_price * side_multiplier *
                                      self.strategy.order_exit_params["auto_take_profit"])
        else:
            price = relative_price - \
                (side_multiplier *
                 self.strategy.order_exit_params["limit_margin_ep"])

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
            "reduceOnly": True,
            "triggerType": "ByLastPrice",
            "timeInForce": time_in_force,
            "takeProfitEp": 0,
            "stopLossEp": 0,
            "pegOffsetValueEp": 0,
            "pegPriceType": "UNSPECIFIED"
        }

        return params
