#!/usr/bin/env python3

import json
import logging
import threading
import time

import numpy as np
import pandas as pd
import websocket

from typing import Callable
from .strategy import Strategy
from .market import Market


class WebsocketConnection(object):

    def __init__(self,
                 strategy: Strategy,
                 handler: Callable[[Strategy], None],
                 test_net: bool = False,
                 enable_trace: bool = False) -> None:
        """
        Provides some abstraction for connection to the websocket stream for market data via the Phemex API.
        Uses the websocket_client module to subscribe to the stream and handle each message.

        See: https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#wsapi

        :param strategy: A strategy object representing the user input trading strategy, used primarily in this class
            to specify the query object per the Phemex API specifications.
        :param handler: A function that will receive and handle the message from the websocket connection.
        :type test_net: Phemex offers a test API. Specify True if you want to connect to the test API. Otherwise,
            default is False.
        :type enable_trace: Specify whether to turn on debug logging in the terminal for the websocket connection.
        """

        self.strategy = strategy
        self.handler = handler
        self.test_net = test_net
        self.enable_trace = enable_trace

    def run(self) -> None:
        """
        Primary websocket connection set up. Responsible for sending the user query to the server and directing the
        message to the approach handler function within the class. Also contains a regular ping query, which is sent
        every 5 seconds. This is required by the Phemex API.

        """

        def on_message(ws, message):
            self._handle_message_data(message)
            self.handler(self.strategy)

        def on_error(ws, error):
            logging.error(error)

        def on_close(ws):
            ws.close()
            logging.debug("thread terminating...")
            logging.debug("### closed ###")

        def on_open(ws):
            def market_data():
                ws.send(json.dumps(self.strategy.websocket_query))

            def ping():
                while True:
                    ws.send(json.dumps({
                        "id": int(np.random.randint(1e15, 1e16, 1)[0]),
                        "method": "server.ping",
                        "params": []
                    }))
                    time.sleep(5)

            market_data_thread = threading.Thread(target=market_data)
            ping_thread = threading.Thread(target=ping)
            market_data_thread.start()
            ping_thread.start()

        def subscribe():
            websocket.enableTrace(self.enable_trace)
            url = "wss://testnet.phemex.com/ws" if self.test_net else "wss://phemex.com/ws"
            ws = websocket.WebSocketApp(url,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.on_open = on_open
            ws.run_forever()

        subscribe()

    def _handle_message_data(self, message: str) -> None:
        """
        Filter the messages received from the websocket server and save only the useful and relevant market data to a
        pandas DataFrame and then to a CSV that can be read at any time by other functions in the script. Intention
        here is to be somewhat stateful, to save having to pass the data through lots of other functions.

        :param message: Message received from websocket server.

        """

        raw_data = json.loads(message)
        market_data = []
        index = []

        try:
            data_type = raw_data["type"]
        except KeyError:
            return None

        if data_type == "snapshot" or data_type == "incremental":
            for a in raw_data["kline"]:
                kline = {
                    "timestamp": a[0],
                    "interval": a[1],
                    "lastCloseEp": a[2],
                    "openEp": a[3],
                    "highEp": a[4],
                    "lowEp": a[5],
                    "closeEp": a[6],
                    "volume": a[7],
                    "turnoverEv": a[8]
                }
                market_data.append(kline)
                index.append(kline["timestamp"])

        # Using .reverse() method because snapshot is received from most recent
        # to least recent, but it needs to be the other way for most indicator
        # calculations, like RSI.
        market_data.reverse()
        index.reverse()

        df = pd.DataFrame(data=market_data, index=index)

        if data_type == "incremental":
            prev_df = pd.read_csv(Market.MARKET_DATA_PATH, index_col=0)
            prev_df.update(df)

            is_in_index = df.index.isin(prev_df.index)
            is_current_period = is_in_index[-1]
            if not is_current_period:
                df = prev_df.append(df.tail(1))
                df = df.iloc[1:]
            else:
                df = prev_df

        df.to_csv(Market.MARKET_DATA_PATH, index=True)
