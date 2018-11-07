"""
lag_cleaner
~~~~~~~~~~~~~~~~
Custom scikit-learn transformer to clean lagged data.
"""

import sys

import numpy as np
import pandas as pd

from sklearn.base import TransformerMixin

from lag_transformer import LagTransformer


_DAYS_IN_WEEK = 7
_NA_VAL = 0.0


def _find_lag_cols(df_in):
    lag_cols = []
    for col in df_in.columns:
        if col.find('_t-') > 0 and df_in[col].dtype == np.float64:
            lag_cols.append(col)

    return lag_cols


def get_daily_averages(df_in):
    lag_cols = _find_lag_cols(df_in)

    daily_avg = pd.DataFrame(columns=['month', 'day'] + lag_cols)

    df_avg = df_in[lag_cols].replace(_NA_VAL, np.NaN).dropna()

    for mon in range(1, 13):
        mon_df = df_avg[df_avg.index.month == mon]
        for day in range(0, _DAYS_IN_WEEK):
            day_df = mon_df[mon_df.index.dayofweek == day]

            avgs = {}
            avgs['month'] = mon
            avgs['day'] = day
            for col in lag_cols:
                avgs[col] = day_df[col].mean()

            daily_avg = daily_avg.append(avgs, ignore_index=True)

    daily_avg = daily_avg.replace(np.NaN, _NA_VAL)
    daily_avg = daily_avg.set_index(['month', 'day'])

    return daily_avg


def clean_lags(df_in):
    lag_cols = _find_lag_cols(df_in)

    day_avg = get_daily_averages(df_in)

    for idx, row in df_in.iterrows():
        month_day = (idx.month, idx.dayofweek)

        if row.y == _NA_VAL:
            for col in lag_cols:
                df_in.loc[idx, col] = _NA_VAL
        else:
            non_na_vals = 0
            na_vals = 0
            for col in lag_cols:
                if row[col] == _NA_VAL:
                    na_vals += 1
                else:
                    non_na_vals += 1

            if na_vals > 0 and non_na_vals > 0:
                for col in lag_cols:
                    if df_in.loc[idx, col] == _NA_VAL:
                        df_in.loc[idx, col] = day_avg.loc[month_day, col]

                        if col == 'sales_t-1':
                            print(idx, month_day)

    return df_in


class LagCleaner(TransformerMixin):
    """scikit-learn custom transformer to clean lagged time
    series data.

    Notes
    -----
    It doesn't make any sense to use days when the business is
    closed and generated zero sales to forecast days when the
    business is open. The can happen when creating lagged values
    and shifting a holiday from a Thursday, for instance.

    The LagCleaner finds these values and replaces them with a
    4-week moving average of that day in the lagged column.
    """

    def __init__(self):
        pass

    def fit(self, X, **kwargs):
        self.avgs = get_daily_averages(X)

    def transform(self, X, **transform_params):
        df = clean_lags(X)
        return df

    def fit_transform(self, X, **transform_params):
        self.fit(X)
        return self.transform(X, **transform_params)


def main(args):

    if len(args) != 1:
        print('Usage: lag_cleaner source_file')
        return
    else:
        source = args[0]

    df_in = pd.read_excel(source, index_col='date', parse_dates=True)

    trans = LagTransformer(x_cols=['sales'], y_col='sales', lags=[7, 14])
    df_lags = trans.transform(df_in)

    print(df_lags.tail(60))

    cleaner = LagCleaner()
    df = cleaner.fit_transform(df_lags)

    print(df.tail(60))


if __name__ == '__main__':
    main(sys.argv[1:])
