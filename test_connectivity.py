import requests
import os
# --- Configuration ---
INSTANCE = os.environ.get('SERVICENOW_INSTANCE_NAME')
BASE_URL = os.environ.get('SERVICENOW_INSTANCE')
USERNAME = os.environ.get('SERVICENOW_USERNAME')
PASSWORD = os.environ.get('SERVICENOW_PASSWORD')

# --- Test Connection ---
def test_connection():
    url = f"{BASE_URL}/api/now/table/sys_user?sysparm_limit=1"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            url,
            auth=(USERNAME, PASSWORD),
            headers=headers
        )

        if response.status_code == 200:
            print("✅ Connection Successful!")
            print(f"   Instance: {BASE_URL}")
            print(f"   Status Code: {response.status_code}")
        else:
            print(f"❌ Connection Failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_connection()
