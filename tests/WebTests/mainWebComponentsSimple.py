from Runtimes.runtime import runtime
from MetaArchitecture.MetaArchitecture import MetaArchitecture
from requests.auth import HTTPBasicAuth
import requests
import json, time

# Initialize architecture and runtime
meta = MetaArchitecture()
opencom = runtime(meta)

# Create components
calc1 = opencom.create("web", "Examples.Calculator", "Calculator1", False)
add1 = opencom.create("web", "Examples.Adder", "Adder1", False)
sub1 = opencom.create("web", "Examples.Subber", "Subber1", False)

# Print all components
print("\n🧱 Components created:")
for comp in meta.getAllComponents():
    print(f" - {comp}")

# Connect components
print("\n🔗 Connecting components:")
print(opencom.connect("web", calc1, add1, "Examples.IAdd"))
print(opencom.connect("web", calc1, sub1, "Examples.ISub"))

# Basic auth setup
auth = HTTPBasicAuth("user", "pass")
base_url = "http://localhost:8000/Calculator1"

# Helper function to perform POST request and print result
def call_api(endpoint, a, b):
    url = f"{base_url}/{endpoint}?a={a}&b={b}"
    try:
        response = requests.post(url, auth=auth)
        response.raise_for_status()
        data = response.json()
        print(f"✅ {endpoint}({a}, {b}) = {data.get('result')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling {endpoint}: {e}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response from {endpoint}")
    except KeyError:
        print(f"❌ 'result' key not found in response: {response.text}")

# Test calculator methods
print("\n🧪 Testing Calculator:")
call_api("add", 676, 8)
call_api("sub", 676, 8)
time.sleep(2)

# Delete the Subber component
print("\n❌ Deleting 'Subber1' component:")
opencom.delete("web", "Adder1")

# Test subtraction again after deletion
print("\n🧪 Testing subtraction after component deletion:")
call_api("sub", 676, 8)
