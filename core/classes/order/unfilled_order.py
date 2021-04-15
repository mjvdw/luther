from core.classes.user import User

class UnfilledNewOrder(object):
    def __init__(self, order_data: dict):
        """
        Similar to the Position class, create an object representing an existing unfilled order on the Phemex platform.
        :param order_data:
        """
        self.order_data = order_data

    @property
    def cl_ord_id(self):
        cl_ord_id = 0
        return cl_ord_id
