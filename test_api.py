import requests
import json

BASE_URL = "http://127.0.0.1:5000/items"

def post_item(item_data):
    """Posts a new item to the API."""
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(BASE_URL, headers=headers, data=json.dumps(item_data))
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("POST Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"POST Error: {err.response.status_code} - {err.response.text}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"POST Error: Could not connect to the API. Is your Flask app running? {err}")
        return None

def get_item(item_id):
    """Retrieves a specific item by its ID."""
    url = f"{BASE_URL}/{item_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"GET (ID: {item_id}) Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            print(f"GET (ID: {item_id}) Error: Item not found.")
        else:
            print(f"GET (ID: {item_id}) Error: {err.response.status_code} - {err.response.text}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"GET Error: Could not connect to the API. Is your Flask app running? {err}")
        return None

def get_all_items():
    """Retrieves all items from the API."""
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        print("GET All Items Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"GET All Items Error: {err.response.status_code} - {err.response.text}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"GET All Items Error: Could not connect to the API. Is your Flask app running? {err}")
        return None

def delete_item(item_id):
    """Deletes a specific item by its ID."""
    url = f"{BASE_URL}/{item_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        print(f"DELETE (ID: {item_id}) Response:", response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            print(f"DELETE (ID: {item_id}) Error: Item not found.")
        else:
            print(f"DELETE (ID: {item_id}) Error: {err.response.status_code} - {err.response.text}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"DELETE Error: Could not connect to the API. Is your Flask app running? {err}")
        return None

if __name__ == '__main__':
    print("--- Starting API Tests ---")

    # 1. Post a new item with only the 'name' field
    new_item_data = {"name": "Omulet","price": 1000,"quantity": 100}
    posted_item = post_item(new_item_data)
    item_id_to_test = None

    if posted_item and 'id' in posted_item:
        item_id_to_test = posted_item['id']
        print(f"Successfully posted item with ID: {item_id_to_test}")

        # 2. Get all items
        print("\n--- Getting all items ---")
        get_all_items()

        # 3. Get the newly created item
        print(f"\n--- Getting item with ID: {item_id_to_test} ---")
        get_item(item_id_to_test)

        # 4. Delete the item
        # print(f"\n--- Deleting item with ID: {item_id_to_test} ---")
        # delete_item(item_id_to_test)

        # 5. Try to get the deleted item (should be 404)
        print(f"\n--- Trying to get deleted item with ID: {item_id_to_test} ---")
        get_item(item_id_to_test)
    else:
        print("\nFailed to post an item, skipping further tests.")

    print("\n--- API Tests Finished ---")
