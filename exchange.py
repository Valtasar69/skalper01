import ccxt
from config import load_keys


def init_exchange():
    keys = load_keys()
    exchange = ccxt.okx({
        'apiKey': keys['apiKey'],
        'secret': keys['secret'],
        'password': keys['password'],
        'enableRateLimit': True
    })
    exchange.load_markets()
    return exchange