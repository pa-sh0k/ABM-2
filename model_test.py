from AgentBasedModel import *
import random
from config import seed


random.seed(seed)

# Define parameters
risk_free_rate = 5e-4
price = 100
dividend = price * risk_free_rate

assets = [
    Stock(dividend) for _ in range(1)
]

exchanges = [
    ExchangeAgent(assets[0], risk_free_rate) for i in range(1)  # single asset
]


def yield_simulator(pred_trader):
    traders = [
        *[Random(exchanges[0]) for _ in range(5)],
        *[Fundamentalist(exchanges[0]) for _ in range(2)],
        *[Chartist2D(exchanges) for _ in range(2)],
        *[MarketMaker2D(exchanges) for _ in range(1)],
        *[pred_trader]
    ]
    simulator = Simulator(**{
        'assets': assets,
        'exchanges': exchanges,
        'traders': traders,
        'events': []
    })

    return simulator


# Initialize objects

features = ['smart_pr', 'tr_signs']

pred_trader = PredictingTrader(exchanges[0], features)


for _ in range(7):
    simulator = yield_simulator(pred_trader)
    simulator.simulate(500, silent=False)
    pred_trader.train(0)
    seed += 2

pred_trader.active = True

simulator = yield_simulator(pred_trader)
simulator.simulate(250, silent=False)

print(f"FINAL ASSETS: {pred_trader.assets}")
print(f"FINAL CASH: {pred_trader.cash}")
print(f"FINAL VALUE: {pred_trader.cash + pred_trader.assets * simulator.info.prices[0][-1] }")