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

import requests
import sys
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[2] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
from MetaArchitecture.MetaArchitecture import MetaArchitecture

# Constants for reuse
RUNTIME_TYPE = "plain"
IADD = "Examples.IAdd"
ISUB = "Examples.ISub"
AUTH_URL = "http://localhost:8676/token"
USERNAME = "alice"
PASSWORD = "password123"

# Initialise runtime and meta
meta = MetaArchitecture()
sec_runtime = runtime(meta)

# Create components
try:
    CALC1 = sec_runtime.create(RUNTIME_TYPE, "Examples.CalculatorAuthZ", "Calculator1", True)
    CALC2 = sec_runtime.create(RUNTIME_TYPE, "Examples.Calculator", "Calculator2", False)
    ADD1 = sec_runtime.create(RUNTIME_TYPE, "Examples.AdderAuthZ", "Adder1", True)
    ADD2 = sec_runtime.create(RUNTIME_TYPE, "Examples.Adder", "Adder2", False)
    SUB1 = sec_runtime.create(RUNTIME_TYPE, "Examples.SubberAuthZ", "Subber1", True)
    SUB2 = sec_runtime.create(RUNTIME_TYPE, "Examples.Subber", "Subber2", False)
except ComponentException as e:
    sys.exit(f"Component creation failed: {e}")

# Duplicate component creation test
try:
    _ = sec_runtime.create(RUNTIME_TYPE, "Examples.Adder", "Adder1", False)
except ComponentException as e:
    print(f"Correctly failed duplicate component creation: {e}")

# Connect components

def connect_all():
    try:
        assert sec_runtime.connect(RUNTIME_TYPE, CALC1, ADD1, IADD)
        assert sec_runtime.connect(RUNTIME_TYPE, CALC2, ADD2, IADD)
        assert sec_runtime.connect(RUNTIME_TYPE, CALC1, SUB1, ISUB)
        assert sec_runtime.connect(RUNTIME_TYPE, CALC2, SUB2, ISUB)
    except ConnectionException as e:
        sys.exit(f"Connection failed: {e}")

connect_all()

# Obtain Auth Token
resp = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
resp.raise_for_status()
TOKEN = resp.json().get("access_token")
assert TOKEN, "Token retrieval failed"

# Secured calls
assert CALC1.call_with_token(CALC1.add, TOKEN, 1, 2) == 3
assert CALC1.call_with_token(CALC1.sub, TOKEN, 8, 1) == 7

# Unauthenticated calls
assert CALC2.add(1, 2) == 3
assert CALC2.sub(8, 2) == 6

# Disconnect and verify failure

def disconnect_and_test(component, target, interface, call_fn):
    if sec_runtime.disconnect(RUNTIME_TYPE, component, target, interface):
        try:
            call_fn()
            print("Error: call succeeded after disconnection")
        except:
            print("Correctly failed call after disconnection")

disconnect_and_test(CALC1, ADD1, IADD, lambda: CALC1.add(1, 2))
disconnect_and_test(CALC2, ADD2, IADD, lambda: CALC2.add(1, 2))
disconnect_and_test(CALC1, SUB1, ISUB, lambda: CALC1.sub(8, 2))
disconnect_and_test(CALC2, SUB2, ISUB, lambda: CALC2.sub(1, 2))

# Reconnect
connect_all()
assert CALC2.add(2, 3) == 5

# Metadata assignment and checks
meta.setInterfaceAttributeValue("Calculator1", IADD, "Variation", 8)
assert meta.getInterfaceAttributeValue("Calculator1", IADD, "Variation") == 8

meta.setInterfaceAttributeValue("Calculator2", IADD, "peter", "bob")
assert meta.getInterfaceAttributeValue("Calculator2", IADD, "peter") == "bob"

meta.setInterfaceAttributeValue("Adder1", IADD, "Variation", 77)
assert meta.getInterfaceAttributeValue("Adder1", IADD, "Variation") == 77

meta.setInterfaceAttributeValue("Subber1", ISUB, "Variation", 98)
assert meta.getInterfaceAttributeValue("Subber1", ISUB, "Variation") == 98

meta.setInterfaceAttributeValue("Calculator2", ISUB, "Variation", 87)
assert meta.getInterfaceAttributeValue("Calculator2", ISUB, "Variation") == 87

# Inspect connections
print("Connections to Adder1 IAdd:", meta.connectionsToIntf("Adder1", IADD))
print("Connections from Calculator1 IAdd:", meta.connectionsFromRecp("Calculator1", IADD))
print("Connections from Calculator1 ISub:", meta.connectionsFromRecp("Calculator1", ISUB))

# Inspect interfaces and receptacles
print("Interfaces:")
for comp in ["Calculator1", "Calculator2", "Adder1", "Subber1"]:
    print(f"{comp}: {meta.getInterfaces(comp)}")

print("Receptacles:")
for comp in ["Calculator1", "Adder1"]:
    print(f"{comp} Receptacles:")
    for recp in meta.getReceptacles(comp):
        print(f"- {recp}")

# List and delete components
print("All Components:", meta.getAllComponents())
sec_runtime.delete(RUNTIME_TYPE, "Calculator2")
print("After Deletion:", meta.getAllComponents())
