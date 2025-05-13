import logging

def execute_trade(exchange, signal: str, symbol: str, size: float,
                  stop_price: float = None, take_profit: float = None):
    """
    Отправка рыночного ордера + опциональных стоп-лосс / тейк-профит.
    signal     — "BUY" или "SELL"
    size       — объём в базовом активе
    stop_price — уровень стоп-лосса
    take_profit— уровень тейк-профита
    """
    side = 'buy' if signal == 'BUY' else 'sell'
    try:
        # 1) Market order
        order = exchange.create_order(symbol, 'market', side, size)
        logging.info(f"🚀 Выполнен MARKET {signal}: {size} @ market")
        
        # 2) Stop-loss (стоп-маркет)
        if stop_price is not None:
            sl_side = 'sell' if signal == 'BUY' else 'buy'
            params = {
                'stopPrice': stop_price,
                'trigger': 'stop',       # или 'loss' в зависимости от биржи
                'orderType': 'market'    # стоп-маркет
            }
            sl = exchange.create_order(symbol, 'stop', sl_side, size, None, params)
            logging.info(f"🔒 Стоп-лосс ордер: {sl_side} {size} @ stopPrice={stop_price}")

        # 3) Take-profit (трейлинг/фикс)
        if take_profit is not None:
            tp_side = 'sell' if signal == 'BUY' else 'buy'
            params = {
                'stopPrice': take_profit,
                'trigger': 'profit',     # или 'entry'/'take', проверь у OKX
                'orderType': 'limit'     # лимитная заявка
            }
            tp = exchange.create_order(symbol, 'limit', tp_side, size, take_profit, params)
            logging.info(f"🏁 Тейк-профит ордер: {tp_side} {size} @ price={take_profit}")

        return True

    except Exception as e:
        logging.error(f"💥 Ошибка исполнения сделки: {e}")
        return False
