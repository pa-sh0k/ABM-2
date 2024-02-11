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

features = ['smart_pr', 'tr_signs']

pred_trader = PredictingTrader(exchanges[1], features)
traders = [
    *[Random(exchanges[randint(0, 2)])         for _ in range(20)],
    *[Fundamentalist(exchanges[randint(0, 2)]) for _ in range(20)],
    *[Chartist2D(exchanges)                    for _ in range(20)],
    *[MarketMaker2D(exchanges)                 for _ in range(4)],
    *[pred_trader]
]

for _ in range(5):
    simulator = Simulator(**{
        'assets': assets,
        'exchanges': exchanges,
        'traders': traders,
        'events': []
    })
    simulator.simulate(250, silent=False)
    pred_trader.train(1)
    seed += 2

pred_trader.active = True

simulator = Simulator(**{
        'assets': assets,
        'exchanges': exchanges,
        'traders': traders,
        'events': []
    })
simulator.simulate(250, silent=False)

print(f"FINAL ASSETS: {pred_trader.assets}")
print(f"FINAL CASH: {pred_trader.cash}")
# initial cash for prediction trader is 100
