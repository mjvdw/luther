#!/usr/bin/env python3

import os
import json

from core.core import run
from core.classes.strategy.strategy import Strategy
from core.classes.strategy.simple_strategy import SimpleStrategy
from core.classes.strategy.breakout_strategy import BreakoutStrategy


if __name__ == "__main__":
    strategy_file = os.path.join(os.path.dirname(__file__), 'config/simple_strategy.json')

    with open(strategy_file, "r") as json_file:
        strategy_params = json.load(json_file)

        # Generate subclass Strategy object based on user provided JSON file, depending on strategy type.
        if strategy_params["type"] == Strategy.SIMPLE_STRATEGY:
            strategy = SimpleStrategy(strategy_params)
        elif strategy_params["type"] == Strategy.BREAKOUT_STRATEGY:
            strategy = BreakoutStrategy(strategy_params)
        else:
            strategy_type = strategy_params["type"]
            raise TypeError(f"Invalid Strategy type: {strategy_type}")

        run(strategy)  # Use strategy object to execute trading strategy.
