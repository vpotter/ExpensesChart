import os
import yaml
import json
from flask import (request, render_template, redirect, url_for, Blueprint,
    abort)
from app import app, db
from dateutil.parser import parse as parse_date
from datetime import date, timedelta
from parser import parse_csv_file, parse_rates_file
from charts import expenses_pie_chart
from models import Payment, ExchangeRate

charts = Blueprint('charts', __name__, template_folder='templates')


def store_parsed_data(parsed_data, bank):
    for category, rows in parsed_data.items():
        if category == 'Skip':
            continue
        for row in [r for r in rows if r['reference'] != 'HOLD']:
            try:
                payment = Payment(category=category, bank=bank, **row)
                db.session.add(payment)
                db.session.commit()
            except Exception:
                db.session.rollback()


@charts.route('/upload/expenses', methods=['POST'])
def expenses_upload_form():
    if request.method == 'POST':
        categories = yaml.load(open(os.path.join(app.config['PROJECT_DIR'],
                                    'categories.yml')))
        parsed_data = parse_csv_file(request.files['csv_file'], categories,
                                     request.form['bank'])
        store_parsed_data(parsed_data, request.form['bank'])
    return redirect(url_for('charts.chart'))


@charts.route('/upload/rates', methods=['POST'])
def rates_upload_form():
    if request.method == 'POST':
        parsed_data = parse_rates_file(request.files['dbf_file'])

        for rate_record in parsed_data:
            try:
                rate = ExchangeRate(**rate_record)
                db.session.add(rate)
                db.session.commit()
            except Exception:
                db.session.rollback()

    return redirect(url_for('charts.chart'))


@charts.route('/chart/data', methods=['GET'])
def pie_chart_data():
    date_from = request.args.get('date_from')
    date_from = parse_date(date_from).date() if date_from else \
                date.today() - timedelta(days=30)

    date_to = request.args.get('date_to')
    date_to = parse_date(date_to).date() if date_to else date.today()

    pie_data, date_range = expenses_pie_chart(date_from, date_to, 'RUB')

    total = sum([item[1] for item in pie_data[1:]])
    return json.dumps({
                'pie_data': pie_data,
                'date_from': str(date_range[0]),
                'date_to': str(date_range[1]),
                'total': total,
                'last_rate_date': ExchangeRate.query.order_by(ExchangeRate.date.desc()).first().date.strftime('%Y-%m-%d')})

@charts.route('/chart/', methods=['GET'])
def chart():
    return render_template('charts.html')


@charts.route('/chart/category', methods=['GET'])
def get_category():
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    currency = request.args.get('currency') or app.config['DEFAULT_CURRENCY']

    if not (category and date_from and date_to):
        return abort(400)

    date_from = parse_date(date_from)
    date_to = parse_date(date_to)

    payments = Payment.query.filter_by(category=category).\
                  filter(Payment.date.between(date_from, date_to)).\
                  filter(Payment.amount > 0).\
                  order_by(Payment.date.desc()).all()

    response = []
    for payment in payments:
        item = {
        'date': payment.date.strftime('%Y-%m-%d'),
        'amount': '%.2f' % payment.convert_to(currency),
        'description': payment.description
        }
        response.append(item)

    return json.dumps(response)
