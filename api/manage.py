"""Simple CLI to run administrative tasks for the flaskcrud app.

Usage:
    python api/manage.py init-db
"""
import sys
from dotenv import dotenv_values
from pymongo import MongoClient
from init_db import initialize_items_collection

# Load config only from .env to avoid direct os usage
config = dotenv_values('.env')

def main(argv):
    if len(argv) < 2:
        print('usage: python api/manage.py init-db')
        return 1
    cmd = argv[1]
    mongo_uri = config.get('MONGODB_URI')
    db_name = config.get('MONGO_DB_NAME')
    if not mongo_uri or not db_name:
        print('MONGODB_URI and MONGO_DB_NAME must be set in .env')
        return 2
    client = MongoClient(mongo_uri)
    if cmd == 'init-db':
        print('Initializing items collection...')
        initialize_items_collection(client, db_name)
        print('Done')
        return 0
    else:
        print('unknown command')
        return 2

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))


