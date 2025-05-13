import pandas as pd

class Simulator:
    def __init__(self, df, stop_loss=0.001, take_profit=0.002, max_bars=None):
        self.df = df.reset_index(drop=True)
        self.sl = stop_loss
        self.tp = take_profit
        self.max_bars = max_bars
        self.trades = []

    def run(self, entry_func):
        i = 1
        while i < len(self.df):
            window = self.df.iloc[:i+1]
            signal = entry_func(window)
            if signal == 'LONG':
                entry_price = self.df.at[i, 'open']
                sl_price = entry_price * (1 - self.sl)
                tp_price = entry_price * (1 + self.tp)
                exit_price = None
                exit_idx = None

                for j in range(i+1, len(self.df)):
                    hi = self.df.at[j, 'high']
                    lo = self.df.at[j, 'low']
                    if hi >= tp_price:
                        exit_price = tp_price
                        exit_idx = j
                        break
                    if lo <= sl_price:
                        exit_price = sl_price
                        exit_idx = j
                        break
                    if self.max_bars and (j - i) >= self.max_bars:
                        exit_price = self.df.at[j, 'close']
                        exit_idx = j
                        break

                if exit_price is not None:
                    profit = (exit_price - entry_price) / entry_price
                    self.trades.append({
                        'entry_idx': i,
                        'exit_idx': exit_idx,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'profit': profit
                    })
                    i = exit_idx
                else:
                    break
            i += 1
        return pd.DataFrame(self.trades)

    def stats(self):
        if not self.trades:
            return {
                'trades': 0,
                'EV': 0,
                'Sharpe': 0,
                'Profit Factor': 0,
                'Max Profit': None,
                'Max Loss': None
            }
        df = pd.DataFrame(self.trades)
        profits = df['profit']
        ev = profits.mean()
        sharpe = ev / profits.std() if profits.std() != 0 else 0
        pf = (
            profits[profits > 0].sum() / abs(profits[profits < 0].sum())
            if any(profits < 0) else float('inf')
        )
        return {
            'trades': len(df),
            'EV': ev,
            'Sharpe': sharpe,
            'Profit Factor': pf,
            'Max Profit': profits.max(),
            'Max Loss': profits.min()
        }
