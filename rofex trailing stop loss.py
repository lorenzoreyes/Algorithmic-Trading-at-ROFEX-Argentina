import datetime as dt
import pandas as pd
import numpy as np
import pyRofex

pyRofex.initialize(user="XXXXXXXX",
                   password="XXXXXX",
                   account="XXXXXXXX",
                   environment=pyRofex.Environment.REMARKET)

end = dt.date.today()
start = dt.date.today() - dt.timedelta(days=1)
historic_trades = pyRofex.get_trade_history(ticker=input(), start_date=start, end_date=end)
trades = pd.DataFrame(historic_trades['trades']) # get dataframe from trades dictionary

# re-structure data in a clean dataframe
bot = pd.DataFrame(trades['price'].values, columns=['price'], index=trades['datetime'])
bot['SMA'] = bot['price'].rolling(round(len(bot)*0.05), min_periods=1).mean() # a signal to test
# Trailing Stop-Loss Part. As a warranty
bot['Highest'] = bot['price'].rolling(round(len(bot)*0.05), min_periods=1).max() 
bot['Stop_Loss'] = bot['Highest'].rolling(round(len(bot)*0.05), min_periods=1).min() 
bot['Exit'] = bot['price'] < bot['Stop_Loss']
bot['signal'] = 0.0
bot['signal'] = np.where(bot['SMA'] > bot['Stop_Loss'], 1.0, 0.0) # use a conditional integrating Stop Loss
bot['positions'] = bot['signal'].diff() # check changes of positions entries
print(bot.tail(1))
bot.iloc[:,:4].plot(grid=True)

# chequeo entradas y salidas
ordenes = bot['price'] * bot['positions']
precio_entrada = ordenes[ordenes>=1.0]
precio_salida = ordenes[ordenes<=-1.0] * -1.0 
book = pd.DataFrame(precio_entrada, columns=['entrada'])
book['salida'] = precio_salida.values 
book['resultado'] = book['salida'] - book['entrada']
