#!/usr/bin/env python

import flask
from flask.ext.sqlalchemy import SQLAlchemy
import json

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


def to_json(value):
    return json.dumps(value)

app.jinja_env.filters['to_json'] = to_json

from charts.views import charts as charts_bp
app.register_blueprint(charts_bp)


@app.route('/')
def index():
    return flask.redirect(flask.url_for('charts.chart'))
