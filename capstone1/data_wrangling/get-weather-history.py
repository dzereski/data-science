"""
get-weather-history
~~~~~~~~~~~~~~~~
Get weather observations for the store's location from a given
START_DATE through yesterday using the Dark Sky API
"""

import os
import time

import requests
import pendulum
from openpyxl import Workbook

from wrangletools import (writexlrow, get_data_path)


def main():

    # First day of store sales data
    START_DATE = '2016-06-01'

    # Store lat/lon
    LAT = 42.359153
    LON = -71.785629

    # API credentials are stored as env vars
    api_key = os.environ.get('WX_KEY')

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date_time', 'summary', 'icon', 'temperature', 'apparent_temperature', 'precip_type', 'precip_intensity'])

    # Iterate through days from START_DATE and pull hourly WX observations
    # from Dark Sky for that day
    start = pendulum.parse(START_DATE)
    end = pendulum.yesterday()

    for day in pendulum.period(start, end).range('days'):
        print('Fetching WX for {}'.format(day.to_date_string()))
        url = 'https://api.darksky.net/forecast/{}/{},{},{}?exclude=daily,currently,flags'.format(api_key, LAT, LON, day.int_timestamp)

        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.status_code, r.text)

        data = r.json()

        # Extract each hourly observation and save to the Excel workbook
        for obs in data['hourly']['data']:
            obs_time = pendulum.from_timestamp(obs['time'])
            row = writexlrow(
                ws,
                row,
                [obs_time.to_datetime_string(),
                 obs['summary'],
                 obs['icon'],
                 obs['temperature'],
                 obs['apparentTemperature'],
                 obs.get('precipType', None),
                 obs['precipIntensity']])

        # Take a short nap to avoid API throttling issues
        time.sleep(0.2)

    # Save the Excel workbook in the data dir for this project
    wb.save(get_data_path('daily-weather.xlsx'))


if __name__ == '__main__':
    main()
