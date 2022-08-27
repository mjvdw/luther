#!/usr/bin/env python3

import json
import os

from core.classes.slack import Slack
from core.classes.strategy.breakout_strategy import BreakoutStrategy
from core.classes.strategy.scalping_strategy import ScalpingStrategy
from core.classes.strategy.simple_strategy import SimpleStrategy
from core.classes.strategy.strategy import Strategy
from core.core import run

if __name__ == "__main__":
    try:
        strategy_file = os.path.join(os.path.dirname(
            __file__), 'config/scalping_strategy.json')
        # strategy_file = os.path.join(os.path.dirname(__file__), 'config/simple_strategy_v004.json')
        # strategy_file = os.path.join(os.path.dirname(__file__), 'config/breakout_strategy.json')

        with open(strategy_file, "r") as json_file:
            strategy_params = json.load(json_file)
            strategy_type = strategy_params["type"]

            # Generate subclass Strategy object based on user provided JSON file, depending on strategy type.
            if strategy_type == Strategy.SIMPLE_STRATEGY:
                strategy = SimpleStrategy(strategy_params)
            elif strategy_type == Strategy.BREAKOUT_STRATEGY:
                strategy = BreakoutStrategy(strategy_params)
            elif strategy_type == Strategy.SCALPING_STRATEGY:
                strategy = ScalpingStrategy(strategy_params)
            else:
                raise TypeError(f"Invalid strategy type: {strategy_type}")

            Slack().send("#####################################")
            Slack().send(f"Starting {strategy_type} strategy...")
            run(strategy)  # Use strategy object to execute trading strategy.
    except Exception as e:
        Slack().send(f"<!channel> Error: {e}")
