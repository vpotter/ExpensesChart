# coding: utf-8

import csv
from collections import defaultdict
import dateutil.parser

def ffloat(val):
    return float(str(val).replace(',', '.'))

def detect_category(row, categories):
    for name, values in categories.items():
        for v in values:
            if v in row[5]:
                return name[0].upper() + name.replace('_', ' ')[1:]
    return 'Untracked'

def parse_csv_file(csvfile, categories, delimiter=';'):
    """ Parses expenses from csv file (only Alfabank is supported) """
    rows = csv.reader(csvfile, delimiter=delimiter)
    rows.next()

    result = defaultdict(list)

    for row in rows:
        row = [item.decode('utf-8') for item in row]
        category = detect_category(row, categories)
        result[category].append((ffloat(row[-2]),
                                dateutil.parser.parse(row[3], dayfirst=True),
                                row[5]))
    return result
