"""
get-facebook-page-data
~~~~~~~~~~~~~~~~
Gather data on a single page metric from Facebook's Graph API
from START_DATE through yesterday.
"""

import os

import requests
import pendulum
from openpyxl import Workbook

from wrangletools import (writexlrow, get_data_path)


def time_window_range(start_date):
    """Generator function to iterate through 60-day windows from
    the start date to yesterday. According to the docs, 90 days
    is the max range in since/until.
    """

    DAY_WINDOW_SIZE = 60

    start_dt = pendulum.parse(start_date)
    end_dt = pendulum.today()

    day_range = end_dt.diff(start_dt).in_days()
    windows_in_range = day_range // DAY_WINDOW_SIZE
    extra_days = day_range % DAY_WINDOW_SIZE

    # Since/Until works like range in Python in that the end
    # data is not included. Add one more day to get the full range
    for n in range(windows_in_range):
        since_dt = start_dt.add(days=(n * DAY_WINDOW_SIZE))
        until_dt = since_dt.add(days=DAY_WINDOW_SIZE + 1)

        yield since_dt, until_dt

    if extra_days > 0:
        since_dt = until_dt.subtract(days=1)
        until_dt = since_dt.add(days=extra_days + 1)
        yield since_dt, until_dt


def main():

    # API credentials are stored as env vars
    access_token = os.environ.get('FB_PAGE_TOKEN')

    # Pass the FB token in the request header
    fb_headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'
    }

    # ID of the business page, metric to acquire and start date
    PAGE_ID = 325293794166930
    METRIC = 'page_impressions_organic_unique'
    START_DATE = '2016-06-01'

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date', 'page_impressions_organic_unique'])

    # Iterate through days from START_DATE and call FB's Graph API to pull
    # the requested page metric
    for (start, end) in time_window_range(START_DATE):
        print('Fetching {} - {}'.format(start.date(), end.date()))

        url = 'https://graph.facebook.com/{}/insights/{}?period=day&since={}&until={}'.format(PAGE_ID, METRIC, start.int_timestamp, end.int_timestamp)

        r = requests.get(url, headers=fb_headers)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.status_code, r.text)

        # Iterate through the days of data returned and save as an Excel row
        data = r.json()['data'][0]

        for item in data['values']:
            # Note that the end_time returned when using since/until is advanced
            # by 1 day to reflect the metric of the since date.  Subtract a day
            # to make the days line up properly.
            utc_fb_dt = pendulum.parse(item['end_time'])
            date_str = utc_fb_dt.subtract(days=1).to_date_string()
            row = writexlrow(ws, row, [date_str, item['value']])

    wb.save(get_data_path('fb-{}.xlsx'.format(METRIC)))


if __name__ == '__main__':
    main()
