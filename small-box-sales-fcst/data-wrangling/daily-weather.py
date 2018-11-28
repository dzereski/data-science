import sys

import pandas as pd
import pendulum

BIZ_HOURS = 10


def is_precip_day(hourly_obs):
    result = False

    counts = hourly_obs.value_counts()
    if len(counts) > 0 and counts[0] > BIZ_HOURS / 2:
        result = True

    return int(result)


def main(args):
    if len(args) != 2:
        print('usage: daily-weather src dst')
        sys.exit(-2)

    src = args[0]
    dst = args[1]

    df = pd.read_excel(src)
    df.set_index(pd.to_datetime(df.date_time), inplace=True)
    df.drop('date_time', axis='columns', inplace=True)

    df_out = pd.DataFrame()

    start = pendulum.parse('2017-11-17')
    end = pendulum.parse(str(df.index.max().date()))

    for day in pendulum.period(start, end).range('days'):
        day_str = day.to_date_string()
        hourly_wx = df[day_str].between_time('9:00', '18:00')
        df_out.loc[day_str, 'min_temp'] = hourly_wx.temperature.min()
        df_out.loc[day_str, 'max_temp'] = hourly_wx.temperature.max()
        df_out.loc[day_str, 'is_precip'] = is_precip_day(hourly_wx.precip_type)

    df_out.reset_index(inplace=True)
    df_out.columns = ['date', 'min_temp', 'max_temp', 'is_precip']
    df_out.dropna(inplace=True)
    df_out.to_excel(dst)


if __name__ == '__main__':
    main(sys.argv[1:])
