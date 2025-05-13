import pandas as pd

def calc_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    Средний истинный диапазон за последние `period` баров.
    """
    high_low = df['high'] - df['low']
    high_prev_close = (df['high'] - df['close'].shift()).abs()
    low_prev_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    return tr.tail(period).mean()

def position_size(balance: float, risk_per_trade: float, entry_price: float, stop_price: float) -> float:
    """
    Возвращает размер позиции (в базовом активе), 
    чтобы риск (entry_price - stop_price) * size ≈ balance * risk_per_trade.
    """
    risk_amount = balance * risk_per_trade
    trade_risk = abs(entry_price - stop_price)
    if trade_risk == 0:
        return 0
    size = risk_amount / trade_risk
    return size
