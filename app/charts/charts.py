# coding: utf-8
from app import db
from flask import current_app
from sqlalchemy import func
from datetime import date
from collections import defaultdict

from models import Payment, ExchangeRate


def expenses_pie_chart(date_from=None, date_to=None, currency=None):
    """ Prepares expenses data for Google Pie chart """
    currency = currency or current_app.config['DEFAULT_CURRENCY']
    payments = db.session.query(Payment.category, func.sum(Payment.amount)).\
                               filter_by(currency=currency)

    date_from = date_from or date.min
    date_to = date_to or date.today()

    payments = Payment.query.filter(Payment.date.between(date_from, date_to))
    dates = [p.date for p in payments]

    per_category = defaultdict(lambda: 0)
    for payment in payments:
        per_category[payment.category] += payment.convert_to(currency)

    categories = []
    for category, amount in per_category.items():
        categories.append((category, round(amount, 2)))

    categories.sort(key=lambda x: x[1], reverse=True)
    result = [['Category', 'Spent amount']]
    result.extend(categories)

    return result, (date_from or min(dates), date_to or max(dates))

