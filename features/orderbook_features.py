# features/orderbook_features.py

def detect_orderbook_imbalance(exchange, symbol="BTC/USDT", depth=20, thresh=1.5):
    """
    Проверяем imbalance в стакане:
      - скачиваем топ `depth` бидов и асков
      - считаем суммарный объём в bids и asks
      - возвращаем:
          "BID"  — если bid_vol > thresh * ask_vol
          "ASK"  — если ask_vol > thresh * bid_vol
          None   — если сбалансированно или не хватает данных
    """
    ob = exchange.fetch_order_book(symbol, limit=depth)
    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    # суммируем объёмы (элемент [1] каждой записи)
    bid_vol = sum(bid[1] for bid in bids)
    ask_vol = sum(ask[1] for ask in asks)

    # если нет данных — считаем сбалансированно
    if bid_vol == 0 or ask_vol == 0:
        return None

    # определяем дисбаланс
    if bid_vol / ask_vol > thresh:
        return "BID"   # кластер покупателей
    if ask_vol / bid_vol > thresh:
        return "ASK"   # кластер продавцов

    return None       # нет выраженного дисбаланса
