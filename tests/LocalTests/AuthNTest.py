# client.py
import requests

# Step 1: Obtain token from Auth Server
auth_url = "http://localhost:8001/token"
auth_data = {"username": "alice", "password": "password123"}

resp = requests.post(auth_url, data=auth_data)
resp.raise_for_status()
token = resp.json().get("access_token")
print("Obtained JWT token:", token)

# Step 2: Use token to call Falcon protected endpoint
api_url = "http://localhost:8001/admin"
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(api_url, headers=headers)
print("Falcon API response:", resp.json())
