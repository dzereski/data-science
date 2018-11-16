import pandas as pd

from getlags import get_lags

dates = ['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05', '2018-01-06',
         '2018-01-07', '2018-01-08', '2018-01-09', '2018-01-10', '2018-01-11', '2018-01-12',
         '2018-01-13', '2018-01-14', '2018-01-15', '2018-01-16', '2018-01-17', '2018-01-18',
         '2018-01-19', '2018-01-20', '2018-01-21', '2018-01-22', '2018-01-23', '2018-01-24',
         '2018-01-25', '2018-01-26', '2018-01-27', '2018-01-28', '2018-01-29', '2018-01-30',
         '2018-01-31']

temps = [9.65, 14.54, 25.96, 24.53, 16.29, 8.04, 11.51, 31.54, 38.85, 34.94, 48.18,
         57.57, 58.59, 19.98, 15.76, 30.29, 32.43, 27.14, 31.55, 43.94, 46.36, 34.61,
         33.76, 35.92, 26.35, 29.77, 49.04, 47.52, 35.81, 29.26, 27.69]

df = pd.DataFrame({'date': dates, 'temp': temps})
df = df.set_index(pd.to_datetime(df.date))
df.drop('date', axis='columns', inplace=True)

print(df.head())

df_lag = get_lags(df, 'temp', 'temp', [1, 7])

print(df_lag.head())
