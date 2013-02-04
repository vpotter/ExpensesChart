# coding: utf-8
from itertools import chain

def expenses_pie_chart(raw_data):
    """ Prepares expenses data for Google Pie chart """

    result = [['Category', 'Spent amount']]
    for category, values in raw_data.items():
        result.append([category, int(sum(v[0] for v in values))])

    dates = [v[1] for v in chain(*raw_data.values())]
    return result, min(dates), max(dates)

def category_line_chart(category_raw_data):
    """ Prepares category data for Google Line chart """
    pass
