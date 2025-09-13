# flaskcrud

Simple Flask CRUD API using MongoDB Atlas. Designed for deployment to Vercel using the Python runtime.

Features
- Create an item
- Read all items
- Update an item
- Delete an item

Quickstart (local)

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following keys and your MongoDB Atlas values:

```
MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net
MONGO_DB_NAME=flaskcrud
# Optional: protect admin init endpoint
ADMIN_TOKEN=some-secret-token
```

3. Run the app (Vercel will use your environment variables from the dashboard). For local admin initialization use the CLI:

```bash
python api/manage.py init-db
```

API endpoints

- POST /items  { name, quantity, price }
- GET /items
- GET /items/:id
- PUT /items/:id { name?, quantity?, price? }
- DELETE /items/:id

Deploying to Vercel

1. Add your MongoDB Atlas connection string as `MONGODB_URI` in Vercel project environment variables.
2. Optionally set `INIT_DB=1` on first deploy to create the `items` collection validator.


