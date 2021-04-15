#!/usr/bin/env python3

import pandas as pd
import time

from .classes.websocketconnection import WebsocketConnection
from .classes.database import Database
from .classes.signal import Signal
from core.classes.strategy.strategy import Strategy
from .classes.user import User
from core.classes.order.new_order import NewOrder
from .classes.slack import Slack


def run(strategy):
    """
    Primary script logic. Begins by connecting to the live data stream. That websockets function then sends off the
    messages it receives to the remainder of the script to handle each time, until the connection is closed. It then
    comes back to this functions to tidy up and close out any remaining program logic.

    """

    ws_connection = WebsocketConnection(strategy=strategy,
                                        handler=trade_logic,
                                        enable_trace=False)
    ws_connection.run()

    # TODO: Include any closing tidy up logic.


def trade_logic(strategy: Strategy) -> None:
    """
    For each message received via websockets in the main run function, perform trade logic to determine whether there
    is a long, short, exit or wait signal. If there is a long, short or exit signal (anything other than wait) then
    execute a trade using the given strategy.

    :type strategy: Strategy object generated in main function from JSON file, containing details about the user's
    preferred trading strategy.

    """
    market_data = pd.read_csv(Database.MARKET_DATA_PATH, index_col=0)

    if not market_data.empty:
        # Check whether market_data DataFrame actually contains data, to avoid errors down the track.
        # This will filter out the ping-pong messages and initial set up messages received by the Phemex API.
        user = User(strategy)
        signal = Signal(data=market_data, strategy=strategy, user=user)

        print(signal.signal)

        if signal.action != Signal.WAIT and not user.is_unfilled_orders:
            Slack().send(f"Signal received: {signal.action}, with confidence {signal.confidence}")
            order = NewOrder(data=market_data, signal=signal, strategy=strategy, user=user)
            order.send()
        elif signal.action == Signal.WAIT and user.is_unfilled_orders and not user.is_open_positions:
            current_time = time.time()
            last_order_time = user.unfilled_order.action_time/1000000000  # Convert from nanoseconds to seconds.
            time_since_order = current_time - last_order_time

            if time_since_order > strategy.entry_patience:
                Slack().send(f"Waited {int(time_since_order)} seconds. Cancelling order.")
                client = user.connect()
                client.cancel_all_normal_orders(strategy.symbol)
