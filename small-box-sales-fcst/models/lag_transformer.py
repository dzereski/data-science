"""
lag_transformer
~~~~~~~~~~~~~~~~
Custom scikit-learn transformer to create lags of time series data
"""

import sys

import pandas as pd

from getlags import get_lags
from sklearn.base import TransformerMixin


_DAYS_IN_WEEK = 7
_MIN_TRAIN_SIZE = _DAYS_IN_WEEK * 16
_NA_VAL = 0.0


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
        df_lag = get_lags(X, self.x_cols, self.y_col, self.lags)
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
