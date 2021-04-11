#!/usr/bin/env python3

import os
import json

from core.core import run
from core.classes.strategy import Strategy


if __name__ == "__main__":
    strategy_file = os.path.join(os.path.dirname(__file__), 'config/scalping_strategy.json')

    with open(strategy_file, "r") as json_file:
        strategy_params = json.load(json_file)
        strategy = Strategy(strategy_params)  # Generate Strategy object based on user provided JSON file.
        run(strategy)  # Use strategy object to execute trading strategy.
