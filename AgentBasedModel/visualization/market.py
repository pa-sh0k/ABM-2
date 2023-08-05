from AgentBasedModel.simulator import SimulatorInfo
import AgentBasedModel.utils.math as math

import matplotlib.pyplot as plt
import numpy as np


def plot_price(
        info:    SimulatorInfo,
        idx:     int   = None,
        spread:  bool  = False,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock market price

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param spread: bid-ask prices, defaults to False (only when idx is not None)
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title('Stock Market price') if rolling == 1 else plt.title(f'Stock Price (MA {rolling})')
    plt.xlabel('Iterations')
    plt.ylabel('Price')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = math.rolling(info.prices[idx], rolling)
        iterations = range(rolling - 1, len(values) + rolling - 1)
        
        plt.plot(iterations, values, color='black', label=exchange.name)

        if spread:
            v1 = math.rolling([el['bid'] for el in info.spreads[idx]], rolling)
            v2 = math.rolling([el['ask'] for el in info.spreads[idx]], rolling)

            plt.plot(iterations, v1, label='bid', color='green')
            plt.plot(iterations, v2, label='ask', color='red')

    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            values = math.rolling(info.prices[k], rolling)
            iterations = range(rolling - 1, len(values) + rolling - 1)

            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()


def plot_price_fundamental(
        info:    SimulatorInfo,
        idx:     int   = None,
        access:  int   = 0,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock market price and fundamental price (single asset)

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :parap access: Fundamentalist's number of known dividends, defaults to 0
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(
              'Stock Market and Fundamental price' if rolling == 1
        else f'Stock Market and Fundamental price (MA {rolling})'
    )
    plt.xlabel('Iterations')
    plt.ylabel('Price')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        m_values = math.rolling(info.prices[idx], rolling)                     # market prices
        f_values = math.rolling(info.fundamental_value(idx, access), rolling)  # fundamental prices
        iterations = range(rolling - 1, len(m_values) + rolling - 1)

        plt.plot(iterations, m_values, color='tab:blue', alpha=1,  ls='-',  label=f'{exchange.name}: market')
        plt.plot(iterations, f_values, color='black',    alpha=.6, ls='--', label=f'{exchange.name}: fundamental')
    
    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            m_values = math.rolling(info.prices[k], rolling)                   # market prices
            iterations = range(rolling - 1, len(m_values) + rolling - 1)
            plt.plot(iterations, m_values, ls='-', label=f'{v.name}: market')

        f_values = math.rolling(info.fundamental_value(0, access), rolling)    # fundamental prices
        plt.plot(iterations, f_values, color='black', alpha=.6, ls='--', label=f'fundamental')

    plt.legend()
    plt.show()


def plot_price_fundamental_m(
        info:    SimulatorInfo,
        idx:     int   = None,
        access:  int   = 0,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock market price and fundamental price (multiple assets)

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :parap access: Fundamentalist's number of known dividends, defaults to 0
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(
              'Stock Market and Fundamental price' if rolling == 1
        else f'Stock Market and Fundamental price (MA {rolling})'
    )
    plt.xlabel('Iterations')
    plt.ylabel('Price')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        m_values = math.rolling(info.prices[idx], rolling)                     # market prices
        f_values = math.rolling(info.fundamental_value(idx, access), rolling)  # fundamental prices
        iterations = range(rolling - 1, len(m_values) + rolling - 1)

        plt.plot(iterations, m_values, color='tab:blue', alpha=1, ls='-',   label=f'{exchange.name}: market')
        plt.plot(iterations, f_values, color='tab:blue', alpha=.4, ls='--', label=f'{exchange.name}: fundamental')
    
    # plot N exchanges
    else:
        colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(info.exchanges))))
        
        for k, v in info.exchanges.items():
            m_values = math.rolling(info.prices[k], rolling)                     # market prices
            f_values = math.rolling(info.fundamental_value(k, access), rolling)  # fundamental prices
            iterations = range(rolling - 1, len(m_values) + rolling - 1)
            
            c = next(colors)
            plt.plot(iterations, m_values, color=c, alpha=1, ls='-',   label=f'{v.name}: market')
            plt.plot(iterations, f_values, color=c, alpha=.4, ls='--', label=f'{v.name}: fundamental')

    plt.legend()
    plt.show()


