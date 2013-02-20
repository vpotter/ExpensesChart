import os
from flask import (request, render_template, redirect, url_for, Blueprint,
    abort)
from app import app, db
from dateutil.parser import parse as parse_date
from datetime import date, timedelta
from parser import parse_csv_file
from charts import expenses_pie_chart
from models import Payment
import yaml
import json

charts = Blueprint('charts', __name__, template_folder='templates')


def store_parsed_data(parsed_data):
    for category, rows in parsed_data.items():
        if category == 'Skip':
            continue
        for row in [r for r in rows if r['reference'] != 'HOLD']:
            try:
                payment = Payment(category=category, currency='USD', **row)
                db.session.add(payment)
                db.session.commit()
            except Exception:
                db.session.rollback()


@charts.route('/upload', methods=['POST'])
def upload_form():
    if request.method == 'POST':
        categories = yaml.load(open(os.path.join(app.config['PROJECT_DIR'],
                                    'categories.yml')))
        parsed_data = parse_csv_file(request.files['csv_file'], categories)
        store_parsed_data(parsed_data)
    return redirect(url_for('charts.pie_chart'))


@charts.route('/chart', methods=['GET'])
def pie_chart():
    date_from = request.args.get('date_from')
    date_from = parse_date(date_from).date() if date_from else \
                date.today() - timedelta(days=30)

    date_to = request.args.get('date_to')
    date_to = parse_date(date_to).date() if date_to else date.today()

    pie_data, date_range = expenses_pie_chart(date_from, date_to)
    return render_template('pie_chart.html', pie_data=pie_data,
                           date_range=date_range)


@charts.route('/chart/category', methods=['GET'])
def get_category():
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    currency = 'USD'

    if not (category and date_from and date_to):
        return abort(400)

    date_from = parse_date(date_from)
    date_to = parse_date(date_to)

    payments = db.session.query(Payment.date, Payment.amount,
                                Payment.description).\
                  filter_by(currency=currency, category=category).\
                  filter(Payment.date.between(date_from, date_to)).\
                  filter(Payment.amount > 0).\
                  order_by(Payment.date.desc()).all()

    keys = ['date', 'amount', 'description']
    response = []
    for payment in payments:
        payment = list(payment)
        payment[0] = payment[0].strftime('%Y-%m-%d')
        response.append(dict(zip(keys, payment)))

    return json.dumps(response)
