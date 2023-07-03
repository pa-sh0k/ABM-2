from AgentBasedModel import *
from AgentBasedModel.utils.math import *

exchange = ExchangeAgent(volume=1000)
simulator = Simulator(**{
    'exchange': exchange,
    'traders': [Fundamentalist(exchange, 10**3) for _ in range(10)],
    'events': [MarketPriceShock(200, -20)]
})

info = simulator.info
simulator.simulate(500, silent=False)
