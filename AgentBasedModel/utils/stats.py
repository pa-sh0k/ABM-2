import pandas as pd


def ob_imbalance(info, exchange_ind):
    _bids = info.exchanges[exchange_ind].order_book['bid']
    _asks = info.exchanges[exchange_ind].order_book['ask']

    b = _bids.first.qty
    a = _asks.first.qty

    return (b - a) / (b + a)


