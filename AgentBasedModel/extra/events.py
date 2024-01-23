from __future__ import annotations

from AgentBasedModel.traders import SingleTrader, Universalist, Fundamentalist, MarketMaker1D
from AgentBasedModel.utils.orders import Order
from itertools import chain


class Event:
    def __init__(self, idx: int, it: int):
        """Event that is activated on specific exchange, at specific iteration

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        """
        self.it = it            # Iteration to activate
        self.idx = idx          # ExchangeAgent id
        self.asset = None       # Asset instance
        self.exchange = None    # Exchange instance
        self.simulator = None   # Simulator instance

    def __repr__(self):
        return f'empty (exchange={self.idx}, it={self.it})'

    def call(self, it: int) -> bool:
        """Checks if iteration to activate

        :param it: current iteration
        :raises Exception: Event is not linked to Simulator
        :return: True - pass, False - activate
        """
        if self.simulator is None:
            raise Exception('No simulator instance found')
        if it != self.it:
            return True
        return False

    def link(self, simulator):
        """Links Event to Simulator and ExchangeAgent

        :param simulator: Simulator instance
        :return: Event instance
        """
        exchanges = {exchange.id: exchange for exchange in simulator.exchanges}
        
        self.exchange = exchanges[self.idx]
        self.asset = self.exchange.asset
        self.simulator = simulator
        return self


class FundamentalPriceShock(Event):
    def __init__(self, idx: int, it: int, price_change: int | float):
        """Change fundamental price of traded asset for all exchanges

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param price_change: fundamental price change (nominal)
        """
        super().__init__(idx, it)
        self.dp = round(price_change, 1)

    def __repr__(self):
        return f'fundamental price shock (asset={self.asset.idx}, it={self.it}, dp={self.dp})'

    def call(self, it: int):
        if super().call(it):
            return
        divs = self.asset.dividend_book  # link to dividend book
        rf = self.exchange.risk_free_rate         # risk-free rate

        self.asset.dividend += self.dp * rf
        self.asset.dividend_book = [div + self.dp * rf for div in divs]


class MarketPriceShock(Event):
    def __init__(self, idx: int, it: int, price_change: int | float):
        """Change market price of traded asset on a specific exchange

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param price_change: market price change (nominal)
        """
        super().__init__(idx, it)
        self.dp = round(price_change, 1)

    def __repr__(self):
        return f'market price shock (exchange={self.idx}, it={self.it}, dp={self.dp})'

    def call(self, it: int):
        if super().call(it):
            return

        book = self.exchange.order_book
        for order in chain(*book.values()):
            order.price += self.dp


class LiquidityShock(Event):
    def __init__(self, idx: int, it: int, volume_change: int| float):
        """Make a large market order on a specific exchange

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param volume_change: market order volume (nominal)
        """
        super().__init__(idx, it)
        self.dv = round(volume_change)

    def __repr__(self):
        return f'liquidity shock (exchange={self.idx}, it={self.it}, dv={self.dv})'

    def call(self, it: int):
        if super().call(it):
            return
        pseudo_trader = SingleTrader(self.exchange, 1e6, int(1e4))
        if self.dv < 0:  # buy
            pseudo_trader._buy_market(abs(self.dv))
        else:  # sell
            pseudo_trader._sell_market(abs(self.dv))


class InformationShock(Event):
    def __init__(self, idx: int, it: int, access: int):
        """Change access attribute of all Fundamentalists on a specific exchange

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param access: value to set Fundamentalists' number of known future dividends
        """
        super().__init__(idx, it)
        self.access = access

    def __repr__(self):
        return f'information shock (exchange={self.idx}, it={self.it}, access={self.access})'

    def call(self, it: int):
        if super().call(it):
            return
        for trader in self.simulator.traders:
            if type(trader) in (Universalist, Fundamentalist):
                trader.access = self.access


class MarketMakerIn(Event):
    def __init__(self, idx: int, it: int, **kwargs):
        """Add MarketMaker to a specific exchange. The MarketMaker is not linked to SimulatorInfo.
        MarketMaker is removed with Event: MarketMarketOut.

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param **kwargs: MarketMaker initialization parameters
        """
        super().__init__(idx, it)
        self.maker = None  # MarketMaker instance
        self.kwargs = kwargs if kwargs else {'cash': 10**3, 'assets': 0, 'softlimit': 100}

    def __repr__(self):
        return f'market maker in (exchange={self.idx}, it={self.it}, softlimit={self.kwargs["softlimit"]})'

    def call(self, it: int):
        if super().call(it):
            return

        self.maker = MarketMaker1D(self.exchange, **self.kwargs)
        self.simulator.traders.append(self.maker)


class MarketMakerOut(Event):
    def __init__(self, idx: int, it: int):
        """Remove MarketMaker from a specific exchange. The MarketMaker is removed only
        such that was introduced with Event: MarketMakerIn. Cannot remove regular MarketMakers
        that were initialized through traders parameter in the Simulator. If multiple MarketMakers
        were introduced with MarketMakerIn, then the removal is conducted randomly.

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param **kwargs: MarketMaker initialization parameters
        """
        super().__init__(idx, it)

    def __repr__(self):
        return f'market maker out (exchange={self.idx}, it={self.it})'

    def call(self, it: int):
        if super().call(it):
            return

        # Find first MarketMaker added by MarketMakerIn
        maker = None
        for event in self.simulator.events:
            if (
                    (event.idx == self.idx)         # Exchange id check
                and (type(event) == MarketMakerIn)  # Event type check
                and (event.it < self.it)            # MarketMakerIn has been executed
            ):
                maker = event.maker
        
        # Remove first MarketMaker from Simulator's traders list
        for i, trader in enumerate(self.simulator.traders):
            if trader.id == maker.id:
                del self.simulator.traders[i]
                break
        
        # Remove remaining orders from the book
        for order in maker.orders:
            maker._cancel_order(order)


class TransactionCost(Event):
    def __init__(self, idx: int, it: int, cost: float):
        """Set transaction cost for a specific exchange

        :param idx: ExchangeAgent id
        :param it: iteration to activate
        :param cost: transaction cost to set (fraction)
        """
        super().__init__(idx, it)
        self.cost = cost

    def __repr__(self):
        return f'transaction cost (exchange={self.idx}, it={self.it}, cost={self.cost}%)'

    def call(self, it: int):
        if super().call(it):
            return

        self.exchange.transaction_cost = self.cost
