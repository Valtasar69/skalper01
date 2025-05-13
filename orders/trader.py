import logging

def execute_trade(exchange, signal: str, symbol: str, size: float,
                  stop_price: float = None, take_profit: float = None):
    side = 'buy' if signal == 'BUY' else 'sell'
    try:
        # Market order
        order = exchange.create_order(symbol, 'market', side, size)
        logging.info(f"🚀 MARKET {signal}: {size} @ market")
        
        # Stop-loss
        if stop_price is not None:
            sl_side = 'sell' if signal == 'BUY' else 'buy'
            params = {
                'stopPrice': stop_price,
                'orderType': 'market',  # стоп-маркет
                'trigger': 'loss'
            }
            sl = exchange.create_order(symbol, 'stop', sl_side, size, None, params)
            logging.info(f"🔒 SL: {sl_side} {size} @ stopPrice={stop_price}")

        # Take-profit
        if take_profit is not None:
            tp_side = 'sell' if signal == 'BUY' else 'buy'
            params = {
                'stopPrice': take_profit,
                'orderType': 'limit',   # лимитная заявка
                'trigger': 'profit'
            }
            tp = exchange.create_order(symbol, 'limit', tp_side, size, take_profit, params)
            logging.info(f"🏁 TP: {tp_side} {size} @ price={take_profit}")

        return True

    except Exception as e:
        logging.error(f"💥 Trade execution error: {e}")
        return False
