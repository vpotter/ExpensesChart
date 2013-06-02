import os

PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_DIR, 'app.db')
DEFAULT_CURRENCY = 'RUB'
CSV_SCHEMA = {
    'alfabank': {
        'amount': 7,
        'description': 5,
        'encoding': 'utf-8',
        'date': 3,
        'reference': 4,
        'delimiter': ';',
        'currency': 2
    },
    'tcsbank': {
        'amount': 6,
        'description': 9,
        'currency': 7,
        'encoding': 'cp1251',
        'date': 0,
        'reference': 0,
        'delimiter': ';'
    }
}
