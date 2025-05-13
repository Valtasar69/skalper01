import csv
import os
from datetime import datetime

TRADE_LOG = "trade_log.csv"
FIELDS = [
    "timestamp", "signal", "symbol", "size", "entry_price",
    "stop_price", "take_profit",
    "speed", "vol_spike", "round_lvl", "iceberg", "ob_imbalance",
    "balance", "risk_per_trade"
]

def log_trade(trade):
    """
    trade: dict с ключами из FIELDS
    """
    write_header = not os.path.exists(TRADE_LOG)
    with open(TRADE_LOG, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        # добавляем текущее время, если не передано
        if "timestamp" not in trade or trade["timestamp"] is None:
            trade["timestamp"] = datetime.utcnow().isoformat()
        writer.writerow({k: trade.get(k) for k in FIELDS})
