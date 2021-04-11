from .strategy import Strategy


class Order(object):
    def __init__(self, strategy: Strategy):
        """
        An object representing a trade order to be sent to the Phemex API. Use to generate trade parameters in the
        format required by the Phemex API, by process the user-provided strategy.
        """
        self.strategy = strategy
