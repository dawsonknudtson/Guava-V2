import secrets as API
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from termcolor import colored as cl 
from math import floor
from eodhd import APIClient

plt.rcParams['figure.figsize'] = [20, 10]
plt.style.use('fivethirtyeight')

def get_data(ticker, start_date):
    json_resp = APIClient(API.API_KEY).get_eod_historical_stock_market_data(symbol=ticker, period='d', from_date = start_date, order = 'a')
    df = pd.DataFrame(json_resp)
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index)
    return df

ibm = get_data('IBM', '2020-01-01')
ibm.tail()

# Calculate Values of RSI with 14-day period

def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(abs(ret[i]))
        else:
            up.append(ret[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com=lookback - 1, adjust=False).mean()
    down_ewm = down_series.ewm(com=lookback - 1, adjust=False).mean()
    rs = up_ewm / down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    return rsi_df[3:]

ibm['rsi_14'] = get_rsi(ibm['close'], 14)
ibm = ibm.dropna()
ibm.tail()

# Plot RSI and Close Price

ax1 = plt.subplot2g((10,1), (0,0), rowspan = 4, colspan = 1)
ax2 = plt.subplot2g((10,1), (5,0), rowspan = 4, colspan = 1)

ax1.plot(ibm['close'], linewidth = 2.5)
ax1.set_title('IBM Close Price', fontsize = 20)

ax2.plot(ibm['rsi_14'], color = 'orange', linewidth = 2.5)
ax2.axline(30, linestyle='--', linewidth=1.5, color='grey')
ax2.axline(70, linestyle='--', linewidth=1.5, color='grey')
ax2.set_title('IBM RSI')

plt.show()

    
