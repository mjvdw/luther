import numpy as np
from pandas import DataFrame

"""
Fractal Indicator Function
Note: Functions are adapted from:
Kaabar, Sofien. "The Fractal Indicator — Detecting Tops & Bottoms in Markets," *Medium,* Dec 2020, Link: https://medium.com/swlh/the-fractal-indicator-detecting-tops-bottoms-in-markets-1d8aac0269e8.
"""
# Simple Moving Average
"""
def sma(x, n=10):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[n:] - cumsum[:-n]) / float(n)
"""


def sma(s, n=10):
    out = np.zeros(len(s))
    for i in range(1, len(s) - n):
        out[i + n] = np.mean(s[i:i + n])
    return out


# Exponential Moving Average
def ema(s, n=10):
    ema = np.zeros(len(s))
    multiplier = 2.0 / float(1 + n)
    sma = sum(s[:n]) / float(n)
    ema[n - 1] = sma
    for i in range(1, len(s) - n):
        ema[i + n] = s[i + n] * multiplier + ema[i - 1 + n] * (1 - multiplier)
    return ema


# Rolling volatility
def rolling_volatility(s, n=10):
    volatility = np.zeros(len(s))
    for i in range(1, len(s) - n):
        volatility[i + n] = np.std(s[i:i + n])
    return volatility


# Fractal Indicator
# df is from import_high_low() function.
def fractal_indicator(df, n=20, min_max_lookback=14):
    np.seterr(divide='ignore', invalid='ignore')

    high = df['high'].values
    low = df['low'].values

    ema_high = ema(high, n=n)
    ema_low = ema(low, n=n)

    vol_high = rolling_volatility(high, n=n)
    vol_low = rolling_volatility(low, n=n)
    ave_vol = (vol_high + vol_low) / 2.0

    demeaned_high = high - ema_high
    demeaned_low = low - ema_low

    max_high = np.zeros(len(df))
    min_low = np.zeros(len(df))

    for i in range(min_max_lookback, len(df)):
        max_high[i] = max(demeaned_high[(i - min_max_lookback + 1):(i + 1)])
        min_low[i] = min(demeaned_low[(i - min_max_lookback + 1):(i + 1)])

    fractal_1 = max_high - min_low

    fractal = np.divide(fractal_1, ave_vol)

    out_df = DataFrame(fractal, columns=['Fractal_Indicator'])
    out_df = out_df.replace([np.nan, np.inf], 0)
    out_df = out_df.set_index(df.index)

    df_out = df.merge(out_df, right_index=True, left_index=True)

    return df_out