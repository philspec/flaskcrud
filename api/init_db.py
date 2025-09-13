from pymongo import MongoClient


def initialize_items_collection(client: MongoClient, db_name: str) -> None:
    """Create `items` collection with a simple validator for name, quantity, price.

    This is idempotent: if the collection exists, it will try to update the validator.
    """
    db = client.get_database(db_name)
    coll_name = 'items'
    validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['name', 'quantity', 'price'],
            'properties': {
                'name': {'bsonType': 'string', 'description': 'must be a string'},
                'quantity': {'bsonType': 'int', 'minimum': 0, 'description': 'must be an int'},
                'price': {'bsonType': ['double', 'int'], 'minimum': 0, 'description': 'must be a number'},
            }
        }
    }
    try:
        if coll_name in db.list_collection_names():
            db.command({'collMod': coll_name, 'validator': validator, 'validationLevel': 'moderate'})
        else:
            db.create_collection(coll_name, validator=validator)
    except Exception:
        # Be tolerant in serverless deployment environments where create_collection may fail
        pass


