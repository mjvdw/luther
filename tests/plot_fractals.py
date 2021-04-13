from core.classes.strategy.breakout_strategy import BreakoutStrategy
from core.classes.database import Database

import pandas as pd
import mplfinance as mpf

"""
Documentation for matplotlib-finance: https://github.com/matplotlib/mplfinance/blob/master/examples/using_lines.ipynb
"""


def attempt_two(fractals_df):
    """
    More intelligently discovering and averaging previous fractals to create a reasonably accurate zone.
    """
    pass

    s_prices = fractals_df.loc[fractals_df["fractals_low"]]["Low"].tolist()
    r_prices = fractals_df.loc[fractals_df["fractals_high"]]["High"].tolist()

    zone_margin = 100

    # Create initial support zone.
    working_price = 0
    zones = []
    two_or_more = False
    z = 0
    colors = []
    for prices in [r_prices, s_prices]:
        p = []
        for price in prices:
            if working_price == 0:
                working_price = price
            elif abs(price - working_price) < zone_margin:
                working_price = (working_price + price)/2
                two_or_more = True
            elif two_or_more:
                zones.append(working_price)
                p.append(working_price)
                working_price = 0
                two_or_more = False
            # else:
            #     zones.append(working_price)
            #     p.append(working_price)

        p_colors = [None] * len(p)
        for i in range(len(p_colors)):
            # Resistance red, support green.
            p_colors[i] = "r" if z == 0 else "g"

        print(p_colors)

        sr = "resistance" if z == 0 else "support"
        print(f"All {sr}: {prices}")
        print(f"Selected {sr}: {p}")

        colors = colors + p_colors

        print(z)
        z += 1

    print(colors)

    mpf.plot(fractals_df, hlines=dict(hlines=zones, colors=colors, linestyle='-', linewidths=1, alpha=0.4),
             title='BTCUSD', ylabel='Price')


def attempt_one(fractals_df):
    """
    Essentially just plotting lines between the fractals discovered.
    """
    support = []
    resistance = []

    j = 10
    for i in range(j):
        s_index = fractals_df.loc[fractals_df["fractals_low"]]["Low"].tail(j).index[i]
        s_value = fractals_df.loc[fractals_df["fractals_low"]]["Low"].tail(j).values[i]
        s = (s_index, s_value)
        support.append(s)

        r_index = fractals_df.loc[fractals_df["fractals_high"]]["High"].tail(j).index[i]
        r_value = fractals_df.loc[fractals_df["fractals_high"]]["High"].tail(j).values[i]
        r = (r_index, r_value)
        resistance.append(r)

    sr = [support, resistance]
    print(sr)

    # mpf.plot(fractals_df, hlines=dict(hlines=sr, linestyle='-.'), title='BTCUSD', ylabel='Price')
    mpf.plot(fractals_df, alines=sr, title='BTCUSD', ylabel='Price')


if __name__ == "__main__":
    market_data = pd.read_csv(Database.MARKET_DATA_PATH, index_col=0)

    reformatted_data = pd.DataFrame()
    reformatted_data['Date'] = market_data["timestamp"]
    reformatted_data['Open'] = market_data["openEp"]/10000
    reformatted_data['High'] = market_data["highEp"]/10000
    reformatted_data['Low'] = market_data["lowEp"]/10000
    reformatted_data['Close'] = market_data["closeEp"]/10000
    reformatted_data['Volume'] = market_data["volume"]

    reformatted_data['Date'] = pd.to_datetime(reformatted_data['Date'], unit="s", origin="unix")

    reformatted_data.set_index("Date", inplace=True)

    fractals_df = BreakoutStrategy.get_fractals(reformatted_data.tail(300))

    attempt_two(fractals_df)

