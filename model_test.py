from AgentBasedModel import *
from AgentBasedModel.extra import *
from random import randint
import random
from config import seed
from model import iterative_training

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
traders = [
    *[Random(exchanges[randint(0, 2)])         for _ in range(20)],
    *[Fundamentalist(exchanges[randint(0, 2)]) for _ in range(20)],
    *[Chartist2D(exchanges)                    for _ in range(20)],
    *[MarketMaker2D(exchanges)                 for _ in range(4)]
]

# Run simulation
settings = {
    'assets': assets,
    'exchanges': exchanges,
    'traders': traders,
    'events': []
}

model, acc = iterative_training(1, 5, settings)
print(acc)