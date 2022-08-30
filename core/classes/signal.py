import pandas as pd
# noinspection PyUnresolvedReferences
import pandas_ta as ta

from .user import User


class Signal(object):

    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    EXIT = "EXIT"
    WAIT = "WAIT"
    SET_EXIT_LIMIT = "SET_EXIT_LIMIT"

    SCALPING = "SCALPING"
    BREAKOUT = "BREAKOUT"
    SIMPLE = "SIMPLE"
    RANDOM = "RANDOM"

    def __init__(self, data: pd.DataFrame, strategy, user: User):
        """
        Contains properties and methods for generating long, short, exit or wait signals, along with confidence level
        and trade type (eg, scalping v breakout). These properties are derived from technical indicators and the
        strategy given by the user.

        :param data: Market data received via websocket from Phemex.
        :param strategy: a Strategy subclass containing user information about how and when to trade.
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

        # Get a dictionary representing indicators.
        indicators = self.strategy.indicators

        # Add indicator values to self.data DataFrame, but iterating through the user-provided parameters.
        for indicator in indicators:
            kind = indicator["ta_kind"]  # Type of indicator, for pandas_ta.
            # Parameters required for indicator, for pandas_ta.
            params = indicator["params"]

            ta_output = self.data.ta(kind=kind, **params)

            if type(ta_output) == pd.DataFrame:
                # If the indicator generates a DataFrame rather than individual Series, iterate through and add
                # individually.
                for series in ta_output:
                    self.data[series] = ta_output[series]
                    self._indicators[series] = self.data[series].tail(
                        1).values[0]
            else:
                # Else, just set the Series to be a new column in the existing DataFrame.
                self.data[ta_output.name] = ta_output
                self._indicators[ta_output.name] = self.data[ta_output.name].tail(
                    1).values[0]

    def _check_conditions(self):
        """
        Using parameters provided by user, check whether the relevant conditions are met. If they are met, set the
        relevant properties (action, confidence, strategy_type) to the appropriate value. This is then collected
        and used back out at the script level, outside the class.

        """

        # Get a dictionary containing the conditions for trading.
        conditions = self.strategy.conditions
        valid_conditions_format = self._validate_conditions_format(
            conditions=conditions)

        is_open_positions = self.user.is_open_positions
        is_unfilled_orders = self.user.is_unfilled_orders
        # is_trading is a combination of (is_open_positions OR is_unfilled_orders).
        is_trading = self.user.is_trading

        if valid_conditions_format and not is_trading:
            # Evaluate entry conditions.
            signals = self.strategy.check_entry_conditions(data=self.data)
        elif valid_conditions_format and is_open_positions:
            # Evaluate exit conditions, OR if exit order has been placed, but unfilled, checking whether it should move
            # to match large price movements.
            signals = self.strategy.check_exit_conditions(
                data=self.data, user=self.user)
        else:
            signals = None

        if signals:
            # Get signal with greatest confidence, if there are more than one.
            greatest_confidence = max(signals, key=lambda x: x["confidence"])
            self._action = greatest_confidence["action"]
            self._confidence = greatest_confidence["confidence"]
            self._strategy_type = greatest_confidence["strategy_type"]
        else:
            self._action = self.WAIT

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
            # TODO: Put some action logic here to test whether conditions are valid.
            valid = True
            return valid
        except KeyError:
            raise KeyError(
                "Conditions not formatted correctly. A dictionary key is either missing or incorrect.")
        except IndexError:
            raise IndexError(
                "Conditions not formatted correctly. List index out of range.")
