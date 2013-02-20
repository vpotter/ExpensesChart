# coding: utf-8

import csv
from collections import defaultdict
import dateutil.parser
from app import app


def ffloat(val):
    return float(str(val).replace(',', '.'))


def detect_category(row, categories):
    for name, values in categories.items():
        for v in values:
            if v in row[5]:
                return name[0].upper() + name.replace('_', ' ')[1:]
    return 'Untracked'


def parse_csv_file(csvfile, categories, schema='alfabank'):
    """ Parses expenses from csv file (only Alfabank is supported) """

    csv_schema = app.config['CSV_SCHEMA'][schema]

    rows = csv.reader(csvfile, delimiter=csv_schema.get('delimiter', ';'))
    rows.next()

    result = defaultdict(list)

    for row in rows:
        row = [item.decode('utf-8') for item in row]
        category = detect_category(row, categories)
        result[category].append({
                'amount': ffloat(row[csv_schema['amount']]),
                'date': dateutil.parser.parse(row[csv_schema['date']],
                                              dayfirst=True),
                'reference': row[csv_schema['reference']],
                'description': row[csv_schema['description']]
                })
    return result
