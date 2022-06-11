import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

DB_HOST = os.environ.get('DB_HOST','127.0.0.1:5432')
DB_USER = os.environ.get('DB_USER','postgres')
DB_NAME = os.environ.get('DB_NAME','fyyur')
DB_PASSWORD = os.environ.get('DB_PASSWORD','1987')
DB_PATH = 'postgresql://{}:{}@{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False