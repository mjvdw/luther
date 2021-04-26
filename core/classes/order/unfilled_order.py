class UnfilledOrder(object):
    def __init__(self, order_data: dict):
        """
        Similar to the Position class, create an object representing an existing unfilled order on the Phemex platform.
        :param order_data:
        """
        self.order_data = order_data

    @property
    def action_time(self) -> int:
        action_time = self.order_data["actionTimeNs"]
        return action_time

    @property
    def cl_ord_id(self):
        """
        Random unique client order ID provided by script when sending parameters to Phemex API.

        :return: A string with the unique ID.
        """
        cl_ord_id = self.order_data["clOrdId"]
        return cl_ord_id
