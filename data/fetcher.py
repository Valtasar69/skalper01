import pandas as pd


def fetch_ohlcv(exchange, symbol='BTC/USDT', timeframe='1m', limit=500):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def detect_consolidation(df, bars=10, threshold=0.003):
    recent = df.tail(bars)
    price_range = recent['high'].max() - recent['low'].min()
    relative_range = price_range / recent['close'].mean()
    return relative_range < threshold