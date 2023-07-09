from AgentBasedModel import *

risk_free_rate = 5e-4

price = 100
dividend = price * risk_free_rate

asset = Stock(dividend)

exchange = ExchangeAgent(asset, risk_free_rate, mean=price, n=1000)
simulator = Simulator(**{
    'asset': asset, 
    'exchange': exchange,
    'traders': [
        *[Random(exchange, 10**3)         for _ in range(10)],
        *[Fundamentalist(exchange, 10**3) for _ in range(10)],
        *[Chartist(exchange, 10**3)       for _ in range(10)]
    ],
    'events': [MarketPriceShock(200, -20)]
})

info = simulator.info
simulator.simulate(500, silent=False)

plot_price_fundamental(info)
