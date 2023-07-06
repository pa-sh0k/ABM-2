from AgentBasedModel import *

exchange = ExchangeAgent(volume=1000)
simulator = Simulator(**{
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
