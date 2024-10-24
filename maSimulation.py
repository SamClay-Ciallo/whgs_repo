import numpy as np 
import yfinance as yf
import matplotlib.pyplot as plt 
import pandas as pd 

# Initialize portfolio values
cash = 100000
share = 0
minMperiod = 5
maxMAperiod = 20  # Changed to 10 to match the MA calculation below
Total_value = []

# Function to collect stock prices
def stock_price_collecting(code, datestart, dateend, period):
    data = yf.Ticker(code)
    prices = data.history(start=datestart, end=dateend, interval=period).Close
    return prices

# Collect historical price data
historical_price_data = stock_price_collecting("AAPL", "2023-01-01", "2024-01-01", "1d") 
historical_price_data = pd.DataFrame(historical_price_data)

# Calculate moving averages
historical_price_data['MA5'] = historical_price_data['Close'].rolling(window=minMperiod).mean()
historical_price_data['MA10'] = historical_price_data['Close'].rolling(window=maxMAperiod).mean()

# Calculate Bollinger Bands
historical_price_data['20d_ma'] = historical_price_data['Close'].rolling(window=20).mean()
historical_price_data['20d_std'] = historical_price_data['Close'].rolling(window=20).std()
historical_price_data['upper_band'] = historical_price_data['20d_ma'] + (historical_price_data['20d_std'] * 2)
historical_price_data['lower_band'] = historical_price_data['20d_ma'] - (historical_price_data['20d_std'] * 2)

# Simulation of buying and selling
for i in range(len(historical_price_data)):
    current_price = historical_price_data["Close"].iloc[i]
    T_value = cash + (share * current_price)
    
    if i > 0:  # We can check yesterday's values only if i > 0
        MA5 = historical_price_data["MA5"].iloc[i]
        MA10 = historical_price_data["MA10"].iloc[i]
        MA5_yesterday = historical_price_data["MA5"].iloc[i-1]
        MA10_yesterday = historical_price_data["MA10"].iloc[i-1]

        # Detecting whether to buy
        if i >= maxMAperiod:  # Ensure we have enough data for MA10
            if MA5 > MA10 and MA5_yesterday < MA10_yesterday:
                print("B-sig" + " " + str(historical_price_data.index[i]))
                if cash >= current_price:
                    print("ACTION TRUE")
                    share = cash // current_price
                    cash -= (share * current_price)
                    print("Number of shares " + str(share))
                    print("Amount of cash " + str(cash))
                else:
                    print("ACTION FALSE")

            # Detecting whether to sell
            elif MA5 < MA10 and MA5_yesterday > MA10_yesterday:
                print("S-sig" + " " + str(historical_price_data.index[i]))
                if share > 0:
                    print("ACTION TRUE")
                    cash += (share * current_price)
                    share = 0
                    print("Number of shares " + str(share))
                    print("Amount of cash " + str(cash))
                else:
                    print("ACTION FALSE")

    # Always append the total value at the end of each day
    Total_value.append(T_value)

# Plotting portfolio value over time
plt.figure(figsize=(14, 7))
plt.plot(historical_price_data.index, Total_value, label="Portfolio Value")  # Exclude the last entry if needed for formatting
plt.title("Portfolio Value Over Time")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (in $)")
plt.legend()
plt.grid()
plt.show()