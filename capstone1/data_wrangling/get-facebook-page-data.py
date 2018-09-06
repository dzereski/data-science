import os
import datetime

import requests
from openpyxl import Workbook

from wrangletools import (get_unix_time, writexlrow, get_data_path)


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

    # datetimes used to iterate through the FB data. Pull 4 weeks at a time
    # using since/until API params
    end_dt = datetime.datetime.now()
    start_dt = datetime.datetime.strptime(START_DATE, '%Y-%m-%d')
    four_weeks = datetime.timedelta(weeks=4)
    one_day = datetime.timedelta(days=1)
    until_dt = start_dt + four_weeks

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date', 'page_impressions_organic_unique'])

    # Iterate through days from START_DATE and call FB's Graph API to pull
    # the requested page metric
    while start_dt < end_dt:
        print('Fetching {} - {}'.format(start_dt, until_dt))

        url = 'https://graph.facebook.com/{}/insights/{}?period=day&since={}&until={}'.format(PAGE_ID, METRIC, get_unix_time(start_dt), get_unix_time(until_dt))

        r = requests.get(url, headers=fb_headers)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.text)

        # Iterate through the days of data returned and save as an Excel row
        data = r.json()['data'][0]

        for item in data['values']:
            (fb_date, fb_time) = item['end_time'].split('T')
            fb_dt = datetime.datetime.strptime(fb_date, '%Y-%m-%d')
            date_str = str(fb_dt - one_day).split(' ')[0]

            row = writexlrow(ws, row, [date_str, item['value']])

        # The data returned is basically advanced one day to include the 'since' date.
        # Rewind by a date to accomodate this and advance to the next 4-week period.
        start_dt = until_dt - one_day
        until_dt = start_dt + four_weeks

    wb.save(get_data_path('fb-{}.xlsx'.format(METRIC)))


if __name__ == '__main__':
    main()
