import yfinance as yf
import matplotlib.pyplot as plt 

df  = yf.download('XOM', start='2020-08-01', end='2025-08-01', interval='1d')

fig, ax = plt.subplots()
ax.plot(df['Close'], color='black')
plt.xlabel('Date')
plt.ylabel('Exxon Mobil Price (USD)')
plt.xticks(rotation=45)
plt.show()

