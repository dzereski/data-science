"""
getlags
~~~~~~~~~~~~~~~~
generate lagged columns for time series
"""

import sys

import pandas as pd


_DAYS_IN_WEEK = 7
_MIN_TRAIN_SIZE = _DAYS_IN_WEEK * 16
_NA_VAL = 0.0


def get_lags(df_in, x_cols, y_col, lags):
    """generate lagged versions of a time series.

    Parameters
    ----------
    df_in: Pandas dataframe containing the source time series. It's
        assumed that the index of df_in is a parseable date string
        or datetime index.
    x_cols: A single string or a list of dataframe colums to be lagged
    y_col: The target value to be predicted
    lags: list to specify the x_col lags ([1, 7, 28])

    Returns
    -------
    A Pandas dataframe containing lagged versions of the spcified
    columns along with the target renamed as ('y').
    """

    x_col_list = []

    if isinstance(x_cols, str):
        x_col_list.append(x_cols)
    elif isinstance(x_cols, list):
        x_col_list = x_cols

    if len(x_col_list) == 0:
        raise ValueError('No X columns.  Must specify at least one X column to lag')

    if y_col is None:
        raise ValueError('No Y column.  Must specify the target, Y column')

    if y_col not in df_in.columns:
        raise ValueError('Y column {} is not in df_in'.format(y_col))

    df_out = pd.DataFrame()

    if isinstance(lags, list):
        for n in reversed(lags):
            for col in x_col_list:
                col_name = '{}_t-{}'.format(col, n)
                df_out[col_name] = df_in[col].shift(n)
    elif isinstance(lags, dict):
        for x_col in lags:
            n = lags[x_col]
            col_name = '{}_t-{}'.format(col, n)

    df_out['y'] = df_in[y_col]
    df_out['date'] = pd.to_datetime(df_in.index)
    df_out = df_out.set_index(df_out.date)
    df_out = df_out.drop('date', axis='columns')

    return df_out.dropna()
