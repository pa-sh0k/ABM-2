from __future__ import annotations

from typing import Type

from AgentBasedModel.utils import Order, OrderList
from AgentBasedModel.utils.math import exp
import random


class Asset:
    id = 0

    def __init__(self):
        self.type = 'Stock'
        self.name = f'Asset{self.id}'
        self.id = Asset.id
        Asset.id += 1

    def update(self):
        pass


class Stock(Asset):
    """
    Asset with the following properties:
    - Dividend is paid to holders
    - Dividend is non-negative
    - Dividend changes over time
    - Traded throught ExchangeAgent
    """
    def __init__(self, dividend: float | int):
        """
        :param dividend: initial dividend > 0
        """
        super().__init__()
        self.type = 'Stock'
        self.dividend = dividend
        
        self.dividend_book = list()  # act like queue
        self._fill_book()
    
    def _next_dividend(self, div_current: float | int, std: float | int = 5e-3) -> float | int:
        x = max(exp(random.normalvariate(0, std)), 0)
        return div_current * x

    def _fill_book(self, n: int = 100):
        """
        Fill dividend book with future dividends.
        
        :param n: number of dividends to fill
        """
        if not self.dividend_book:
            self.dividend_book.append(self.dividend)
            n -= 1
        
        for i in range(n):
            div = self.dividend_book[-1]
            div = self._next_dividend(div)
            self.dividend_book.append(div)
    
    def update(self):
        """
        Add new dividend to queue and pop last
        """
        self._fill_book(1)
        self.dividend = self.dividend_book.pop(0)


