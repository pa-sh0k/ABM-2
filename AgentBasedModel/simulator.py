from typing import Type, List

from AgentBasedModel.exchange import ExchangeAgent, Asset
from AgentBasedModel.traders import (
    Trader,
    Universalist,
    Chartist1D,
    Chartist2D,
    Fundamentalist
)
from AgentBasedModel.extra import Event
from AgentBasedModel.utils.math import mean, std, rolling

import random
from tqdm import tqdm


class Simulator:
    """
    Simulator is responsible for launching agents' actions and executing scenarios
    """
    # todo: Only traders are to be passed, trader -> trader.exchange -> trader.exchange.asset. Use dict comprehension to get unique items.
    def __init__(
            self,
            assets:    List[Type[Asset]],
            exchanges: List[ExchangeAgent],
            traders:   List[Type[Trader]],
            events:    List[Type[Event]] = None
        ):
        self.assets = assets
        self.exchanges = exchanges
        self.traders = traders
        self.events = [event.link(self) for event in events] if events else None  # link all events to simulator

        self.info = SimulatorInfo(exchanges, traders)

    def simulate(self, n_iter: int, silent: bool = False) -> object:
        for it in tqdm(range(n_iter), desc='Simulation', disable=silent):
            # Call scenario
            if self.events:
                for event in self.events:
                    event.call(it)

            # Capture current info
            self.info.capture()

            # Call Traders
            random.shuffle(self.traders)

            for trader in self.traders:
                if type(trader) == Universalist:
                    trader.change_strategy(self.info)
                if type(trader) in (Universalist, Chartist1D, Chartist2D):
                    trader.change_sentiment(self.info)

                trader.call()    # trader's action
            
            # Pay Traders
            for trader in self.traders:
                trader.income()  # trader's dividend and interest

            # Update assets
            for asset in self.assets:
                asset.update()  # generate next dividend

        return self


