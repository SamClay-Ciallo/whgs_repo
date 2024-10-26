# Import necessary libraries
import yfinance as yf  
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler 
from tensorflow.keras.models import Sequential, load_model 
from tensorflow.keras.layers import Dense, Dropout, LSTM 

# Download stock data
tickerSymbol = 'AAPL'
data = yf.Ticker(tickerSymbol)
starttime = '2015-01-01'
endtime = '2019-12-31'
period = '1d'
prices = data.history(start=starttime, end=endtime, interval=period).Close
returns = prices.pct_change().dropna()

# Scale data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(prices.values.reshape(-1, 1))

prediction_days = 50

# Prepare training data
x_train = []
y_train = []

for x in range(prediction_days, len(scaled_data)):
    x_train.append(scaled_data[x-prediction_days:x, 0])
    y_train.append(scaled_data[x, 0])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# Build the model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1)) # Prediction

# Train the model
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=70, batch_size=32)

# Save the model
model.save(tickerSymbol+".keras")