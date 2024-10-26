# Import necessary libraries
import yfinance as yf  
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler 
from tensorflow.keras.models import load_model 

# Load the saved model
model = load_model('/Users/m3macair/Desktop/Academic/WHGS/whgs_repo/AAPL.keras')

# Download stock data for test set
tickerSymbol = 'AAPL'
data = yf.Ticker(tickerSymbol)
test_start = '2020-01-01'  
test_end = '2024-01-01'

# Getting actual prices for the test set
testdata = data.history(start=test_start, end=test_end, interval='1d').Close
actual_prices = testdata.values

# Prepare the total dataset for predictions
total_dataset = pd.concat((data.history(start='2015-01-01', end='2019-12-31', interval='1d').Close, testdata), axis=0)
model_inputs = total_dataset[len(total_dataset) - len(testdata) - 50:].values  # 50 is prediction_days
model_inputs = model_inputs.reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 1))
model_inputs = scaler.fit_transform(model_inputs)

# Prepare x_test for prediction
x_test = []
prediction_days = 50  # Ensure this matches with your training setup
for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x - prediction_days:x, 0])

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Make predictions
predicted_prices = model.predict(x_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

# Create DataFrame to store results
results_df = pd.DataFrame({
    'Date': testdata.index,
    'Actual Price': actual_prices,
    'Predicted Price': predicted_prices.flatten()  # Flatten to 1D for DataFrame
})

# Calculate whether the predicted price indicates a rise or fall
# Shift predicted prices to align with today's date
results_df['Price Direction'] = np.where(
    results_df['Predicted Price'].shift(-1) > results_df['Actual Price'], 1, -1
)

# Determine whether the price trends are correct
results_df['Actual Return'] = results_df['Actual Price'].pct_change()
results_df['Predicted Return'] = results_df['Predicted Price'].pct_change()

# Identify correctness of predictions based on direction
results_df['Correct/Wrong'] = np.where(
    np.sign(results_df['Actual Return']) == np.sign(results_df['Predicted Return']),
    'Correct', 'Wrong'
)

# Calculate the True Positives (TP) where both returns are positive
results_df['True Positive'] = np.where(
    (results_df['Actual Return'] > 0) & (results_df['Predicted Return'] > 0),
    1, 0
)

# Calculate True Positive Rate
true_positive_rate = results_df['True Positive'].mean() * 100  # Calculate percentage

# Calculate accuracy
accuracy = (results_df['Correct/Wrong'] == 'Correct').mean() * 100  # Calculate percentage

# Print results
print(results_df[['Date', 'Actual Price', 'Predicted Price', 'Price Direction', 'Correct/Wrong', 'True Positive']])
print(f"Accuracy of predictions: {accuracy:.2f}%")
print(f"True Positive Rate: {true_positive_rate:.2f}%")

# Visualization
plt.title(tickerSymbol, fontsize=22)
plt.plot(actual_prices, 'b.-', label='Actual Price')
plt.plot(predicted_prices, 'r.-', label='Predicted Price')
plt.xlabel('Time(days)', fontsize=16)
plt.ylabel('Stock Price', fontsize=16)
plt.legend()
plt.show()