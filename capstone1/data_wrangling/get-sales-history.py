"""
get-sales-history
~~~~~~~~~~~~~~~~
Gather store sales data from Square using the Connect V1 API.
"""

import os
import json
from collections import OrderedDict

import pendulum
from openpyxl import Workbook

from wrangletools import (writexlrow, get_data_path)

import requests


def sqv1_api_call(endpoint_path):
    """Generator function for calls to the Square V1 API.
    Call the requested API endpoint, return each item in the JSON
    result and paginate through all results.
    """

    more_results = True
    next_page_url = endpoint_path
    page = 0

    access_token = os.environ.get('SQ_ACCESS_TOKEN')

    sq_headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'
    }

    while more_results is True:
        page += 1
        print('...page {}'.format(page))

        r = requests.get(next_page_url, headers=sq_headers)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.status_code, r.text)

        resp = r.json()

        if 'link' in r.headers:
            pagination_header = r.headers['link']
            next_page_url = pagination_header.split('<')[1].split('>')[0]
            more_results = True
        else:
            next_page_url = None
            more_results = False

        for item in resp:
            yield(item)


def main():

    # Get Square sales since opening (and data available in Square)
    START_DATE = '2017-11-17'

    # Local timezone. Will need this to converte UTC sales dates
    # returned from Square's API to local time
    local_zone = pendulum.today().timezone_name

    print('Getting sales since {} from Square'.format(START_DATE))

    # Call the Square Sales API endpoint and store the total net sale
    # for each transaction in an ordered dict to preserve date order
    location = os.environ.get('SQ_LOCATION')
    endpoint_path = 'https://connect.squareup.com/v1/{}/payments?begin_time={}T00:00:00Z'.format(location, START_DATE)

    sales_by_day = OrderedDict()

    for t in sqv1_api_call(endpoint_path):
        # Convert from UTC dates returned by the API to local
        utc_sale_dt = pendulum.parse(t['created_at'])
        local_dt = utc_sale_dt.in_tz(local_zone)
        sale_date_str = local_dt.to_date_string()

        amount = t['gross_sales_money']['amount'] / 100.0
        sales_by_day[sale_date_str] = sales_by_day.get(sale_date_str, 0.0) + amount
        # print(json.dumps(t, indent=4, sort_keys=True))

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date', 'year', 'month', 'week', 'day', 'sales'])

    # Iterate through all dates since opening and save to the Excel workbook.
    # This approach will write 0.0 on days where the business is not open and
    # Square has no data.  This will capture zero sale days on Sundays, holidays,
    # snow days, etc.
    start = pendulum.parse(START_DATE)
    end = pendulum.today()

    for day in pendulum.period(start, end).range('days'):
        date_str = day.to_date_string()
        if date_str in sales_by_day:
            sales = sales_by_day[date_str]
        else:
            sales = 0.0

        row = writexlrow(ws, row, [date_str, day.year, day.month, day.week_of_year, day.day_of_week, sales])

    wb.save(get_data_path('daily-sales.xlsx'))


# -----------------------


if __name__ == "__main__":
    main()
