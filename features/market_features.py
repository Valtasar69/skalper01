import pandas as pd
import numpy as np

def calc_price_speed(df):
    """
    Добавляет в df колонку price_speed = change по закрытиям
    """
    df['price_speed'] = df['close'].diff()
    return df

def detect_volume_spike(df, mult=2.5):
    """
    Возвращает True, если объём последнего бара > mult * средний объём по 20 барам
    """
    mean_vol = df['volume'].rolling(20).mean()
    return df['volume'].iloc[-1] > mean_vol.iloc[-1] * mult

def near_round_level(price, round_levels=[100, 500, 1000], tolerance=0.001):
    """
    True, если price близко к любому из уровней в round_levels с допуском tolerance
    """
    for level in round_levels:
        if abs(price % level) / level < tolerance:
            return True
    return False

def detect_iceberg(df, window=20, vol_mult=1.5, price_tol=0.002):
    """
    Псевдо-айсберг:
    - за последние `window` баров объём последнего > vol_mult * средний объём
    - относительный диапазон high-low на этом окне < price_tol
    """
    if len(df) < window:
        return False

    recent = df.tail(window)
    avg_vol = recent['volume'].mean()
    last_vol = recent['volume'].iat[-1]
    price_range = recent['high'].max() - recent['low'].min()
    rel_range = price_range / recent['close'].mean()

    is_big_vol = last_vol > avg_vol * vol_mult
    is_tight_price = rel_range < price_tol

    return bool(is_big_vol and is_tight_price)
