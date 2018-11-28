"""
wrangletools
~~~~~~~~~~~~~~~~
A collection of utility functions used across data gathering modules
"""


def writexlrow(ws, row, values, font=None):
    """Write a row of data to an Excel workbook and apply
    the given font
    """
    for col, name in enumerate(values):
        ws.cell(column=col + 1, row=row).value = name
        if font is not None:
            ws.cell(column=col + 1, row=row).font = font
    return row + 1


def get_data_path(fname):
    """Return the path to a given data file name.
    """
    DATA_DIR = '../data/'
    return DATA_DIR + fname
