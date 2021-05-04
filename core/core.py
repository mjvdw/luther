#!/usr/bin/env python3

import time
import pandas as pd

from .classes.database import Database
from .classes.order.new_order import NewOrder
from .classes.signal import Signal
from .classes.strategy.strategy import Strategy
from .classes.user import User
from .classes.websocketconnection import WebsocketConnection
from .classes.slack import Slack
from .classes.state import State
from .classes.phemex import Phemex


def run(strategy):
    """
    Primary script logic. Begins by connecting to the live data stream. That websockets function then sends off the
    messages it receives to the remainder of the script to handle each time, until the connection is closed. It then
    comes back to this functions to tidy up and close out any remaining program logic.

    """

    State.reset()

    ws_connection = WebsocketConnection(strategy=strategy,
                                        handler=trade_logic,
                                        enable_trace=False)
    ws_connection.run()


def trade_logic(strategy: Strategy) -> None:
    """
    For each message received via websockets in the main run function, perform trade logic to determine whether there
    is a long, short, exit or wait signal. If there is a long, short or exit signal (anything other than wait) then
    execute a trade using the given strategy.

    :param strategy: Strategy object generated in main function from JSON file, containing details about the user's
    preferred trading strategy.

    """
    market_data = pd.read_csv(Database.MARKET_DATA_PATH, index_col=0)

    if not market_data.empty:
        # Check whether market_data DataFrame actually contains data, to avoid errors down the track.
        # This will filter out the ping-pong messages and initial set up messages received by the Phemex API.
        user = User(strategy)
        signal = Signal(data=market_data, strategy=strategy, user=user)

        print(signal.signal)

        simulate_trading(market_data, signal, strategy, user)

        if signal.action != Signal.WAIT and not user.is_unfilled_orders:
            order = NewOrder(data=market_data, signal=signal, strategy=strategy, user=user)
            # order.send()
        elif signal.action == Signal.WAIT and user.is_unfilled_orders and not user.is_open_positions:
            current_time = time.time()
            last_order_time = user.unfilled_order.action_time/1000000000  # Convert from nanoseconds to seconds.
            time_since_order = current_time - last_order_time

            if time_since_order > strategy.entry_patience:
                # Slack().send(f"Waited {int(time_since_order)} seconds. Cancelling order.")
                client = user.connect()
                client.cancel_all_normal_orders(strategy.symbol)


def simulate_trading(market_data, signal, strategy, user):
    state = State()

    # Notify if signal changes.
    # if state.last_signal != signal.action:
    #     Slack().send(f"Signal received: {signal.action}, with confidence {signal.confidence}")
    #     state.last_signal = signal.action

    # If signal is not WAIT, prepare and send an order.
    if signal.action != Signal.WAIT and not state.existing_position and signal.action == Signal.ENTER_LONG or \
            signal.action == Signal.ENTER_SHORT:
        order = NewOrder(data=market_data, signal=signal, strategy=strategy, user=user)

        size = order.order_params["orderQty"]
        side = 'long' if signal.action == Signal.ENTER_LONG else 'short'
        side_multiplier = -1 if order.order_params["side"] == "Sell" else 1

        take_profit_price = order.order_params["priceEp"] * (1 + (side_multiplier * float(strategy.conditions["exit"]
                                                                                          ["take_profit"])))
        take_profit_price = take_profit_price / Phemex.SCALE_EP_BTCUSD
        stop_loss_price = order.order_params["priceEp"] * (1 + (side_multiplier * float(strategy.conditions["exit"]
                                                                                        ["stop_loss"])))
        stop_loss_price = stop_loss_price / Phemex.SCALE_EP_BTCUSD

        Slack().send(f"Entered {side} position of size {size} at US${order.entry_price:,.2f}, with a target price of "
                     f"US${take_profit_price:,.2f} and stop loss of US${stop_loss_price:,.2f}.")

        state.existing_position = order.order_params

    # If there is a position open, let user know when it exits.
    if state.existing_position:
        position = state.existing_position
        current_price = market_data["closeEp"].tail(1).values[0]
        side_multiplier = -1 if signal.action == position["side"] == "Sell" else 1
        take_profit_price = position["priceEp"] * (1 + (side_multiplier * float(strategy.conditions["exit"]
                                                                                ["take_profit"])))
        stop_loss_price = position["priceEp"] * (1 + (side_multiplier * float(strategy.conditions["exit"]
                                                                              ["stop_loss"])))

        take_profit = ((current_price - take_profit_price) * side_multiplier) >= 0
        stop_loss = ((stop_loss_price - current_price) * side_multiplier) >= 0

        if take_profit:
            profit = ((current_price - position["priceEp"])/current_price) * side_multiplier * 100
            scaled_current_price = current_price/Phemex.SCALE_EP_BTCUSD
            Slack().send(f"Exited position at US${scaled_current_price:,.2f} for a profit of {profit:.2f}%")
            state.existing_position = None
        elif stop_loss:
            loss = ((position["stopLossEp"] - current_price)/current_price) * side_multiplier * 100
            scaled_current_price = current_price / Phemex.SCALE_EP_BTCUSD
            Slack().send(f"Exited position at US${scaled_current_price:,.2f} for a loss of {loss:.2f}%")
            state.existing_position = None
