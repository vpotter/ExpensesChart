from app import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(120), unique=True)
    date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(4))
    description = db.Column(db.String(256))
    category = db.Column(db.String(120))

    def __init__(self, reference, date, amount, currency, description,
                 category):
        self.reference = reference
        self.date = date
        self.amount = amount
        self.currency = currency
        self.description = description
        self.category = category
