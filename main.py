import logging
import json
import time
from datetime import datetime

from exchange import init_exchange
from data.fetcher import fetch_ohlcv, detect_consolidation
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
from backtest.simulator import Simulator

# --- Logging setup ---
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("bot_runtime.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_success(step):
    logger.info(f"✅ {step} — OK!")

def log_fail(step, err):
    logger.error(f"💥 {step} — FAILED: {err}")

def run_iteration(exchange, symbol="BTC/USDT"):
    try:
        # 1) OHLCV
        df = fetch_ohlcv(exchange)

        # 2) Risk: ATR & SL
        atr = calc_atr(df, period=14)
        price = df["close"].iat[-1]
        sl_long = price - atr
        sl_short = price + atr

        # 3) Other features
        df = calc_price_speed(df)
        speed = df["price_speed"].iat[-1]
        vol_spike = detect_volume_spike(df)
        round_lvl = near_round_level(price)
        iceberg = detect_iceberg(df)
        ob_imbalance = detect_orderbook_imbalance(exchange, symbol) or 0

        # 4) Signal
        features = {
            "price": price,
            "speed": speed,
            "vol_spike": vol_spike,
            "round_lvl": round_lvl,
            "iceberg": iceberg,
            "orderbook_imbalance": ob_imbalance,
        }
        signal = generate_signal(features)

        # 5) Position sizing & execution
        balance = 1000.0           # TODO: брать реальный баланс через API
        risk_per_trade = 0.01      # 1% риска
        size = None
        trade_info = None

        if signal == "BUY":
            size = position_size(balance, risk_per_trade, price, sl_long)
            tp = price + 2 * atr
            trade_info = execute_trade(
                exchange, signal, symbol, size,
                stop_price=sl_long, take_profit=tp
            )
        elif signal == "SELL":
            size = position_size(balance, risk_per_trade, price, sl_short)
            tp = price - 2 * atr
            trade_info = execute_trade(
                exchange, signal, symbol, size,
                stop_price=sl_short, take_profit=tp
            )

        # 6) Log trade to CSV
        if trade_info:
            trade_info.update({
                "speed": speed,
                "vol_spike": vol_spike,
                "round_lvl": round_lvl,
                "iceberg": iceberg,
                "ob_imbalance": ob_imbalance,
                "balance": balance,
                "risk_per_trade": risk_per_trade
            })
            log_trade(trade_info)

        # 7) Console log for iteration
        sl_str = f"{sl_long:.2f}" if signal == "BUY" else (f"{sl_short:.2f}" if signal == "SELL" else "—")
        tp_str = f"{tp:.2f}" if signal in ("BUY", "SELL") else "—"
        size_str = f"{size:.6f}" if size is not None else "—"
        logger.info(
            f"🎯 Iteration @ {datetime.utcnow().isoformat()} — "
            f"Signal={signal}, Price={price:.2f}, Size={size_str}, SL={sl_str}, TP={tp_str}"
        )
    except Exception as e:
        log_fail("Iteration", e)

def main():
    logger.info("🚀 Starting Scalper Bot (loop mode)")
    try:
        exchange = init_exchange()
        log_success("Connect to OKX & load markets")
    except Exception as e:
        log_fail("Connect to OKX", e)
        return

    symbol = "BTC/USDT"
    interval = 60  # seconds

    try:
        while True:
            start = time.time()
            run_iteration(exchange, symbol)
            elapsed = time.time() - start
            time.sleep(max(0, interval - elapsed))
    except KeyboardInterrupt:
        logger.info("🛑 KeyboardInterrupt received — stopping bot")
    except Exception as e:
        log_fail("Main loop", e)

    logger.info("🎉 Bot stopped")

if __name__ == "__main__":
    main()
