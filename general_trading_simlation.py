# Import necessary packages
import yfinance as yf 
import pandas as pd 
import pandas_ta as ta
import matplotlib.pyplot as plt 

# Initialize the portfolio for a single stock
cash = 100000  # Initial cash
shareNUm = 0   # Set the number of shares to zero
stock_code = "GOOG" 
data_collecting_begaining_date = "2020-01-01"
data_collecting_ending_date = "2024-01-01"
period_of_collecting = "1d" 

# Function to collect stock price data
def stock_price_collecting(code, datestart, dateend, period):
    data = yf.Ticker(code)
    prices = data.history(start=datestart, end=dateend, interval=period)
    return prices

# Collect historical price data
historical_price_data = stock_price_collecting(stock_code, data_collecting_begaining_date, data_collecting_ending_date, period_of_collecting)
historical_price_data = pd.DataFrame(historical_price_data)

# Initialize day counter
dayCounter = 0

#Initialize the return change
Portfolio_value = []

# Basic price initializations
current_price = historical_price_data["Close"].iloc[dayCounter]
T_value = cash + (shareNUm * current_price)


# Define basic functions
def buy(amount):
    global cash, shareNUm
    if amount == "max" and cash >= ((cash // current_price) * current_price):  # Buy all shares you can afford
        print("")
        print("Buy Action(ALL) - " + str(historical_price_data.index[dayCounter]) + " at price " + str(current_price)) 
        trading_number_of_share = (cash // current_price)
        shareNUm += (cash // current_price)
        cash -= (trading_number_of_share * current_price)
        print("Trading Summary------Trading Summary------ " ) # Print trading summary
        print("Share Num : " + str(shareNUm))
        print("Cash Num " + str(cash))
        print("Portfolio Value : "+ str(T_value))
        print("---------------------------------------------") 
    elif isinstance(amount, (int, float)) and cash >= (amount * current_price):  # Buy specified amount
        print("")
        print("Buy Action(CUS) - " + str(historical_price_data.index[dayCounter]) + " at price " + str(current_price)) 
        shareNUm += amount 
        cash -= (amount * current_price)
        print("Trading Summary------Trading Summary------ " )
        print("Share Num : " + str(shareNUm))
        print("Cash Num " + str(cash))
        print("Portfolio Value : "+ str(T_value))
        print("---------------------------------------------")
    #else:
        #print("Buy Action FAILED")

def sell(amount):
    global cash, shareNUm
    if amount == "max" and shareNUm > 0:
        print("")
        print("Sell Action(ALL) - " + str(historical_price_data.index[dayCounter]) + " at price " + str(current_price)) 
        cash += (shareNUm * current_price)
        shareNUm = 0
        print("Trading Summary------Trading Summary------ " )
        print("Share Num : " + str(shareNUm))
        print("Cash Num " + str(cash))
        print("Portfolio Value : "+ str(T_value))
        print("---------------------------------------------") 
    elif isinstance(amount, (int, float)) and shareNUm >= amount:
        
        print("Sell Action(CUS) - " + str(historical_price_data.index[dayCounter]) + " at price " + str(current_price)) 
        cash += (amount * current_price)
        shareNUm -= amount
        print("Trading Summary------Trading Summary------ " )
        print("Share Num : " + str(shareNUm))
        print("Cash Num " + str(cash))
        print("Portfolio Value : "+ str(T_value))
        print("---------------------------------------------") 
    #else:
        #print("Sell Action FAILED")

def crossover_threshold(target, crosstarget):
    if target.iloc[dayCounter] > crosstarget and target.iloc[dayCounter - 1] <= crosstarget:
        return True
    return False

def crossover_double(target, target_variable):
    if dayCounter >= 1:
        if target.iloc[dayCounter] > target_variable[dayCounter] and target.iloc[dayCounter - 1] <= target_variable[dayCounter - 1]:
            return True
    return False

def crossdown_threshold(target, crosstarget):
    if target.iloc[dayCounter] < crosstarget and target.iloc[dayCounter - 1] >= crosstarget:
        return True
    return False

def crossdown_double(target, target_variable):
    if dayCounter >= 1:
        if target.iloc[dayCounter] < target_variable[dayCounter] and target.iloc[dayCounter - 1] >= target_variable[dayCounter - 1]:
            return True
    return False



#Strategy area----------------------------------------------------------------------------------------------------
# RSI strategy
RSI_upper = 70
RSI_lower = 30

def MaStrategy():
    global current_price, T_value  # Add the necessary variables to global
    RSI14 = ta.rsi(historical_price_data["Close"], length=14)
    if dayCounter >= 14:  # Ensure enough data for RSI calculation
        if crossover_threshold(RSI14, RSI_upper):
            sell("max")
        elif crossdown_threshold(RSI14, RSI_lower):
            buy("max")

# MovingAveragePro
windowp = 30
def BolliangerChannel():
    std = historical_price_data.Close.rolling(window=windowp).std()
    ma = historical_price_data.Close.rolling(window=windowp).mean()
    
    BoHigh = ma + (2*std)
    BoLow = ma - (2*std) 
    Bomean = ma
    return(BoHigh,BoLow,Bomean)

High,Low,Mean = BolliangerChannel()

def SimpleBolStra():
    if dayCounter >= 30:
        if crossover_double(historical_price_data.Close,Mean):
            sell("max")
        if crossover_double(historical_price_data.Close,Low):
            buy("max")

#Strategy area----------------------------------------------------------------------------------------------------


# Run the simulation
while dayCounter < len(historical_price_data):  # Proper condition to prevent out-of-bounds access
    current_price = historical_price_data["Close"].iloc[dayCounter]
    T_value = cash + (shareNUm * current_price)  # Update portfolio value

    #MaStrategy()  # Execute strategy for the current day
    SimpleBolStra()
    
    Portfolio_value.append(T_value)
    dayCounter += 1  # Move to the next day

#Calculate buy and hold strategy return.
BHreturn = (historical_price_data["Close"].iloc[len(historical_price_data)-1]-historical_price_data["Close"].iloc[0])/historical_price_data["Close"].iloc[0]
print("")
print("B&H return : " + f"{BHreturn:.3f}") 
#Calculate the strategy return:
StraReturn = ((Portfolio_value[len(Portfolio_value) - 1]) - Portfolio_value[0])/Portfolio_value[0]
print("Strategy return : " + f"{StraReturn:.3f}") 

#Visualization
plt.figure(figsize=(14, 7))
plt.plot(historical_price_data.index, Portfolio_value, label="Portfolio Value")  # Exclude the last entry if needed for formatting
plt.title("Portfolio Value Over Time")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (in $)")
plt.legend()
plt.grid()
plt.show()

