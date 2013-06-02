#!/usr/bin/env python

import os
import sys
import yaml

_basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_basedir)

from app import app, db
from app.charts.models import Payment
from app.charts.parser import detect_category

categories = yaml.load(open(os.path.join(app.config['PROJECT_DIR'],
                                    'categories.yml')))
_row = ['' for i in range(6)]
payments = Payment.query.all()

for payment in payments:
    new_cat = detect_category(payment.description, categories)
    if new_cat == 'Skip':
        db.session.delete(payment)
    elif payment.category != new_cat:
        payment.category = new_cat

db.session.commit()
