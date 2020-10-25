import pyRofex
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

""" this programs is designed to receive and print real time data
 to show it in the screen and tell you, base on the signal, if you
 have to take a long or short position in the instruemnt """


pyRofex.initialize(user="XXXXXXX",
                   password="XXXXXXX"
                   account="XXXXXXX",
                   environment=pyRofex.Environment.REMARKET)

instruments = ['RFX20Dic20']

prices = pd.DataFrame(columns=["Time", "Bid", "Offer", "Last"])
prices.set_index('Time', inplace=True)

def market_data_handler(message):
    global prices
    last = None if not message["marketData"]["LA"] else message["marketData"]["LA"]["price"]
    prices.loc[datetime.fromtimestamp(message["timestamp"]/1000)] = [
        message["marketData"]["BI"][0]["price"],
        message["marketData"]["OF"][0]["price"],
        last
    ]
    chartboard()

entries=[pyRofex.MarketDataEntry.BIDS,
        pyRofex.MarketDataEntry.OFFERS,
        pyRofex.MarketDataEntry.LAST]

# 3-Initialize Websocket Connection with the handlers
pyRofex.init_websocket_connection(market_data_handler=market_data_handler)
pyRofex.market_data_subscription(tickers=instruments,
                                 entries=entries)

prices = prices.append(prices)

def chartboard():
    bot = pd.DataFrame(prices['Last'].values, columns=['Last'], index=prices.index)
    bot['SMA'] = prices['Last'].rolling(round(len(bot.index)*0.05), min_periods=1).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot['Last'] > bot['SMA'], 1.0, 0.0)  # use a conditional
    bot['positions'] = bot['signal'].diff()
    print(bot.tail(1))