class SimulatorInfo:
    """
    SimulatorInfo is responsible for capturing data during simulating
    """
    def __init__(
            self,
            exchanges: List[ExchangeAgent],
            traders:   List[Type[Trader]],
        ):
        self.exchanges = {exchange.id: exchange for exchange in exchanges}
        self.traders   = {trader.id: trader for trader in traders}

        # Market Statistics
        self.prices    = {idx: list() for idx in self.exchanges.keys()}  # exchange: price at the end of iteration
        self.spreads   = {idx: list() for idx in self.exchanges.keys()}  # exchange: bid-ask spreads
        self.dividends = {idx: list() for idx in self.exchanges.keys()}  # exchange: dividend paid at each iteration
        self.orders    = {idx: list() for idx in self.exchanges.keys()}  # exchange: order book statistics

        # Agent statistics
        self.cash       = {idx: list() for idx in self.traders.keys()}  # trader: cash
        self.assets     = {idx: list() for idx in self.traders.keys()}  # trader: number of assets
        self.equities   = {idx: list() for idx in self.traders.keys()}  # trader: equity
        self.types      = {idx: list() for idx in self.traders.keys()}  # trader: current type
        self.sentiments = {idx: list() for idx in self.traders.keys()}  # trader: current sentiment
        self.returns    = {idx: list() for idx in self.traders.keys()}  # trader: return (price change + dividend)

        # self.returns = [{tr_id: 0 for tr_id in self.traders.keys()}]  # agent: return (price change + dividend)

    def capture(self):
        """
        Method called at the end of each iteration to capture basic info on simulation.

        **Attributes:**

        *Market Statistics*

        - :class:`dict[list[float]]` **prices** --> stock prices on each iteration
        - :class:`dict[list[dict]]` **spreads** --> order book bid-ask pairs on each iteration
        - :class:`dict[list[float]]` **dividends** --> dividend paid on each iteration
        - :class:`dict[list[dict[dict]]]` **orders** --> order book price, volume, quantity stats on each iteration

        *Traders Statistics*

        - :class:`dict[list[dict]]` **equities** --> each agent's equity on each iteration
        - :class:`dict[list[dict]]` **cash** --> each agent's cash on each iteration
        - :class:`dict[list[dict]]` **assets** --> each agent's number of stocks on each iteration
        - :class:`dict[list[dict]]` **types** --> each agent's type on each iteration
        """

        # Market Statistics
        for idx, exchange in self.exchanges.items():
            self.prices[idx].append(exchange.price())
            self.spreads[idx].append(exchange.spread())
            self.dividends[idx].append(exchange.dividend())

            # Order book details
            self.orders[idx].append({
                'quantity': {
                    'bid': len(exchange.order_book['bid']),
                    'ask': len(exchange.order_book['ask'])
                },
                # 'price mean': {
                #     'bid': mean([order.price for order in self.exchange.order_book['bid']]),
                #     'ask': mean([order.price for order in self.exchange.order_book['ask']])
                # },
                # 'price std': {
                #     'bid': std([order.price for order in self.exchange.order_book['bid']]),
                #     'ask': std([order.price for order in self.exchange.order_book['ask']])
                # },
                # 'volume sum': {
                #     'bid': sum([order.qty for order in self.exchange.order_book['bid']]),
                #     'ask': sum([order.qty for order in self.exchange.order_book['ask']])
                # },
                # 'volume mean': {
                #     'bid': mean([order.qty for order in self.exchange.order_book['bid']]),
                #     'ask': mean([order.qty for order in self.exchange.order_book['ask']])
                # },
                # 'volume std': {
                #     'bid': std([order.qty for order in self.exchange.order_book['bid']]),
                #     'ask': std([order.qty for order in self.exchange.order_book['ask']])
                # }
            })

        # Trader Statistics
        for idx, trader in self.traders.items():
            self.cash[idx].append(trader.cash)
            self.assets[idx].append(trader.assets)
            self.equities[idx].append(trader.equity())
            self.types[idx].append(trader.type)

            if len(self.equities[idx]) > 1:
                self.returns[idx].append(
                    (self.equities[idx][-1] - self.equities[idx][-2]) / self.equities[idx][-2]
                )
            if type(trader) in (Chartist1D, Chartist2D, Universalist):
                self.sentiments[idx].append(trader.sentiment)

    def fundamental_value(self, idx: int, access: int = 0) -> list:
        """Fundamental value is calculated using Fundamental trader logic.

        :param idx: ExchangeAgent id
        :param access: Fundamentalist's number of known dividends, defaults to 0
        :return: stock fundamental values
        """
        rf = self.exchanges[idx].risk_free_rate
        divs = [
            *self.dividends[idx],                              # paid dividends
            *self.exchanges[idx].dividend(access)[1:access+1]  # unpaid dividends
        ]

        return [Fundamentalist.evaluate(divs[i:i+access+1], rf) for i in range(len(divs) - access)]

    # todo: roll - deprecated (roll is used only in visualizations)
    def stock_returns(self, idx: int, roll: int = 1) -> list:
        """Stock return is calculated based on: 1) dividend, 2) price change

        :param idx: ExchangeAgent id
        :param roll: MA applied to list, defaults to 1
        :return: stock returns
        """
        p = self.prices[idx]
        div = self.dividends[idx]
        
        r = [
              (p[i+1] - p[i]) / p[i]  # price related return
            + (div[i]) / p[i]         # dividend related return

            for i in range(len(p) - 1)
        ]

        return rolling(r, roll)

    def abnormal_returns(self, idx: int, roll: int = 1) -> list:
        """Stock abnormal return is a return that is greater than risk-free rate

        :param idx: ExchangeAgent id
        :param roll: MA applied to list, defaults to 1
        :return: stock abnormal returns
        """
        rf = self.exchanges[idx].risk_free_rate
        
        r = [r - rf for r in self.stock_returns(idx)]

        return rolling(r, roll)

    def return_volatility(self, idx: int, window: int = 5) -> list:
        """Stock return volatility is calculated as a standard deviation of stock returns 

        :param idx: ExchangeAgent id
        :param window: sample size, > 1, defaults to 5
        :return: stock return volatility
        """

        r = self.stock_returns(idx)

        return [std(r[i:i+window]) for i in range(len(r) - window + 1)]

    def price_volatility(self, idx: int, window: int = 5) -> list:
        """Stock price volatility is calculated as a standard deviation of stock market prices 

        :param idx: ExchangeAgent id
        :param window: sample size, > 1, defaults to 5
        :return: stock price volatility
        """
        
        p = self.prices[idx]

        return [std(p[i:i+window]) for i in range(len(p) - window + 1)]

    def liquidity(self, idx: int, roll: int = 1) -> list:
        """Stock liquidity is calculated as a best-ask, best-bid difference relative to market price

        :param idx: ExchangeAgent id
        :param roll: MA applied to list, defaults to 1
        :return: stock liquidities
        """
        prices = self.prices[idx]
        spreads = [el['ask'] - el['bid'] for el in self.spreads[idx]]

        liq = [spreads[i] / prices[i] for i in range(len(prices))]

        return rolling(liq, roll)
