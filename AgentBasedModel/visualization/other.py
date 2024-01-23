from AgentBasedModel.simulator import SimulatorInfo
import AgentBasedModel.utils.math as math
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import pandas as pd


def plot_book_stat(
        info:    SimulatorInfo,
        idx:     int,
        stat:    str = 'quantity',
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot ExchangeAgent`s Order Book chosen statistic

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id
    :param stat: Order Book statistic to plot, defaults 'quantity'
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(
             f'Exchange{idx}: Order Book {stat} by order type ' if rolling == 1
        else f'Exchange{idx}: Order Book {stat} by order type  (MA {rolling})'
    )
    plt.xlabel('Iterations')
    plt.ylabel(f'Order {stat}')

    iterations = range(rolling - 1, len(info.dividends[idx]))
    v_bid = math.rolling([v[stat]['bid'] for v in info.orders[idx]], rolling)
    v_ask = math.rolling([v[stat]['ask'] for v in info.orders[idx]], rolling)
    
    plt.plot(iterations, v_bid, label='bid', color='green')
    plt.plot(iterations, v_ask, label='ask', color='red')

    plt.legend()
    plt.show()


def print_book(info: SimulatorInfo, idx: int, n=5):
    val = pd.concat([
        pd.DataFrame({
            'Sell': [v.price for v in info.exchanges[idx].order_book['ask']],
            'Quantity': [v.qty for v in info.exchanges[idx].order_book['ask']]
            }).groupby('Sell').sum().reset_index().head(n),
        pd.DataFrame({
            'Buy': [v.price for v in info.exchanges[idx].order_book['bid']],
            'Quantity': [v.qty for v in info.exchanges[idx].order_book['bid']]
        }).groupby('Buy').sum().reset_index().sort_values('Buy', ascending=False).head(n)
    ])
    print(val[['Buy', 'Sell', 'Quantity']].fillna('').to_string(index=False))


def plot_book(info: SimulatorInfo, idx: int, bins=50, figsize=(6, 6)):
    bid = list()
    for order in info.exchanges[idx].order_book['bid']:
        for p in range(order.qty):
            bid.append(order.price)

    ask = list()
    for order in info.exchanges[idx].order_book['ask']:
        for p in range(order.qty):
            ask.append(order.price)

    plt.figure(figsize=figsize)
    plt.title('Order book')
    plt.hist(bid, label='bid', color='green', bins=bins)
    plt.hist(ask, label='ask', color='red', bins=bins)
    plt.show()


def plot_orderbook(info: SimulatorInfo, exchange_ind: int = 0):

    _bids = info.exchanges[exchange_ind].order_book['bid']
    _asks = info.exchanges[exchange_ind].order_book['ask']

    bids = pd.DataFrame({'qty': [bid.qty for bid in _bids], 'price': [bid.price for bid in _bids]})
    asks = pd.DataFrame({'qty': [ask.qty for ask in _asks], 'price': [ask.price for ask in _asks]})

    bids['cum_qty'] = bids['qty'].cumsum()
    asks['cum_qty'] = asks['qty'].cumsum()

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.bar(bids['price'], bids['cum_qty'], width=1, align='center', color='green', label='Bids')
    ax.bar(asks['price'], asks['cum_qty'], width=1, align='center', color='red', label='Asks')

    ax.set_title('Order Book')
    ax.set_xlabel('Price')
    ax.set_ylabel('Cumulative Quantity')

    ax.legend()
    plt.show()


def plot_orderbook_with_depth(depth: float, info: SimulatorInfo, exchange_ind: int = 0):
    _bids = info.exchanges[exchange_ind].order_book['bid']
    _asks = info.exchanges[exchange_ind].order_book['ask']

    bids = pd.DataFrame({'qty': [bid.qty for bid in _bids], 'price': [bid.price for bid in _bids]})
    asks = pd.DataFrame({'qty': [ask.qty for ask in _asks], 'price': [ask.price for ask in _asks]})

    mid_price = (bids['price'].max() + asks['price'].min()) / 2
    price_range = mid_price * depth

    bids = bids[(bids['price'] >= mid_price - price_range) & (bids['price'] <= mid_price)]
    asks = asks[(asks['price'] <= mid_price + price_range) & (asks['price'] >= mid_price)]

    bids_grouped = bids.groupby('price').apply(lambda x: list(x['qty'])).reset_index(name='orders')
    asks_grouped = asks.groupby('price').apply(lambda x: list(x['qty'])).reset_index(name='orders')

    fig, ax = plt.subplots(figsize=(12, 7))

    for _, bid in bids_grouped.iterrows():
        bottom = 0
        for qty in bid['orders']:
            ax.bar(bid['price'], qty, width=0.1, bottom=bottom, align='center', color='green', edgecolor='black')
            bottom += qty

    for _, ask in asks_grouped.iterrows():
        bottom = 0
        for qty in ask['orders']:
            ax.bar(ask['price'], qty, width=0.1, bottom=bottom, align='center', color='red', edgecolor='black')
            bottom += qty

    ax.set_title(f'Order Book within ±{depth*100}% of Mid Price')
    ax.set_xlabel('Price')
    ax.set_ylabel('Quantity')

    plt.grid(False)
    plt.show()


def plot_feature_chronology(info, idx):
    fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(15, 20))

    features = ['ob_imbs', 'smart_pr', 'ba_imbs', 'tr_signs', 'sign_vol', 'prets']
    titles = ['Order Book Imbalances', 'Smart Prices', 'Bid-Ask Imbalances', 'Trade Signs', 'Signed Transaction Volume', 'Past Returns']

    for ax, feature, title in zip(axes, features, titles):
        ax.plot(getattr(info, feature)[idx])
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.grid(True)

    plt.tight_layout()
    plt.show()


def plot_feature_distributions(info, idx):
    fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(15, 20))

    features = ['ob_imbs', 'smart_pr', 'ba_imbs', 'tr_signs', 'sign_vol', 'prets']
    titles = ['Order Book Imbalances Distribution', 'Smart Prices Distribution', 'Bid-Ask Imbalances Distribution', 'Trade Signs Distribution', 'Signed Transaction Volume Distribution', 'Past Returns Distribution']

    for ax, feature, title in zip(axes, features, titles):
        ax.hist(getattr(info, feature)[idx], bins=20, edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.grid(True)

    plt.tight_layout()
    plt.show()