def plot_arbitrage(
        info:    SimulatorInfo,
        idx:     int   = None,
        access:  int   = 0,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot % difference between stock market price and fundamental price

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :parap access: Fundamentalist's number of known dividends, defaults to 0
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(
              'Stock Market and Fundamental price difference %' if rolling == 1
        else f'Stock Market and Fundamental price difference % (MA {rolling})'
    )
    plt.xlabel('Iterations')
    plt.ylabel('Difference %')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        m_values = math.rolling(info.prices[idx], rolling)                     # market prices
        f_values = math.rolling(info.fundamental_value(idx, access), rolling)  # fundamental prices
        values = [
            100 * (m_values[i] - f_values[i]) / m_values[i]                    # arbitrage opportunity %
            for i in range(len(m_values))
        ]
        iterations = range(rolling - 1, len(values) + rolling - 1)

        plt.plot(iterations, values, color='black', label=exchange.name)
    
    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            m_values = math.rolling(info.prices[k], rolling)                     # market prices
            f_values = math.rolling(info.fundamental_value(k, access), rolling)  # fundamental prices
            values = [
                100 * (m_values[i] - f_values[i]) / m_values[i]                  # arbitrage opportunity %
                for i in range(len(m_values))
            ]
            iterations = range(rolling - 1, len(values) + rolling - 1)
            
            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()


def plot_dividend(
        info:    SimulatorInfo,
        idx:     int   = None,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock dividend

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title('Stock Dividend') if rolling == 1 else plt.title(f'Stock Dividend (MA {rolling})')
    plt.xlabel('Iterations')
    plt.ylabel('Dividend')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = math.rolling(info.dividends[idx], rolling)
        iterations = range(rolling - 1, len(values) + rolling - 1)
        
        plt.plot(iterations, values, color='black', label=exchange.name)

    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            values = math.rolling(info.dividends[k], rolling)
            iterations = range(rolling - 1, len(values) + rolling - 1)

            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()


def plot_liquidity(
        info:    SimulatorInfo,
        idx:     int   = None,
        rolling: int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock liquidity

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param rolling: MA applied to list, defaults to 1
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title('Stock Liquidity') if rolling == 1 else plt.title(f'Stock Liquidity (MA {rolling})')
    plt.xlabel('Iterations')
    plt.ylabel('Liquidity')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = math.rolling(info.liquidity(idx), rolling)
        iterations = range(rolling - 1, len(values) + rolling - 1)
        
        plt.plot(iterations, values, color='black', label=exchange.name)

    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            values = math.rolling(info.liquidity(k), rolling)
            iterations = range(rolling - 1, len(values) + rolling - 1)

            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()


def plot_volatility_price(
        info:    SimulatorInfo,
        idx:     int   = None,
        window:  int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock price volatility

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param window: sample size to calculate std, > 1, defaults to 5
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(f'Stock Price Volatility (WINDOW: {window})')
    plt.xlabel('Iterations')
    plt.ylabel('Price Volatility')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = info.price_volatility(idx, window)
        iterations = range(window, len(values) + window)
        
        plt.plot(iterations, values, color='black', label=exchange.name)

    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            values = info.price_volatility(k, window)
            iterations = range(window, len(values) + window)

            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()


def plot_volatility_return(
        info:    SimulatorInfo,
        idx:     int   = None,
        window:  int   = 1,
        figsize: tuple = (6, 6)
    ):
    """Lineplot stock return volatility

    :param info: SimulatorInfo instance
    :param idx: ExchangeAgent id, defaults to None (all exchanges)
    :param window: sample size to calculate std, > 1, defaults to 5
    :param figsize: figure size, defaults to (6, 6)
    """
    plt.figure(figsize=figsize)
    plt.title(f'Stock Return Volatility (WINDOW: {window})')
    plt.xlabel('Iterations')
    plt.ylabel('Return Volatility')

    # plot 1 exchange
    if idx is not None:
        exchange = info.exchanges[idx]
        values = info.return_volatility(idx, window)
        iterations = range(window, len(values) + window)
        
        plt.plot(iterations, values, color='black', label=exchange.name)

    # plot N exchanges
    else:
        for k, v in info.exchanges.items():
            values = info.return_volatility(k, window)
            iterations = range(window, len(values) + window)

            plt.plot(iterations, values, label=v.name)

    plt.legend()
    plt.show()
