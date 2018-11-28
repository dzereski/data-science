"""
get-sales-history
~~~~~~~~~~~~~~~~
Gather store sales data from Square using the Connect V1 API.
"""

import os
import json
from collections import OrderedDict

import pendulum
import holidays
from openpyxl import Workbook

from wrangletools import (writexlrow, get_data_path)

import requests


def sqv2_get_transactions(start_date):
    """ Generator function to get transaction data from Square.  Call
    the Square V2 API for transactions and paginate through the results.
    """

    # Access token and location ID are stored as env vars
    access_token = os.environ.get('SQ_ACCESS_TOKEN')
    sq_location = os.environ.get('SQ_LOCATION')

    sq_headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'
    }

    endpoint_path = 'https://connect.squareup.com/v2/locations/{}/transactions?begin_time={}T00:00:00Z'.format(sq_location, start_date)
    cursor = ''
    page = 0
    more_results = True

    while more_results is True:
        page += 1
        print('...page {}'.format(page))

        if len(cursor) > 0:
            url = '{}&cursor={}'.format(endpoint_path, cursor)
        else:
            url = endpoint_path

        r = requests.get(url, headers=sq_headers)
        if r.status_code != requests.codes.ok:
            raise RuntimeError(r.status_code, r.text)

        resp = r.json()
        cursor = resp.get('cursor', None)
        trans = resp.get('transactions', None)
        more_results = True if cursor is not None else False

        for t in trans:
            yield(t)


_THANKSGIVING = pendulum.datetime(2017, 11, 23)
_NEWYEARS = pendulum.datetime(2018, 1, 1)


def init_open_days():
    store_holidays = holidays.UnitedStates()

    # 2018 Federal Holidays when store was open
    open_2018 = ['2018-01-15', '2018-02-19', '2018-10-08', '2018-11-12']

    for day in open_2018:
        store_holidays.pop(day)

    # Closed first week of Jan 2017 for renovations
    store_holidays.append(['2018-01-09', '2018-01-10', '2018-01-11', '2018-01-12'])

    # Snow day
    store_holidays.append('2018-03-13')

    # Closed Labor Day weekend
    store_holidays.append('2018-09-01')

    def is_open(day):
        if day.day_of_week == 0:
            if day > _THANKSGIVING and day < _NEWYEARS:
                return True
            else:
                return False
        elif day in store_holidays:
            return False
        else:
            return True

    return is_open


def init_holidays():
    us_holidays = holidays.UnitedStates()

    def is_holiday(day):
        if day in us_holidays:
            return True
        else:
            return False

    return is_holiday


def black_swan_adjust(date_str):
    sale_adj = 0
    cust_adj = 0

    # First installment of kids' saddle
    if date_str == '2018-02-23':
        sale_adj = 1050
        cust_adj = 2
    # Second installment of kids' saddle
    elif date_str == '2018-02-24':
        sale_adj = 750
        cust_adj = 1
    # Adult saddle that was returned
    elif date_str == '2018-08-02':
        sale_adj = 2995
        cust_adj = 1
    # Above saddle was finally purchased
    elif date_str == '2018-08-11':
        sale_adj = 2995
        cust_adj = 1
    # Team shopping event for boarding school
    elif date_str == '2018-09-22':
        sale_adj = 5300
        cust_adj = 12
    else:
        sale_adj = 0
        cust_adj = 0

    return sale_adj, cust_adj


def main():

    # Local timezone. Will need this to converte UTC sales dates
    # returned from Square's API to local time
    local_zone = pendulum.today().timezone_name

    # Get Square sales since opening (and data available in Square)
    START_DATE = '2017-11-17'

    # Initialize 'open days' for the store. US Holidays plus days closed
    # for renovations, snow, etc
    is_open = init_open_days()

    # Initialize US holidays.  Useful to track holidays when the store
    # was open
    is_us_holiday = init_holidays()

    print('Getting sales since {} from Square'.format(START_DATE))

    # Call the Square Sales API endpoint and store the total net sale
    # for each transaction in an ordered dict to preserve date order.
    # Also track the number of customers per day. Customers map very
    # closely to transactions.  It's quite rare for customers to make
    # more than one purchase in a day for this store.

    sales_by_day = OrderedDict()
    customers_by_day = OrderedDict()

    for t in sqv2_get_transactions(START_DATE):
        # Convert from UTC dates returned by the API to local
        utc_sale_dt = pendulum.parse(t['created_at'])
        local_dt = utc_sale_dt.in_tz(local_zone)
        sale_date_str = local_dt.to_date_string()

        total = 0.0

        # Each transaction can have more than one "tender", ie paying
        # some with cash, some on a card
        for m in t['tenders']:
            total += int(m['amount_money']['amount']) / 100.0

        sales_by_day[sale_date_str] = sales_by_day.get(sale_date_str, 0.0) + total
        customers_by_day[sale_date_str] = customers_by_day.get(sale_date_str, 0) + 1
        # print(json.dumps(t, indent=4, sort_keys=True))

    # Create the Excel workbook to store data and write the header
    wb = Workbook()
    ws = wb.active
    ws.title = 'Summary'

    row = writexlrow(ws, 1, ['date', 'year', 'month', 'week', 'day', 'is_open', 'is_holiday', 'sales', 'customers', 'avg_sale'])

    # Iterate through all dates since opening and save to the Excel workbook.
    # This approach will write 0.0 on days where the business is not open and
    # Square has no data.  This will capture zero sale days on Sundays, holidays,
    # snow days, etc.
    start = pendulum.parse(START_DATE)
    end = pendulum.today()

    for day in pendulum.period(start, end).range('days'):
        sales = 0.0
        customers = 0.0
        avg_sale = 0.0

        date_str = day.to_date_string()
        day_name = day.strftime('%a').lower()

        is_holiday = is_us_holiday(day)

        is_store_open = is_open(day)

        if is_store_open is True:
            if date_str in sales_by_day:
                sales = sales_by_day[date_str]

            if date_str in customers_by_day:
                customers = customers_by_day[date_str]

            if customers > 0 and sales > 0:
                avg_sale = sales / customers

            sale_adj, cust_adj = black_swan_adjust(date_str)

            sales -= sale_adj
            customers -= cust_adj

        row = writexlrow(ws, row, [date_str, day.year, day.strftime('%b'), day.week_of_year, day_name, int(is_store_open), int(is_holiday), sales, customers, avg_sale])

    wb.save(get_data_path('daily-sales.xlsx'))


# -----------------------


if __name__ == "__main__":
    main()
