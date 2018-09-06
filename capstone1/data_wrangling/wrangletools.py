import time
import datetime


def get_unix_time(date_obj):
    dt = datetime.datetime.combine(date_obj, datetime.time.min)
    unix_time = int(time.mktime(dt.timetuple()))

    return unix_time


def writexlrow(ws, row, values, font=None):
    for col, name in enumerate(values):
        ws.cell(column=col + 1, row=row).value = name
        if font is not None:
            ws.cell(column=col + 1, row=row).font = font
    return row + 1


def get_data_path(fname):
    DATA_DIR = '../data/'
    return DATA_DIR + fname
