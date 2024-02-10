from AgentBasedModel import *
from AgentBasedModel.extra import *
from AgentBasedModel.visualization import (
    plot_price,
    plot_price_fundamental,
    plot_orderbook_with_depth,
    plot_feature_chronology,
    plot_feature_distributions
)
from AgentBasedModel.utils import ob_imbalance

from random import randint
import random
from config import seed

random.seed(seed)

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

features = ['smart_pr', 'prets', 'tr_signs']

traders = [
    *[Random(exchanges[randint(0, 2)])         for _ in range(20)],
    *[Fundamentalist(exchanges[randint(0, 2)]) for _ in range(20)],
    *[Chartist2D(exchanges)                    for _ in range(20)],
    *[MarketMaker2D(exchanges)                 for _ in range(4)],
    *[PredictingTrader(exchanges[1], features)           for _ in range(1)]
]

# Run simulation
simulator = Simulator(**{
    'assets': assets,
    'exchanges': exchanges,
    'traders': traders,
    'events': [MarketPriceShock(0, 200, -10)]
})

plot_orderbook_with_depth(0.02, simulator.info, exchange_ind=1)

simulator.simulate(150, silent=False)

# plot_feature_chronology(simulator.info, 1)
# plot_feature_distributions(simulator.info, 1)

# print(len(simulator.info.trades[0]))

# plot_price(simulator.info, None, rolling=1)
