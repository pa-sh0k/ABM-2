from AgentBasedModel.utils import Order, OrderList
from AgentBasedModel.utils.math import exp
import random

class ExchangeAgent:
    """
    ExchangeAgent implements automatic orders handling within the order book
    """
    id = 0

    def __init__(self, price: float or int = 100, std: float or int = 25, volume: int = 1000, rf: float = 5e-4,
                 transaction_cost: float = 0):
        """
        Creates ExchangeAgent with initialised order book and future dividends

        :param price: stock initial price
        :param std: standard deviation of order prices
        :param volume: number of orders initialised
        :param rf: risk-free rate
        :param transaction_cost: transaction cost on operations for traders
        """
        self.name = f'ExchangeAgent{self.id}'
        self.id = ExchangeAgent.id
        ExchangeAgent.id += 1

        self.order_book = {'bid': OrderList('bid'), 'ask': OrderList('ask')}
        self.dividend_book = list()  # act like queue
        self.risk_free = rf
        self.transaction_cost = transaction_cost
        self._fill_book(price, std, volume, rf * price)  # initialise both order book and dividend book

    def generate_dividend(self):
        """
        Add new dividend to queue and pop last
        """
        # Generate future dividend
        d = self.dividend_book[-1] * self._next_dividend()
        self.dividend_book.append(max(d, 0))  # dividend > 0
        self.dividend_book.pop(0)

    def _fill_book(self, price, std, volume, div: float = 0.05):
        """
        Fill order book with random orders and fill dividend book with future dividends.

        **Order book:** generate prices from normal distribution with *std*, and *price* as center; generate
        quantities for these orders from uniform distribution with 1, 5 bounds. Set bid orders when
        order price is less than *price*, set ask orders when order price is greater than *price*.

        **Dividend book:** add 100 dividends using *_next_dividend* method.
        """
        # Order book
        prices1 = [round(random.normalvariate(price - std, std), 1) for _ in range(volume // 2)]
        prices2 = [round(random.normalvariate(price + std, std), 1) for _ in range(volume // 2)]
        quantities = [random.randint(1, 5) for _ in range(volume)]

        for (p, q) in zip(sorted(prices1 + prices2), quantities):
            if p > price:
                order = Order(round(p, 1), q, 'ask', None)
                self.order_book['ask'].append(order)
            else:
                order = Order(p, q, 'bid', None)
                self.order_book['bid'].push(order)

        # Dividend book
        for i in range(100):
            self.dividend_book.append(max(div, 0))  # dividend > 0
            div *= self._next_dividend()

    def _clear_book(self):
        """
        **(UNUSED)** Clear order book from orders with 0 quantity.
        """
        self.order_book['bid'] = OrderList.from_list([order for order in self.order_book['bid'] if order.qty > 0])
        self.order_book['ask'] = OrderList.from_list([order for order in self.order_book['ask'] if order.qty > 0])

    def spread(self) -> dict or None:
        """
        Returns best bid and ask prices as dictionary

        :return: {'bid': float, 'ask': float}
        """
        if self.order_book['bid'] and self.order_book['ask']:
            return {'bid': self.order_book['bid'].first.price, 'ask': self.order_book['ask'].first.price}
        raise Exception(f'There no either bid or ask orders')

    def spread_volume(self) -> dict or None:
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

    def dividend(self, access: int = None) -> list or float:
        """
        Returns either current dividend or *access* future dividends (if called by trader)

        :param access: the number of future dividends accessed by a trader
        """
        if access is None:
            return self.dividend_book[0]
        return self.dividend_book[:access]

    @classmethod
    def _next_dividend(cls, std=5e-3):
        return exp(random.normalvariate(0, std))

    def limit_order(self, order: Order):
        bid, ask = self.spread().values()
        t_cost = self.transaction_cost
        if not bid or not ask:
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
