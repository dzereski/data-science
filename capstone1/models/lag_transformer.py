"""
lag_transformer
~~~~~~~~~~~~~~~~
Custom scikit-learn transformer to create lags of time series data
"""

import sys

import pandas as pd

from sklearn.base import TransformerMixin


_DAYS_IN_WEEK = 7
_MIN_TRAIN_SIZE = _DAYS_IN_WEEK * 16
_NA_VAL = 0.0


def make_lags(df_in, x_cols, y_col, lag_size=1, num_lags=1):
    """generate lagged versions of a time series.

    Parameters
    ----------
    df_in: Pandas dataframe containing the source time series. It's
        assumed that the index of df_in is a parseable date string
        or datetime index.
    x_cols: List of dataframe colums to create lags
    y_col: The target value to be predicted
    lag_size: Either an integer or list to specify how much to
        how much to lag the x_cols by.  (ie 7 or [1, 7, 28])
    num_lags: Only used if lag_size is an int.  In this case,
        it's the number of lags to generate.

    Returns
    -------
    A Pandas dataframe containing lagged versions of the spcified
    columns along with the target renamed as ('y').
    """

    df_out = pd.DataFrame()

    if isinstance(lag_size, int):
        lags = [n * lag_size for n in range(1, num_lags + 1)]
    elif isinstance(lag_size, list):
        lags = lag_size
        num_lags = len(lags)

    x_col_list = []

    if isinstance(x_cols, str):
        x_col_list.append(x_cols)
    elif isinstance(x_cols, list):
        x_col_list = x_cols

    for n in reversed(lags):
        for col in x_col_list:
            col_name = '{}_t-{}'.format(col, n)
            df_out[col_name] = df_in[col].shift(n)

    df_out['y'] = df_in[y_col]
    df_out['date'] = pd.to_datetime(df_in.index)
    df_out = df_out.set_index(df_out.date)
    df_out = df_out.drop('date', axis='columns')

    return df_out.dropna()


class LagTransformer(TransformerMixin):
    """scikit-learn custom transformer to create lagged time series

    Parameters
    ----------
    x_cols: List of dataframe colums to create lags
    y_col: The target value to be predicted
    lags: List to specify how much to how much to lag
    the x_cols by.  (ie [1, 7, 28])

    Returns
    -------
    A Pandas dataframe containing lagged versions of the spcified
    columns along with the target renamed as ('y').
    """

    def __init__(self, x_cols=None, y_col=None, lags=1):
        self.x_cols = x_cols
        self.y_col = y_col
        self.lags = lags

    def fit(self, *args, **kwargs):
        pass

    def transform(self, X, **transform_params):
        df_lag = make_lags(X, self.x_cols, self.y_col, self.lags)
        return df_lag

    def fit_transform(self, X, **transform_params):
        return self.transform(X, **transform_params)


def main(args):

    if len(args) != 1:
        print('Usage: lag_transformer source_file')
        return
    else:
        source = args[0]

    df_in = pd.read_excel(source, index_col='date', parse_dates=True)

    trans = LagTransformer(x_cols=['sales'], y_col='sales', lags=[1, 7])
    df_lags = trans.transform(df_in)

    print(df_lags.tail(30))
    print(df_lags.info())


if __name__ == '__main__':
    main(sys.argv[1:])
