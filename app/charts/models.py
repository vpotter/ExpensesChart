from app import db


class UnsupportedCurencyError(Exception):
    pass


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(120), unique=True)
    date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(4))
    description = db.Column(db.String(256))
    category = db.Column(db.String(120))
    bank = db.Column(db.String(20))

    def __init__(self, reference, date, amount, currency, description,
                 category, bank):
        self.reference = reference
        self.date = date
        self.amount = amount
        self.currency = currency
        self.description = description
        self.category = category
        self.bank = bank

    def convert_to(self, currency):
        if self.currency == currency:
            amount = self.amount
        else:
            if currency == 'RUB':
                convert_currency = self.currency
            elif self.currency == 'RUB':
                convert_currency = currency
            else:
                raise UnsupportedCurencyError
            rate = ExchangeRate.query.filter_by(currency=convert_currency).filter(ExchangeRate.date<self.date).order_by(ExchangeRate.date.desc()).first()
            amount = self.amount * rate.rate
        return amount


class ExchangeRate(db.Model):
    __table_args__ = (db.UniqueConstraint('date', 'currency'), {})
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(4))
    date = db.Column(db.DateTime)
    rate = db.Column(db.Float)
