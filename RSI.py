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

# Impliment Strategy

def rsi_strategy(prices, rsi):
    buy_price = []
    sell_price = []
    rsi_signal = []
    signal = 0

    for i in range(len(rsi)):
        if rsi[i-1] > 30 and rsi[i] < 30:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                rsi_signal.append(0)
        elif rsi[i-1] < 70 and rsi[i] > 70:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                signal = -1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append( np.nan)
                rsi_signal.append(0)            
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            rsi_signal.append(0)
    return buy_price, sell_price, rsi_signal

buy_price, sell_price, rsi_signal = rsi_strategy(ibm['close'], ibm['rsi_14'])

# Plotting Signals (Do Later)

# Position Sizing 

position = []
for i in range(len(rsi_signal)):
    if rsi_signal[i] > 1:
        position.append(0)
    else:
        position.append(0)

for i in range(len(ibm['close'])):
    if rsi_signal[i] == 1:
        position[i] = 1
    elif rsi_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]

rsi  = ibm['rsi_14']
close_price = ibm['close']    

rsi_signal = pd.DataFrame(rsi_signal).reanme(columns = {0:'rsi_signal'}).set_index(ibm.index)
position = pd.DataFrame(position).rename(columns = {0:'rsi_position'}).set_index(ibm.index)

frames = [close_price, rsi, rsi_signal, position]
strategy = pd.concat(frames, join='inner', axis=1)

strategy 

# BackTesting

ibm_ret = pd.DataFrame(np.diff(ibm['close'])).rename(columns = {0 : 'returns'})
rsi_strategy_ret = []

for i in range(len(ibm_ret)):
    returns = ibm_ret['returns'][i] * strategy['rsi_position'][i]
    rsi_strategy_ret.append(returns)

rsi_strategy_ret_df = pd.DataFrame(rsi_strategy_ret).rename(columns = {0 : 'rsi_strategy_returns'})
investment_value = 100000
rsi_investment_ret = []

for i in range(len(rsi_strategy_ret_df['rsi_returns'])):
    number_of_stocks = floor(investment_value / ibm['close'][i])
    returns = number_of_stocks * rsi_strategy_ret_df['rsi_strategy_returns'][i]
    rsi_investment_ret.append(returns)

rsi_investment_ret_df = pd.DataFrame(rsi_investment_ret).rename(columns = {0 : 'rsi_investment_returns'})
total_investment_ret = round(sum(rsi_investment_ret_df['rsi_investment_returns']), 2) 
profit_percentage = floor((total_investment_ret / investment_value) * 100)

print(cl('Profit gained from the RSI strategy by investing $100k in IBM : {}'.format(total_investment_ret), attrs = ['bold']))
print(cl('Profit percentage of the RSI strategy : {}%'.format(profit_percentage), attrs = ['bold']))