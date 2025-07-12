"""
Integration Test for Component Runtime & MetaArchitecture in AddasuSec

This script initializes and configures multiple Calculator, Adder, and Subber components,
connects them using the runtime, and performs both authenticated and unauthenticated calls.
It verifies disconnection behavior, dynamic metadata updates, and component inspection APIs.

Test Validations:
- Component creation, duplication handling
- Inter-component connections and disconnections
- Token-based secured interface access
- Metadata assignment and validation
- Interface and receptacle inspection APIs
- Component list and deletion
"""

from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
from MetaArchitecture.MetaArchitecture import MetaArchitecture
import requests
import sys

# Constants for reuse
RUNTIME_TYPE = "web"
IADD = "Examples.IAdd"
ISUB = "Examples.ISub"
AUTH_URL = "http://localhost:8676/token"
USERNAME = "alice"
PASSWORD = "password123"
base_url = "http://localhost:8000/Calculator1"

# Initialise runtime and meta
meta = MetaArchitecture()
sec_runtime = runtime(meta)

# Helper function to perform POST request and print result
def call_api(base_url, endpoint, a, b, token):
    url = f"{base_url}/{endpoint}?a={a}&b={b}"
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"✅ {endpoint}({a}, {b}) = {data.get('result')}")
        return data.get('result')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling {endpoint}: {e}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON response from {endpoint}")
    except KeyError:
        print(f"❌ 'result' key not found in response: {response.text}")



def run_tests(token):
    """Perform basic add and subtract operations to verify component connectivity."""
    print("\n🧪 Testing Calculator:")

    assert call_api(base_url, "add", 1, 2, token) == 3
    assert call_api(base_url, "sub", 8, 2, token) == 6
    print("Basic math operation tests passed")
    
def run_insecuretests():
    """Perform basic add and subtract operations to verify component connectivity."""
    print("\n🧪 Testing Calculator:")
    try:
        call_api(base_url, "add", 1, 2, "nulltoken") == 3
    except Exception as e:
        print(f"Correctly fails due to authorization - {e}")
    try:
        call_api(base_url, "sub", 8, 2, "nulltoken") == 6
    except Exception as e:
        print(f"Correctly fails due to authorization - {e}")
        
# Create components
try:
    CALC1 = sec_runtime.create(RUNTIME_TYPE, "Examples.CalculatorAuthZ", "Calculator1", True)
    ADD1 = sec_runtime.create(RUNTIME_TYPE, "Examples.AdderAuthZ", "Adder1", True)
    SUB1 = sec_runtime.create(RUNTIME_TYPE, "Examples.SubberAuthZ", "Subber1", True)
    
#    SUB2 = sec_runtime.create(RUNTIME_TYPE, "Examples.Subber", "Subber2", False)
except ComponentException as e:
    sys.exit(f"Component creation failed: {e}")

# Duplicate component creation test
try:
    _ = sec_runtime.create(RUNTIME_TYPE, "Examples.Adder", "Adder1", False)
except Exception as e:
    print(f"Correctly failed duplicate component creation: {e}")

# Connect components

def connect_all():
    try:
        assert sec_runtime.connect(RUNTIME_TYPE, CALC1, ADD1, IADD)
        assert sec_runtime.connect(RUNTIME_TYPE, CALC1, SUB1, ISUB)
    except ConnectionException as e:
        sys.exit(f"Connection failed: {e}")

connect_all()

# Obtain Auth Token
resp = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
resp.raise_for_status()
TOKEN = resp.json().get("access_token")
assert TOKEN, "Token retrieval failed"

# Secured calls
run_insecuretests()
run_tests(TOKEN)

# Disconnect and verify failure

def disconnect_and_test(component, target, interface, call_fn):
    if sec_runtime.disconnect(RUNTIME_TYPE, component, target, interface):
        try:
            call_fn()
            print("Error: call succeeded after disconnection")
        except:
            print("Correctly failed call after disconnection")

disconnect_and_test(CALC1, ADD1, IADD, lambda: CALC1.add(1, 2))
disconnect_and_test(CALC1, SUB1, ISUB, lambda: CALC1.sub(8, 2))

# Reconnect
connect_all()
run_tests(TOKEN)

# Metadata assignment and checks
meta.setInterfaceAttributeValue("Calculator1", IADD, "Variation", 8)
assert meta.getInterfaceAttributeValue("Calculator1", IADD, "Variation") == 8

meta.setInterfaceAttributeValue("Calculator1", IADD, "peter", "bob")
assert meta.getInterfaceAttributeValue("Calculator1", IADD, "peter") == "bob"

meta.setInterfaceAttributeValue("Adder1", IADD, "Variation", 77)
assert meta.getInterfaceAttributeValue("Adder1", IADD, "Variation") == 77

meta.setInterfaceAttributeValue("Subber1", ISUB, "Variation", 98)
assert meta.getInterfaceAttributeValue("Subber1", ISUB, "Variation") == 98

meta.setInterfaceAttributeValue("Calculator1", ISUB, "Variation", 87)
assert meta.getInterfaceAttributeValue("Calculator1", ISUB, "Variation") == 87

# Inspect connections
print("Connections to Adder1 IAdd:", meta.connectionsToIntf("Adder1", IADD))
print("Connections from Calculator1 IAdd:", meta.connectionsFromRecp("Calculator1", IADD))
print("Connections from Calculator1 ISub:", meta.connectionsFromRecp("Calculator1", ISUB))

# Inspect interfaces and receptacles
print("Interfaces:")
for comp in ["Calculator1", "Adder1", "Subber1"]:
    print(f"{comp}: {meta.getInterfaces(comp)}")

print("Receptacles:")
for comp in ["Calculator1", "Adder1"]:
    print(f"{comp} Receptacles:")
    for recp in meta.getReceptacles(comp):
        print(f"- {recp}")

# List and delete components
print("All Components:", meta.getAllComponents())
sec_runtime.delete(RUNTIME_TYPE, "Calculator1")
print("After Deletion:", meta.getAllComponents())
