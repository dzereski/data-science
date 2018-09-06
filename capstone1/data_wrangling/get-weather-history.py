import os
import time
import datetime

import requests
from openpyxl import Workbook

from wrangletools import (get_unix_time, writexlrow, get_data_path)


def main():

    # First day of store sales data
    START_DATE = '2016-06-01'

    # Store lat/lon
    LAT = 42.359153
    LON = -71.785629

    # API credentials are stored as env vars
    api_key = os.environ.get('WX_KEY')

    # datetimes used to iterate through days to acquire WX data
    end_dt = datetime.datetime.now()
    one_day = datetime.timedelta(days=1)
    wx_dt = datetime.datetime.strptime(START_DATE, '%Y-%m-%d')

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date_time', 'summary', 'icon', 'temperature', 'apparent_temperature', 'precip_type', 'precip_intensity'])

    # Iterate through days from START_DATE and pull hourly WX observations
    # from Dark Sky for that day
    while wx_dt < end_dt:
        print('Fetching WX for {}'.format(wx_dt.date()))
        unix_time = get_unix_time(wx_dt)
        url = 'https://api.darksky.net/forecast/{}/{},{},{}?exclude=daily,currently,flags'.format(api_key, LAT, LON, unix_time)

        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.text)

        data = r.json()

        # Extract each hourly observation and save to the Excel workbook
        for obs in data['hourly']['data']:
            dt = datetime.datetime.fromtimestamp(obs['time'])
            time_str = dt.strftime('%Y-%m-%d %H:%M%S')
            row = writexlrow(
                ws,
                row,
                [time_str,
                 obs['summary'],
                 obs['icon'],
                 obs['temperature'],
                 obs['apparentTemperature'],
                 obs.get('precipType', None),
                 obs['precipIntensity']])

        # Advance to the next day and take a short nap to avoid API
        # throttling issues
        wx_dt += one_day
        time.sleep(0.2)

    # Save the Excel workbook in the data dir for this project
    wb.save(get_data_path('daily-weather.xlsx'))


if __name__ == '__main__':
    main()
