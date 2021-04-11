from .strategy import Strategy
from .phemex import Phemex
from .user import User
import pandas as pd
# noinspection PyUnresolvedReferences
import pandas_ta as ta


class Signal(object):

    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    EXIT = "EXIT"
    WAIT = "WAIT"

    SCALPING = "SCALPING"
    BREAKOUT = "BREAKOUT"

    def __init__(self, data: pd.DataFrame, strategy: Strategy, user: User):
        """
        Contains properties and methods for generating long, short, exit or wait signals, along with confidence level
        and trade type (eg, scalping v breakout). These properties are derived from technical indicators and the
        strategy given by the user.

        :param data: Market data received via websocket from Phemex.
        :param strategy: a Strategy object containing user information about how and when to trade.
        """

        self.data = data
        self.strategy = strategy
        self.user = user

        self._action = None
        self._confidence = None
        self._strategy_type = None

        self._indicators = {}

        self._generate_signal()

    @property
    def signal(self) -> dict:
        """
        Utility function returning the entire signal, rather than components only.

        :return: a dictionary containing all signal properties.
        """

        return {
            "action": self.action,
            "confidence": self.confidence,
            "strategy_type": self.strategy_type
        }

    @property
    def action(self) -> str:
        """
        The trade to make, or not make. Possible options are ENTER_LONG, ENTER_SHORT, EXIT and WAIT.

        :return: A string identifying whether to go long, go short, exit the trade or wait for a better signal.
        """

        return self._action

    @property
    def confidence(self) -> int:
        """
        A trading strategy may specify different trading parameters depending on the technical indicator requirements
        that are met. If the strategy is very confident that the market is about to move in a particular direction,
        this number will be high. If only a few technical indicator requirements are met, but the user still wants to
        trade, this number will be low.

        :return: An integer representing the script's confidence in the signal it's generating, based on how many
        technical indicator requirements have been met. Higher numbers indicate higher confidence.
        """
        return self._confidence

    @property
    def strategy_type(self) -> str:
        """
        A user may specify multiple types of strategies. This property represents which strategy type is current being
        used or assessed.

        :return: A string representing the strategy type (eg, SCALPING or BREAKOUT). These are fixed values.
        """
        return self._strategy_type

    def _generate_signal(self):
        """
        Generate a dictionary containing relevant signal information from the provided strategy and market data, and
        set these values to the corresponding properties of the class instance.

        """

        # Generate indicator values.
        self._get_indicator_values()

        # Use indicator values to check whether trading conditions are met and set the relevant action, confidence and
        # strategy_type class properties.
        self._check_conditions()

    def _get_indicator_values(self):
        """
        Using the pandas_ta library, generate technical indicators based on the parameters provided by the user.

        """

        indicators = self.strategy.indicators  # Get a dictionary representing indicators.

        # Add indicator values to self.data DataFrame, but iterating through the user-provided parameters.
        for indicator in indicators:
            kind = indicator["ta_kind"]  # Type of indicator, for pandas_ta.
            params = indicator["params"]  # Parameters required for indicator, for pandas_ta.

            ta_output = self.data.ta(kind=kind, **params)

            if type(ta_output) == pd.DataFrame:
                # If the indicator generates a DataFrame rather than individual Series, iterate through and add
                # individually.
                for series in ta_output:
                    self.data[series] = ta_output[series]
                    self._indicators[series] = self.data[series].tail(1).values[0]
            else:
                # Else, just set the Series to be a new column in the existing DataFrame.
                self.data[ta_output.name] = ta_output
                self._indicators[ta_output.name] = self.data[ta_output.name].tail(1).values[0]

    def _check_conditions(self):
        """
        Using parameters provided by user, check whether the relevant conditions are met. If they are met, set the
        relevant properties (action, confidence, strategy_type) to the appropriate value. This is then collected
        and used back out at the script level, outside the class.

        """

        conditions = self.strategy.conditions  # Get a dictionary containing the conditions for trading.
        valid_conditions_format = self._validate_conditions_format(conditions=conditions)
        is_trading = self.user.is_trading()  # Returns True if there is either an open position or unfilled order.

        if valid_conditions_format and not is_trading:
            # Evaluate entry conditions.

            signals = []

            for condition in conditions["enter"]:
                # Test each set of conditions.
                params = condition["params"]
                results = []

                for param in params:
                    # Test each parameter within one set of conditions.
                    left = self.data[param[0]].tail(1).values[0] if type(param[0]) == str else param[0]
                    right = self.data[param[1]].tail(1).values[0] if type(param[1]) == str else param[1]

                    expression = str(left) + param[2] + str(right)  # Comparison expression string to be evaluated.
                    passed = eval(expression)  # Result of evaluation.
                    results.append(passed)

                if all(results):
                    signal = {
                        "action": condition["action"],
                        "confidence": condition["confidence"],
                        "strategy_type": self.strategy.strategy_type
                    }
                    signals.append(signal)

            if signals:
                # Get signal with greatest confidence, if there are more than one.
                greatest_confidence = max(signals, key=lambda x: x["confidence"])
                self._action = greatest_confidence["action"]
                self._confidence = greatest_confidence["confidence"]
                self._strategy_type = greatest_confidence["strategy_type"]
            else:
                self._action = self.WAIT

        elif valid_conditions_format and self.user.open_position:
            # Evaluate exit conditions.

            condition = conditions["exit"]
            position = self.user.open_position

            if position.net_pnl >= condition["take_profit"] or position.net_pnl <= condition["stop_loss"]:
                self._action = self.EXIT
            else:
                for indicator in condition["indicators"]:
                    key = indicator["key"]
                    value = self.data[key].tail(1).values[0]
                    limit = indicator["short_exit_limit"] if position.side == "Sell" \
                        else indicator["long_exit_limit"]
                    condition_str = str(value) + str(limit[1]) + str(limit[0])
                    if eval(condition_str):
                        self._action = self.EXIT

        if not self.action:
            self._action = self.WAIT

    @staticmethod
    def _validate_conditions_format(conditions: dict) -> bool:
        """
        Check whether the strategy config file provided is giving conditions in the right format, and raise an error
        if it isn't, with a rough indication about what is likely wrong.

        :param conditions: The conditions being validated.
        :return: A boolean indicating whether the conditions file is valid.
        """
        try:
            valid = bool(conditions["enter"][0]["params"][0][2])
            return valid
        except KeyError:
            raise KeyError("Conditions not formatted correctly. A dictionary key is either missing or incorrect.")
        except IndexError:
            raise IndexError("Conditions not formatted correctly. List index out of range.")
