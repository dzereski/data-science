import sys
import pandas as pd
import numpy as np
from statsmodels.tsa.api import Holt, ExponentialSmoothing
from pandas.tools.plotting import autocorrelation_plot
from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt


def naive(df, train, test):
    dd = np.asarray(df.sales)
    y_hat = test.copy()
    y_hat['naive'] = dd[len(dd) - 1]

    plt.figure(figsize=(12, 8))
    plt.plot(train.index, train['sales'], marker='o', label='Train')
    plt.plot(test.index, test['sales'], marker='o', label='Test')
    plt.plot(y_hat.index, y_hat['naive'], marker='o', label='Naive Forecast')
    plt.legend(loc='best')
    plt.title('Naive Forecast')
    plt.xticks(rotation=45)

    rms = sqrt(mean_squared_error(test.sales, y_hat.naive))
    print(f'Root Mean Squared Error: {rms}')

    plt.show()


def average(df, train, test):
    y_hat_avg = test.copy()
    y_hat_avg['avg_forecast'] = train['sales'].mean()
    plt.figure(figsize=(12, 8))
    plt.plot(train['sales'], marker='o', label='Train')
    plt.plot(test['sales'], marker='o', label='Test')
    plt.plot(y_hat_avg['avg_forecast'], marker='o', label='Average Forecast')
    plt.legend(loc='best')
    plt.xticks(rotation=45)

    rms = sqrt(mean_squared_error(test.sales, y_hat_avg.avg_forecast))
    print(f'Root Mean Squared Error: {rms}')

    plt.show()


def moving_average(df, train, test):
    y_hat_avg = test.copy()
    y_hat_avg['moving_avg_forecast'] = train['sales'].rolling(6).mean().iloc[-1]
    plt.figure(figsize=(12, 8))
    plt.plot(train['sales'], marker='o', label='Train')
    plt.plot(test['sales'], marker='o', label='Test')
    plt.plot(y_hat_avg['moving_avg_forecast'], marker='o', label='Moving Average Forecast')
    plt.legend(loc='best')
    plt.xticks(rotation=45)

    rms = sqrt(mean_squared_error(test.sales, y_hat_avg.moving_avg_forecast))
    print(f'Root Mean Squared Error: {rms}')

    plt.show()


def holt_linear(df, train, test):
    y_hat_avg = test.copy()

    fit1 = Holt(np.asarray(train['sales'])).fit(smoothing_level=0.3, smoothing_slope=0.1)
    y_hat_avg['Holt_linear'] = fit1.forecast(len(test))

    plt.figure(figsize=(12, 6))
    plt.plot(train['sales'], marker='o', label='Train')
    plt.plot(test['sales'], marker='o', label='Test')
    plt.plot(y_hat_avg['Holt_linear'], marker='o', label='Holt_linear')
    plt.legend(loc='best')
    plt.xticks(rotation=45)

    rms = sqrt(mean_squared_error(test.sales, y_hat_avg.Holt_linear))
    print(f'Root Mean Squared Error: {rms}')

    plt.show()


def holt_winter(df, train, test):
    y_hat_avg = test.copy()
    fit1 = ExponentialSmoothing(np.asarray(train['sales']), seasonal_periods=3, trend='add', seasonal='add',).fit()
    y_hat_avg['Holt_Winter'] = fit1.forecast(len(test))
    plt.figure(figsize=(12, 6))
    plt.plot(train['sales'], marker='o', label='Train')
    plt.plot(test['sales'], marker='o', label='Test')
    plt.plot(y_hat_avg['Holt_Winter'], marker='o', label='Holt_Winter')
    plt.legend(loc='best')
    plt.xticks(rotation=45)

    rms = sqrt(mean_squared_error(test.sales, y_hat_avg.Holt_Winter))
    print(f'Root Mean Squared Error: {rms}')

    plt.show()


def arima_test(df, train, test):
    y_hat_avg = test.copy()
    model = ARIMA(train.sales, order=(51, 1, 0))
    fit1 = model.fit(disp=0)
    print(model.fit.summary())
    y_hat_avg['SARIMA'] = fit1.predict(start='2016-06-2', end='2018-03-15', dynamic=True)
    plt.figure(figsize=(12, 6))
    plt.plot(train['sales'], label='Train')
    plt.plot(test['sales'], label='Test')
    plt.plot(y_hat_avg['SARIMA'], label='SARIMA')
    plt.legend(loc='best')
    plt.show()


def main(args):
    if len(args) != 1:
        print(f'Usage: time-series1 3-letter-day ie. time-series1 mon')
        return
    else:
        day = args[0].lower()

    df = pd.read_excel(f'../data/{day}-sales.xlsx')
    # autocorrelation_plot(df['sales'])
    # plt.show()

    train_idx = int(len(df) * .8)

    train = df[0:train_idx]
    # print(train)
    # print('-' * 20)
    test = df[train_idx:]
    # print(test)

    # naive(df, train, test)
    # average(df, train, test)
    moving_average(df, train, test)
    # holt_linear(df, train, test)
    # holt_winter(df, train, test)
    # arima_test(df, train, test)


if __name__ == '__main__':
    main(sys.argv[1:])
