import time
import logging
from datetime import datetime

from exchange import init_exchange
from data.fetcher import fetch_ohlcv
from features.market_features import (
    calc_price_speed,
    detect_volume_spike,
    near_round_level,
    detect_iceberg,
)
from features.orderbook_features import detect_orderbook_imbalance
from features.signal_generator import generate_signal
from features.risk_management import calc_atr, position_size
from orders.trader import execute_trade
from visual.trade_logger import log_trade

# --- Настройка логирования ---
LOG_FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()
exchange = init_exchange()
def run_iteration(exchange, symbol, balance, risk_per_trade, sl_mul, tp_mul):
    """
    Возвращает dict с результатом сделки или None, если signal==NOTHING
    """
    # 1) OHLCV
    df = fetch_ohlcv(exchange, symbol)

    # 2) ATR и уровни SL/TP
    atr = calc_atr(df, period=14)
    price = df["close"].iat[-1]
    sl_long = price - sl_mul * atr
    sl_short = price + sl_mul * atr

    # 3) Другие фичи
    df = calc_price_speed(df)
    speed = df["price_speed"].iat[-1]
    vol_spike = detect_volume_spike(df)
    round_lvl = near_round_level(price)
    iceberg = detect_iceberg(df)
    ob_imbalance = detect_orderbook_imbalance(exchange, symbol) or 0

    # 4) Генерация сигнала
    features = {
        "price": price,
        "speed": speed,
        "vol_spike": vol_spike,
        "round_lvl": round_lvl,
        "iceberg": iceberg,
        "orderbook_imbalance": ob_imbalance,
    }
    signal = generate_signal(features)
    if signal == "NOTHING":
        return None

    # 5) Размер позиции и исполнение
    if signal == "BUY":
        size = position_size(balance, risk_per_trade, price, sl_long)
        tp = price + tp_mul * atr
        trade = execute_trade(
            exchange, signal, symbol, size,
            stop_price=sl_long, take_profit=tp
        )
    else:  # SELL
        size = position_size(balance, risk_per_trade, price, sl_short)
        tp = price - tp_mul * atr
        trade = execute_trade(
            exchange, signal, symbol, size,
            stop_price=sl_short, take_profit=tp
        )

    if trade:
        # логируем в CSV
        trade.update({
            "speed": speed,
            "vol_spike": vol_spike,
            "round_lvl": round_lvl,
            "iceberg": iceberg,
            "ob_imbalance": ob_imbalance,
            "balance": balance,
            "risk_per_trade": risk_per_trade
        })
        log_trade(trade)

    return {
        "symbol": symbol,
        "signal": signal,
        "size": size,
        "price": price
    }

def main():
    logger.info("🚀 Запуск Scalper Bot (multi)")

    # Параметры
    symbols = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT",
        "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "LINK/USDT",
        "LTC/USDT", "SHIB/USDT"
    ]
    interval = 30               # сек
    risk_per_trade = 0.01       # 1% депозита
    sl_mul = 1.0                # коэффициент ATR для стопа
    tp_mul = 2.0                # коэффициент ATR для тейка

    # Подключаемся к бирже
    try:
        exchange = init_exchange()
        logger.info("✅ OKX Connected")
    except Exception as e:
        logger.error(f"Не удалось подключиться: {e}")
        return

    # Основной цикл
    while True:
        start = time.time()
        # за итерацию обновим баланс
        balance = exchange.fetch_balance().get("USDT", {}).get("free", 0.0)

        results = []
        for symbol in symbols:
            try:
                res = run_iteration(
                    exchange, symbol,
                    balance, risk_per_trade, sl_mul, tp_mul
                )
                if res:
                    results.append(res)
            except Exception as e:
                logger.error(f"Ошибка по {symbol}: {e}")

        # Логируем результат итерации
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if not results:
            logger.info(f"{now} — Ничего интересного")
        else:
            for r in results:
                action = "вошли в" if r["signal"] == "BUY" else "вышли из"
                logger.info(
                    f"{now} — {action} сделку по {r['symbol']} "
                    f"[{r['signal']}] price={r['price']:.2f} size={r['size']:.6f}"
                )

        # Ждём остаток интервала
        elapsed = time.time() - start
        time.sleep(max(0, interval - elapsed))

if __name__ == "__main__":
    main()
