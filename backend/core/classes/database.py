import os


class Database(object):

    MARKET_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/market_data.csv')

    def __init__(self):
        pass
