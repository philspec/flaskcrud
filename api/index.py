from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from init_db import initialize_items_collection
from dotenv import dotenv_values

# Load configuration exclusively from a .env file (dotenv_values returns a dict)
# This avoids direct `os` usage and makes local config explicit.
config = dotenv_values('.env')

# Required configuration keys should be set in the .env file.
MONGODB_URI = config.get('MONGODB_URI')
MONGO_DB_NAME = config.get('MONGO_DB_NAME')
ADMIN_TOKEN = config.get('ADMIN_TOKEN', '')

if not MONGODB_URI:
    raise RuntimeError('MONGODB_URI must be provided in .env')
if not MONGO_DB_NAME:
    raise RuntimeError('MONGO_DB_NAME must be provided in .env')

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client.get_database(MONGO_DB_NAME)
items_collection = db.get_collection('items')

app = Flask(__name__)


def _serialize_item(doc: dict) -> dict:
    return {
        'id': str(doc.get('_id')),
        'name': doc.get('name'),
        'quantity': doc.get('quantity'),
        'price': doc.get('price'),
    }


@app.route('/items', methods=['POST'])
def create_item():
    payload = request.get_json(force=True)
    if not payload:
        abort(400, 'JSON body required')

    name = payload.get('name')
    quantity = payload.get('quantity')
    price = payload.get('price')

    if not isinstance(name, str) or not name:
        abort(400, 'name (string) is required')
    if not isinstance(quantity, int):
        abort(400, 'quantity (int) is required')
    if not (isinstance(price, int) or isinstance(price, float)):
        abort(400, 'price (number) is required')

    doc = {'name': name, 'quantity': quantity, 'price': float(price)}
    result = items_collection.insert_one(doc)
    created = items_collection.find_one({'_id': result.inserted_id})
    return jsonify(_serialize_item(created)), 201


@app.route('/items', methods=['GET'])
def list_items():
    cursor = items_collection.find()
    items = [_serialize_item(d) for d in cursor]
    return jsonify(items)


@app.route('/items/<item_id>', methods=['GET'])
def get_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        abort(400, 'invalid id')
    doc = items_collection.find_one({'_id': oid})
    if not doc:
        abort(404, 'item not found')
    return jsonify(_serialize_item(doc))


@app.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        abort(400, 'invalid id')
    payload = request.get_json(force=True)
    if not payload:
        abort(400, 'JSON body required')

    update_fields = {}
    if 'name' in payload:
        if not isinstance(payload['name'], str) or not payload['name']:
            abort(400, 'name must be a non-empty string')
        update_fields['name'] = payload['name']
    if 'quantity' in payload:
        if not isinstance(payload['quantity'], int):
            abort(400, 'quantity must be an int')
        update_fields['quantity'] = payload['quantity']
    if 'price' in payload:
        if not (isinstance(payload['price'], int) or isinstance(payload['price'], float)):
            abort(400, 'price must be a number')
        update_fields['price'] = float(payload['price'])

    if not update_fields:
        abort(400, 'no updatable fields provided')

    result = items_collection.update_one({'_id': oid}, {'$set': update_fields})
    if result.matched_count == 0:
        abort(404, 'item not found')
    updated = items_collection.find_one({'_id': oid})
    return jsonify(_serialize_item(updated))


@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        abort(400, 'invalid id')
    result = items_collection.delete_one({'_id': oid})
    if result.deleted_count == 0:
        abort(404, 'item not found')
    return jsonify({'deleted': True}), 200


# Admin route to initialize or reconfigure the `items` collection on demand.
# Protect this endpoint by setting `ADMIN_TOKEN` in environment and passing
# an `Authorization: Bearer <token>` header or `?admin_token=<token>` query param.
@app.route('/admin/init-db', methods=['POST'])
def admin_init_db():
    provided = request.headers.get('Authorization', '')
    if provided.startswith('Bearer '):
        provided = provided.replace('Bearer ', '', 1).strip()
    if not provided:
        provided = request.args.get('admin_token', '')
    if ADMIN_TOKEN and provided != ADMIN_TOKEN:
        abort(403, 'forbidden')
    try:
        initialize_items_collection(client, MONGO_DB_NAME)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    return jsonify({'initialized': True}), 200


@app.errorhandler(400)
def handle_400(e):
    return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def handle_404(e):
    return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)


