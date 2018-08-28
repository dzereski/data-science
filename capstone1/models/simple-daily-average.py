import sys
import warnings
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


def init_average(history_df):
    """Closure to compute the average of past single days during the
    given week.  ie - average for thu in prior years week 32.  Closure
    is a clean way to give the average function access to the DF with
    historic data"""
    def daily_average(row):
        history = history_df[history_df.week == row.week]
        return history.sales.mean()
    return daily_average


class SimpleWeeklyAverage:
    def __init__(self, train_df):
        self.df = train_df

    def predict(self, pred_df):
        pred_df['fcst'] = np.NaN
        week_avg = init_average(self.df)
        pred_df['fcst'] = pred_df.apply(week_avg, axis=1)

        return pred_df


def main(args):

    LAG_SIZE = 52

    if len(args) != 1:
        print(f'Usage: simple-daily-average 3-letter-day ie. simple-daily-average mon')
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
    test_df = df[train_idx:].copy()

    # Create a simple daily average instance
    avg = SimpleWeeklyAverage(train_df)

    # Run on the test data and print error stats
    y_pred = avg.predict(test_df)
    y_pred['daily avg'] = train_df.sales.mean()
    y_pred.dropna(inplace=True)

    rmse = np.sqrt(mean_squared_error(y_pred['sales'], y_pred['fcst']))
    print(f'Weekly Average Root Mean Squared Error: {rmse}')
    rmse = np.sqrt(mean_squared_error(y_pred['sales'], y_pred['daily avg']))
    print(f'Daily Average Root Mean Squared Error: {rmse}')

    df = df.drop(['month', 'week'], axis='columns')
    df['weekly avg'] = y_pred['fcst']
    df['daily avg'] = y_pred['daily avg']
    df.plot(figsize=(12, 6), marker='o')
    plt.title(f'{day.title()} Sales')
    plt.show()


if __name__ == '__main__':
    warnings.filterwarnings(action='ignore', module='sklearn', message='^internal gelsd')
    main(sys.argv[1:])
