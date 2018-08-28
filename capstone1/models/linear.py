import sys
import warnings
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


def main(args):

    LAG_SIZE = 52

    if len(args) != 1:
        print(f'Usage: linear 3-letter-day ie. linear mon')
        return
    else:
        day = args[0].lower()

    print(f'Lag size = {LAG_SIZE}')

    # Read historic sales for a given day
    df_all = pd.read_excel(f'../data/{day}-sales.xlsx', index_col='date', parse_dates=True)

    # Drop the day since they're all the same in this case
    df = df_all.drop('day', axis='columns')

    # Print numeric summary stats
    print(df.sales.describe())

    # Hold out 20% of the data as unseen to test the model
    train_idx = int(len(df) * .8)
    train_df = df[0:train_idx].copy()

    # Shift the sales data back in time by the lag window. This
    # turns time series prediction into a supervised learning problem
    train_df['label'] = train_df['sales'].shift(-LAG_SIZE)
    train_df.dropna(inplace=True)

    # Create training and target data
    X = train_df.drop('label', axis='columns')
    X_scaled = scale(X)
    X_recent = df[train_idx:]
    X_recent_scaled = scale(X_recent)
    y = train_df['label']

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, random_state=0)

    # Create and train the model
    reg = LinearRegression()
    reg.fit(X_train, y_train)

    # Run on the test data and print error stats
    y_pred = reg.predict(X_test)

    print(f'R^2: {reg.score(X_test, y_test)}')
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f'Root Mean Squared Error: {rmse}')

    # Run on the unseen data and plot
    y_pred = reg.predict(X_recent_scaled)

    # Copy the predicted values back into a date-indexed dataframe
    forecast = X_recent.drop('month', axis='columns')
    forecast['fcst'] = y_pred

    # Add a forecast column to the dataframe with all sales data
    # for the given day. This way, we get to see just the prediction
    # overlayed on top of all the data
    df = df.drop(['week', 'month'], axis='columns')
    df['forecast'] = forecast['fcst']

    df.plot(figsize=(12, 6), marker='o')
    plt.title(f'{day.title()} Sales')
    plt.show()


if __name__ == '__main__':
    warnings.filterwarnings(action='ignore', module='sklearn', message='^internal gelsd')
    main(sys.argv[1:])