class ExchangeAgent:
    """
    ExchangeAgent implements automatic orders handling within the order book
    """
    id = 0

    def __init__(
            self,
            asset: Type[Asset],                                             # traded asset
            # risk_free_rate: float = 5e-4, transaction_cost: float = 0,      # economy rates
            risk_free_rate: float = 0, transaction_cost: float = 0,      # economy rates
            mean: float | int = None, std: float | int = 25, n: int = 1000  # order book initialization
        ):
        """Creates ExchangeAgent with initialised order book and future dividends

        :param price: stock initial price
        :param std: standard deviation of order prices
        :param n: number of orders initialised
        :param rf: risk-free rate
        :param transaction_cost: transaction cost on operations for traders (fraction)
        """
        if mean is None:
            mean = asset.dividend / risk_free_rate

        self.name = f'Exchange{self.id}'
        self.id = ExchangeAgent.id
        ExchangeAgent.id += 1

        self.asset = asset
        self.risk_free_rate = risk_free_rate
        self.transaction_cost = transaction_cost
        self.last_trades = []
        self.last_price = 0
        self.aggr_baseline = 0.03  # the percentage of volume for which an order should constitute for to be counted as aggressive

        self.order_book = self.order_book = {'bid': OrderList('bid'), 'ask': OrderList('ask')}
        self._fill_book(mean, std, n)

    def _fill_book(self, mean: float | int, std: float | int, n: int):
        """Fill order book with random orders.

        Generate prices from normal distribution with *std*, and *price* as center; generate
        quantities for these orders from uniform distribution with 1, 5 bounds. Set bid orders when
        order price is less than *price*, set ask orders when order price is greater than *price*.
        """
        prices1 = [round(random.normalvariate(mean - std, std), 1) for _ in range(n // 2)]
        prices2 = [round(random.normalvariate(mean + std, std), 1) for _ in range(n // 2)]
        quantities = [random.randint(1, 5) for _ in range(n)]

        for (p, q) in zip(sorted(prices1 + prices2), quantities):
            if p > mean:
                order = Order(round(p, 1), q, 'ask', None)
                self.order_book['ask'].append(order)
            else:
                order = Order(p, q, 'bid', None)
                self.order_book['bid'].push(order)

    def _clear_book(self):
        """
        **(UNUSED)** Clear order book from orders with 0 quantity.
        """
        self.order_book['bid'] = OrderList.from_list([order for order in self.order_book['bid'] if order.qty > 0])
        self.order_book['ask'] = OrderList.from_list([order for order in self.order_book['ask'] if order.qty > 0])

    def spread(self) -> dict:
        """
        Returns best bid and ask prices as dictionary

        :return: {'bid': float, 'ask': float}
        """
        if self.order_book['bid'] and self.order_book['ask']:
            return {'bid': self.order_book['bid'].first.price, 'ask': self.order_book['ask'].first.price}
        raise Exception(f'{self.name}: There no either bid | ask orders')

    def spread_volume(self) -> dict:
        """
        **(UNUSED)** Returns best bid and ask volumes as dictionary

        :return: {'bid': float, 'ask': float}
        """
        if self.order_book['bid'] and self.order_book['ask']:
            return {'bid': self.order_book['bid'].first.qty, 'ask': self.order_book['ask'].first.qty}
        raise Exception(f'There no either bid or ask orders')

    def price(self) -> float:
        """
        Returns current stock price as mean between best bid and ask prices
        """
        spread = self.spread()
        if spread:
            return round((spread['bid'] + spread['ask']) / 2, 1)
        raise Exception(f'Price cannot be determined, since no orders either bid or ask')

    def ob_imb(self) -> float:
        """
        Returns orderbook imbalance in range [-1, 1]
        """

        if not self.order_book['bid'] or not self.order_book['ask']:
            raise Exception(f'There no either bid or ask orders')

        b = self.order_book['bid'].first.qty
        a = self.order_book['ask'].first.qty

        return (b - a) / (b + a)

    def norm_spread(self) -> float:
        """
        Returns normalized spread
        """
        if not self.order_book['bid'] or not self.order_book['ask']:
            raise Exception(f'There no either bid or ask orders')

        b = self.order_book['bid'].first.price
        a = self.order_book['ask'].first.price

        return (a - b) / ((b + a) / 2)

    def smart_price(self) -> float:
        """
        Returns smart price: average of the bid and ask prices weighted according to their inverse volume
        """
        if not self.order_book['bid'] or not self.order_book['ask']:
            raise Exception(f'There no either bid or ask orders')

        b = self.order_book['bid'].first
        a = self.order_book['ask'].first

        return (b.price * b.qty + a.price * a.qty) / (b.qty + a.qty) / ((a.price + b.price) / 2) - 1

    def ba_imb(self) -> float:
        """
        Returns bid-ask imbalance:
        """

        if not self.order_book['bid'] or not self.order_book['ask']:
            raise Exception(f'There no either bid or ask orders')

        return self.order_book['bid'].first.qty - self.order_book['ask'].first.qty

    def trade_sign(self) -> float:
        """
         A feature measuring whether buyers or sellers crossed the spread more frequently in recent executions.
         More buys = 1
         More sells = -1
        """
        if not len(self.last_trades):
            return 0

        buy_number = len([order for order in self.last_trades if order['order_type'] == 'bid'])
        sell_number = len(self.last_trades) - buy_number

        return 1 if buy_number > sell_number else -1

    def signed_tx_vol(self) -> float:
        """
        A signed quantity indicating the number of shares bought in the last tick minus number of shares sold in the last tick
        """
        if not len(self.last_trades):
            return 0

        buy_volume = sum([order['qty'] for order in self.last_trades if order['order_type'] == 'bid'])
        sell_volume = sum([order['qty'] for order in self.last_trades if order['order_type'] == 'ask'])
        # print([order.qty for order in self.last_orders])
        return (buy_volume - sell_volume) / (buy_volume + sell_volume)

    def last_volume(self) -> float:
        """
        Just volume of the tick
        """
        if not len(self.last_trades):
            return 0

        return sum([order['qty'] for order in self.last_trades])

    def pret(self) -> float:
        """
        Calculate past returns in basis points
        """

        # trade_sum = sum([order['price'] * order['qty'] for order in self.last_trades])
        # weight_sum = sum([order['qty'] for order in self.last_trades])
        # if not weight_sum:
        #     return 0

        current_price = (self.order_book['bid'].first.price + self.order_book['ask'].first.price) / 2

        if not self.last_price:
            self.last_price = current_price
            return 0

        past_returns = (current_price / self.last_price - 1) * 10000
        self.last_price = current_price
        return past_returns

    def aggressive_volume_percentage(self, side: int = 0):
        """
        Aggressive order percentage
        :param side: 0 - sells, 1 - buy
        """

        if not side:
            volume = sum([order['qty'] for order in self.last_trades if order['order_type'] == 'ask'])
            orders = [order for order in self.last_trades if order['order_type'] == 'ask']
        else:
            volume = sum([order['qty'] for order in self.last_trades if order['order_type'] == 'bid'])
            orders = [order for order in self.last_trades if order['order_type'] == 'bid']

        return sum([order['qty'] / volume for order in orders if order['qty'] / volume > self.aggr_baseline])

    def dividend(self, access: int = None) -> list | float | int:
        """
        :param access:
        - **None:** return float or int (current dividend)
        - **0:** return list of dividends (only current dividend)
        - **int > 0:** return list of dividends (current dividend and n future)

        :returns: either
        - **for stocks:** current dividend or *access* future dividends (if called by trader).
        - **for others:** returns 0.
        """
        if self.asset.type != 'Stock':
            return 0
        if access is None:  # both None and 0 (see Fundamentalist __init__)
            return self.asset.dividend
        return [self.asset.dividend, *self.asset.dividend_book[:access]]

    def limit_order(self, order: Order):
        bid, ask = self.spread().values()
        t_cost = self.transaction_cost
        if not bid or not ask:
            return
        if not order.qty:
            return

        if order.order_type == 'bid':
            if order.price >= ask:
                order = self.order_book['ask'].fulfill(order, t_cost)
            if order.qty > 0:
                self.order_book['bid'].insert(order)
            return

        elif order.order_type == 'ask':
            if order.price <= bid:
                order = self.order_book['bid'].fulfill(order, t_cost)
            if order.qty > 0:
                self.order_book['ask'].insert(order)

    def market_order(self, order: Order) -> Order:
        t_cost = self.transaction_cost
        if not order.qty:
            return order

        self.last_trades.append({"price": order.price, "qty": order.qty, "order_type": order.order_type})
        
        if order.order_type == 'bid':
            order = self.order_book['ask'].fulfill(order, t_cost)
        elif order.order_type == 'ask':
            order = self.order_book['bid'].fulfill(order, t_cost)
        return order

    def cancel_order(self, order: Order):
        if order.order_type == 'bid':
            self.order_book['bid'].remove(order)
        elif order.order_type == 'ask':
            self.order_book['ask'].remove(order)
