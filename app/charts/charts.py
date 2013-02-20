# coding: utf-8
from app import db
from sqlalchemy import func
from models import Payment


def expenses_pie_chart(date_from=None, date_to=None, currency='USD'):
    """ Prepares expenses data for Google Pie chart """

    payments = db.session.query(Payment.category, func.sum(Payment.amount)).\
                               filter_by(currency=currency)

    if date_from:
        payments = payments.filter(Payment.date >= date_from)
    if date_to:
        payments = payments.filter(Payment.date <= date_to)
    payments = payments.group_by(Payment.category).all()

    dates = db.session.query(func.min(Payment.date),
                             func.max(Payment.date)).\
                       filter_by(currency=currency).first()
    result = [['Category', 'Spent amount']]
    for payment in payments:
        result.append([payment[0], payment[1]])

    return result, (date_from or dates[0].date(), date_to or dates[1].date())


def category_line_chart(category_raw_data):
    """ Prepares category data for Google Line chart """
    pass
