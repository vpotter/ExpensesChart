import os


PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_DIR, 'app.db')
CSV_SCHEMA = {
    'alfabank': {
        'amount': 7,
        'description': 5,
        'date': 3,
        'reference': 4,
        'delimiter': ';',
    }
}
