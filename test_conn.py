from dotenv import dotenv_values
config = dotenv_values('.env')
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
MONGODB_URI = config.get('MONGODB_URI')
MONGO_DB_NAME = config.get('MONGO_DB_NAME')
# Create a new client and connect to the server
client = MongoClient(MONGODB_URI)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)