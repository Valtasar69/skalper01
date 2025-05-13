# features/signal_generator.py

def generate_signal(features: dict) -> str:
    speed = features.get("speed", 0)
    vol_spike = features.get("vol_spike", False)
    iceberg = features.get("iceberg", False)
    ob = features.get("orderbook_imbalance")
    # превращаем None в 0
    ob = ob if isinstance(ob, (int, float)) else 0

    # BUY
    if speed > 20 and vol_spike and iceberg and ob > 1.5:
        return "BUY"
    # SELL
    if speed < -20 and vol_spike and (not iceberg) and ob < -1.5:
        return "SELL"
    return "NOTHING"
