import pandas as pd
from pathlib import Path

EXPORT_PATH = Path('signals.csv')

def export_signal(timestamp, signal_type, price,
                  speed=None, volume_spike=None, round_level=None):
    row = {
        'time': timestamp,
        'signal': signal_type,
        'price': price,
        'speed': speed,
        'volume_spike': volume_spike,
        'round_level': round_level
    }
    df = pd.DataFrame([row])
    df.to_csv(
        EXPORT_PATH,
        mode='a',
        header=not EXPORT_PATH.exists(),
        index=False
    )
    print(f"📤 {signal_type} @ {price} | speed={speed:.2f} | vol_spike={volume_spike} | round={round_level}")