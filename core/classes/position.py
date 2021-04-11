class Position(object):
    def __init__(self, position_details: dict):
        """
        An object representing an open position on the Phemex trading platform. Contains details about the trade, and
        using the clOrdId can link to database with exit parameters.

        :param position_details:
        """
        self.position_details = position_details

    @property
    def entry_price(self) -> int:
        return 0
