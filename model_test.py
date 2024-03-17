from AgentBasedModel import *
import random
from config import seed
import matplotlib.pyplot as plt
import json
from utils import get_classification_metrics

random.seed(seed)

features = ['smart_pr', 'tr_signs', 'prets', 'norm_spread']
methods = ['rolling_ob_imbalance', 'rolling_signed_volume', 'window_aggressive_vol']
args = [0, 0, 0]
# methods = []
# args = []


class Simulation:
    def __init__(self, random_count, fundamentalist_count, chartist_count, mm_count, pred_trader_count, features, methods, args, train_epochs, trade_epochs, tick_number=500, daily_risk_free_rate=2.5e-4, price=100):
        self.tick_number = tick_number
        self.risk_free_rate = daily_risk_free_rate / tick_number
        self.starting_price = price
        self.dividend = price * self.risk_free_rate * 1.1
        self.assets = [Stock(self.dividend) for _ in range(1)]
        self.exchanges = [ExchangeAgent(self.assets[0], self.risk_free_rate, mean=price) for i in range(1)]
        self.pred_traders = [PredictingTrader(self.exchanges[0], features, methods, args) for _ in range(pred_trader_count)]
        self.random_count = random_count
        self.fundamentalist_count = fundamentalist_count
        self.chartist_count = chartist_count
        self.mm_count = mm_count
        self.train_epochs = train_epochs
        self.trade_epochs = trade_epochs

    def calculate_results(self, simulator, inital_value):
        market_price_change = 100 * (simulator.info.prices[0][-1] - simulator.info.prices[0][0]) / simulator.info.prices[0][0]

        results = []
        for pred_trader in self.pred_traders:
            pred_trader_final_value = pred_trader.cash + pred_trader.assets * simulator.info.prices[0][-1]
            pred_trader_pnl = 100 * (pred_trader_final_value - inital_value) / inital_value
            results.append(pred_trader_pnl)

        accuracy, precision, recall = get_classification_metrics(self.pred_traders[0])

        return market_price_change, results, accuracy

    def yield_simulator(self):
        self.traders = [
            *[Random(self.exchanges[0]) for _ in range(self.random_count)],
            *[Fundamentalist(self.exchanges[0]) for _ in range(self.fundamentalist_count)],
            *[Chartist2D(self.exchanges) for _ in range(self.chartist_count)],
            *[MarketMaker2D(self.exchanges) for _ in range(self.mm_count)],
            *self.pred_traders
        ]
        simulator = Simulator(**{
            'assets': self.assets,
            'exchanges': self.exchanges,
            'traders': self.traders,
            'events': []
        })

        return simulator

    def train(self):
        global seed
        for _ in range(self.train_epochs):
            simulator = self.yield_simulator()
            simulator.simulate(self.tick_number, silent=False)
            for pred_trader in self.pred_traders:
                pred_trader.train(0)
            seed += 2

    def trade(self):
        for pred_trader in self.pred_traders:
            pred_trader.active = True
        initial_value = self.pred_traders[0].cash
        simulator = self.yield_simulator()
        simulator.simulate(500 * self.trade_epochs, silent=False)
        market_change, results, accuracy = self.calculate_results(simulator, initial_value)
        print(f"MARKET CHANGE: {market_change}")
        print(f"TRADER RESULTS: {results}")
        print(f"ACCURACY: {accuracy}")
        return market_change, results, accuracy


def create_plot(parameter_string, mode='pnl'):
    with open('results.json', 'r') as f:
        res = json.loads(f.read())

    data = res[parameter_string][mode]
    epochs = list(range(1, len(data)+1))
    plt.title(parameter_string)
    plt.xlabel('Training Epochs')
    plt.ylabel('% PnL' if mode == 'pnl' else 'Accuracy')
    plt.plot(epochs, data)
    plt.show()


def simulate_and_save(parameter_string):
    random_count, fundamentalist_count, chartist_count, mm_count, pred_trader_count = [int(item) for item in parameter_string.split('-')]

    simulation = Simulation(random_count, fundamentalist_count, chartist_count, mm_count, pred_trader_count, features, methods, args, 7, 1)
    simulation.train()
    market_change, results, accuracy = simulation.trade()
    with open('results.json', 'r') as f:
        res = json.loads(f.read())

    res[parameter_string]["accuracy"].append(accuracy)
    res[parameter_string]["pnl"].append(results[0])

    with open('results.json', 'w') as f:
        f.write(json.dumps(res))

    return simulation


# siml = simulate_and_save("30-5-5-10-1")
# create_plot("30-10-5-5-1", "accuracy")
# create_plot("30-10-5-5-1", "pnl")