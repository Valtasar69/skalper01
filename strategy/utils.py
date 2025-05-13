import numpy as np


def calc_expected_value(profits):
    return np.mean(profits)


def calc_sharpe_ratio(profits):
    mean = np.mean(profits)
    std = np.std(profits)
    return mean / std if std != 0 else 0


def is_breakout(df, buffer=0.001):
    if len(df) < 2:
        return False
    last_close = df.iloc[-1]['close']
    prev_high = df.iloc[-2]['high']
    return last_close > prev_high * (1 + buffer)


def is_bounce(df, support_level, buffer=0.001):
    last_close = df.iloc[-1]['close']
    return abs(last_close - support_level) / support_level < buffer