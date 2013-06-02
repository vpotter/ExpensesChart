# coding: utf-8

import csv
from dbfpy import dbf
from collections import defaultdict
import dateutil.parser
from app import app


def ffloat(val):
    return float(str(val).replace(',', '.'))


def detect_category(description, categories):
    for name, values in categories.items():
        for v in values:
            if v in description:
                return name[0].upper() + name.replace('_', ' ')[1:]
    return 'Unknown'


def parse_csv_file(csvfile, categories, schema='alfabank'):
    """ Parses expenses from csv file (only Alfabank is supported) """

    csv_schema = app.config['CSV_SCHEMA'][schema]

    rows = csv.reader(csvfile, delimiter=csv_schema.get('delimiter', ';'))
    rows.next()

    result = defaultdict(list)

    for row in rows:
        row = [item.decode(csv_schema['encoding']) for item in row]
        if row[csv_schema['currency']] == 'RUR':
            row[csv_schema['currency']] = 'RUB'
        category = detect_category(row[csv_schema['description']], categories)
        result[category].append({
                'amount': ffloat(row[csv_schema['amount']]),
                'date': dateutil.parser.parse(row[csv_schema['date']],
                                              dayfirst=True),
                'reference': row[csv_schema['reference']],
                'description': row[csv_schema['description']],
                'currency': row[csv_schema['currency']],
                })
    return result


def parse_rates_file(dbffile):
    dbf_table = dbf.Dbf(dbffile)
    result = []
    for record in dbf_table:
        rec_dict = record.asDict()
        result.append({'currency': rec_dict['CHAR_CODE'],
                       'rate': rec_dict['CURS'],
                       'date': rec_dict['DATA'],
                       })
    return result
