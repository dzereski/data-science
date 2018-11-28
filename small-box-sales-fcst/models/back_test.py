"""
back_test
~~~~~~~~~~~~~~~~
A collection of classes and functions to perform back testing of time series
"""

import sys
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from walksplit import TimeSeriesWalkSplit
from lag_transformer import LagTransformer

_DAYS_IN_WEEK = 7
_MIN_TRAIN_SIZE = _DAYS_IN_WEEK * 16
_NA_VAL = 0.0


def get_first_sunday(df, test_size=_DAYS_IN_WEEK):
    """Find the index of the first Sunday in a DateTime indexed dataframe.
    """
    start_idx = None

    if test_size == _DAYS_IN_WEEK:
        for idx in range(_DAYS_IN_WEEK):
            day = df.index[idx].dayofweek
            if day == 6:
                start_idx = idx
                break
    else:
        start_idx = 0

    return start_idx


def get_default_train_test_size():
    return _MIN_TRAIN_SIZE, _DAYS_IN_WEEK


def root_mean_squared_error(y_true, y_pred):
    """Calculate root mean squared error, workes with scikit-learn's make_scorer
    """
    return(np.sqrt(mean_squared_error(y_true, y_pred)))


def mean_absolute_percentage_error(y_true, y_pred):
    """Calculate root mean absolute percentage error, workes with scikit-learn's make_scorer

    Diminishes division by zero issues by summing values for y_true and y_pred.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    diff = np.absolute(np.sum(y_true) - np.sum(y_pred))
    return diff / np.sum(y_true) * 100.0


def walk_forward_validate(model, df_in, test_size=_DAYS_IN_WEEK):
    """Perform back testing of a time series through walk forward validation.

    Returns
    -------
    Pandas dataframe with y values, yhat and errors with a DateTime index
    corresponding to the input, df_in
    """

    tscv = TimeSeriesWalkSplit(_DAYS_IN_WEEK, train_size=_MIN_TRAIN_SIZE)
    X = df_in.drop('y', axis='columns')
    y = df_in[['y']].values.ravel()

    df_pred = df_in[['y']][_MIN_TRAIN_SIZE:]
    df_pred['yhat'] = np.NaN
    df_pred['error'] = np.NaN
    y_idx = 0

    for (train_index, test_index) in tscv.split(X):
        test_start_idx = len(train_index)
        test_end_idx = len(train_index) + len(test_index)

        X_train = X[:test_start_idx]
        y_train = y[:test_start_idx]
        X_test = X[test_start_idx:test_end_idx]

        model.fit(X_train, y_train)
        yhat = model.predict(X_test)

        df_pred['yhat'][y_idx:y_idx + len(yhat)] = yhat.reshape(test_size,)
        y_idx += len(yhat)

    df_pred['error'] = df_pred['y'] - df_pred['yhat']
    df_pred.dropna(inplace=True)

    return df_pred


def calc_metrics(df_in, start=0, period=_DAYS_IN_WEEK):
    """Calculate MAPE and RMSE metrics from a dataframe returned by walk_forward_predict.
    Also works with Facebook Prophet dataframes.

    Returns
    -------
    Pandas dataframe with RMSE and MAPE columns with a DateTime index
    corresponding to the input, df_in

    Notes
    -----
    Calculates MAPE and RMSE for the specified period (ie one week of data)
    by iterating through df_in
    """

    end = len(df_in.index)

    if 'ds' in df_in.columns:
        is_prophet_df = True
    else:
        is_prophet_df = False

    metrics = []

    for week_start in range(start, end, period):
        week_end = week_start + period
        y_true = df_in.y.iloc[week_start:week_end]
        y_pred = df_in.yhat.iloc[week_start:week_end]

        m = {}
        if is_prophet_df is True:
            m['date'] = df_in.ds[week_start]
        else:
            m['date'] = df_in.index[week_start]

        m['RMSE'] = root_mean_squared_error(y_true, y_pred)
        m['MAPE'] = mean_absolute_percentage_error(y_true, y_pred)
        metrics.append(m)

    df_m = pd.DataFrame(metrics)
    df_m = df_m.set_index(pd.to_datetime(df_m.date))
    df_m.drop('date', axis='columns', inplace=True)
    df_m.sort_index(inplace=True)

    return df_m


def main(args):

    if len(args) != 1:
        print('Usage: tsutils source_file')
        return
    else:
        source = args[0]

    df_in = pd.read_excel(source, index_col='date', parse_dates=True)
    start_idx = get_first_sunday(df_in)
    df_in.drop(df_in.index[:start_idx], inplace=True)

    df_sales = pd.get_dummies(df_in[['sales', 'is_open', 'day']])
    df_sales.drop(['sales'], axis='columns', inplace=True)

    trans = LagTransformer(x_cols=['sales'], y_col='sales', lags=[1, 7, 14, 21, 28])
    df_lag = trans.transform(df_in)

    df_lag.to_csv('lag_test.csv')

    df_wx = pd.read_excel('../data/daily-weather.xlsx')
    df_wx.index = pd.to_datetime(df_wx.date)
    df_wx.drop('date', axis='columns', inplace=True)
    df_wx.info()

    df = pd.concat([df_lag, df_sales], axis='columns').dropna()
    start_idx = get_first_sunday(df)
    if start_idx > 0:
        df.drop(df.index[:start_idx], inplace=True)

    print(df.info(), '\n')
    print(df.head(30))

    model = LinearRegression(normalize=True)

    df_pred = walk_forward_validate(model, df)

    print(df_pred.head(30))

    df_metrics = calc_metrics(df_pred)

    print(df_metrics.tail(12))


if __name__ == '__main__':
    main(sys.argv[1:])
