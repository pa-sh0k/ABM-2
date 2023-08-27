from AgentBasedModel import *
from AgentBasedModel.extra import *
from AgentBasedModel.visualization import (
    plot_price,
    plot_price_fundamental
)
from random import randint

# Define parameters
risk_free_rate = 5e-4
price = 100
dividend = price * risk_free_rate

# Initialize objects
assets = [
    Stock(dividend) for _ in range(3)
]
exchanges = [
    ExchangeAgent(assets[0], risk_free_rate) for i in range(3)  # single asset
]
traders = [
    *[Random(exchanges[randint(0, 2)])         for _ in range(20)],
    *[Fundamentalist(exchanges[randint(0, 2)]) for _ in range(20)],
    *[Chartist2D(exchanges)                    for _ in range(20)],
    *[MarketMaker2D(exchanges)                 for _ in range(4)]
]

# Run simulation
simulator = Simulator(**{
    'assets': assets,
    'exchanges': exchanges,
    'traders': traders,
    'events': [MarketPriceShock(0, 200, -10)]
})

info = simulator.info
simulator.simulate(500, silent=False)

plot_price(info, None, rolling=1)
