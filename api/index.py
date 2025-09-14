from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import uuid
from bson.objectid import ObjectId

# simple config loader
# Prefer real environment variables (e.g. Vercel) and fall back to a local .env
load_dotenv()  # populate os.environ from .env when present
MONGODB_URI = os.environ.get('MONGODB_URI')
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')

# Validate that essential config is available
if not MONGODB_URI:
    raise RuntimeError('MONGODB_URI must be provided as an environment variable (or in .env for local dev)')
if not MONGO_DB_NAME:
    raise RuntimeError('MONGO_DB_NAME must be provided as an environment variable (or in .env for local dev)')

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
    payload = request.get_json(silent=True) or {}
    name = payload.get('name')
    quantity = payload.get('quantity')
    price = payload.get('price')

    # minimal validation
    if not name:
        return jsonify({'error': 'name required'}), 400

    doc = {'name': name, 'quantity': quantity, 'price': price}
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
        return jsonify({'error': 'Invalid ID format'}), 400
    doc = items_collection.find_one({'_id': oid})
    if not doc:
        return jsonify({'error': 'not found'}), 404
    return jsonify(_serialize_item(doc))


@app.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        return jsonify({'error': 'Invalid ID format'}), 400
    payload = request.get_json(silent=True) or {}
    update_fields = {}
    for k in ('name', 'quantity', 'price'):
        if k in payload:
            update_fields[k] = payload[k]
    if not update_fields:
        return jsonify({'error': 'no fields provided'}), 400
    result = items_collection.update_one({'_id': oid}, {'$set': update_fields})
    if result.matched_count == 0:
        return jsonify({'error': 'not found'}), 404
    doc = items_collection.find_one({'_id': oid})
    return jsonify(_serialize_item(doc))


@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except Exception:
        return jsonify({'error': 'Invalid ID format'}), 400
    result = items_collection.delete_one({'_id': oid})
    if result.deleted_count == 0:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'deleted': True}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)), debug=True)


