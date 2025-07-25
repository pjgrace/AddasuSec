"""
Component Lifecycle and Connection Testing Script
--------------------------------------------------

This script validates the creation, deletion, connection, and disconnection of components
within a dynamic component framework (Addasu). It also tests metadata manipulation,
interface listing, and connection queries using `MetaArchitecture`.

Features:
- Component instantiation and deletion
- Interface connection/disconnection
- Metadata tagging and retrieval
- Structural verification using assertions (test-like style)
- Runtime and metadata logging

Intended for internal test and debug use.

Dependencies:
- AddasuSec.Receptacle
- Runtimes.runtime
- MetaArchitecture.MetaArchitecture

Author: Paul Grace

"""

from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
from MetaArchitecture.MetaArchitecture import MetaArchitecture
import sys

# === Constants ===

PLAIN = "plain"

# Component names
CALC1_NAME = "Calculator1"
CALC2_NAME = "Calculator2"
ADDER_NAME = "Adder1"
SUBBER_NAME = "Subber1"

# Interfaces
IADD = "Examples.IAdd"
ISUB = "Examples.ISub"

# Classes
CALC_CLASS = "Examples.Calculator"
ADDER_CLASS = "Examples.Adder"
SUBBER_CLASS = "Examples.Subber"

# === Initialize runtime and metadata ===

addasuMeta = MetaArchitecture()
addasuSec = runtime(addasuMeta)

# === Function Definitions ===

def run_tests():
    """Perform basic add and subtract operations to verify component connectivity."""
    assert calc1.add(1, 2) == 3
    assert calc2.add(1, 2) == 3
    assert calc1.sub(8, 2) == 6
    assert calc2.sub(8, 2) == 6
    print("Basic math operation tests passed")

def full_connection():
    """Connect calculators to the adder and subber components via required interfaces."""
    assert addasuSec.connect(PLAIN, calc1, add1, IADD)
    assert addasuSec.connect(PLAIN, calc2, add1, IADD)
    assert addasuSec.connect(PLAIN, calc1, sub1, ISUB)
    assert addasuSec.connect(PLAIN, calc2, sub1, ISUB)
    print("All components successfully connected")

# === Component Lifecycle Tests ===

try:
    calc1 = addasuSec.create(PLAIN, CALC_CLASS, CALC1_NAME, False)
    calc2 = addasuSec.create(PLAIN, CALC_CLASS, CALC2_NAME, False)
    add1 = addasuSec.create(PLAIN, ADDER_CLASS, ADDER_NAME, False)

    # Test delete + recreate
    assert addasuSec.delete(PLAIN, ADDER_NAME)
    add1 = addasuSec.create(PLAIN, ADDER_CLASS, ADDER_NAME, False)

    sub1 = addasuSec.create(PLAIN, SUBBER_CLASS, SUBBER_NAME, False)

except ComponentException as e:
    sys.exit(f"Component creation failed: {e}")

# === Invalid Creation and Deletion Tests ===

try:
    assert not addasuSec.delete(PLAIN, "Adder5")
except ComponentException as e:
    print(f"Expected error deleting non-existent component: {e}")

try:
    addasuSec.create(PLAIN, ADDER_CLASS, ADDER_NAME, False)
except ComponentException as e:
    print(f"Expected error on duplicate component creation: {e}")

try:
    addasuSec.create(PLAIN, ADDER_CLASS, "Adder 1", False)
except ComponentException as e:
    print(f"Expected error on invalid component name: {e}")

# === Connection and Functionality Tests ===

full_connection()
run_tests()

# === Disconnect and Negative Call Tests ===

def test_disconnect_and_failures():
    """Disconnect components and ensure calls fail."""
    for c, t, iface in [
        (calc1, add1, IADD),
        (calc2, add1, IADD),
        (calc1, sub1, ISUB),
        (calc2, sub1, ISUB),
    ]:
        assert addasuSec.disconnect(PLAIN, c, t, iface)
        try:
            # These calls should raise exceptions since disconnected
            if iface == IADD:
                c.add(1, 2)
            else:
                c.sub(1, 2)
            assert False, "Disconnected call should not succeed"
        except Exception:
            pass

    print("All disconnected calls failed as expected")

test_disconnect_and_failures()

# Reconnect for further testing
full_connection()
run_tests()

# === Metadata Tests ===

addasuMeta.setInterfaceAttributeValue(CALC1_NAME, IADD, "Variation", 8)
assert addasuMeta.getInterfaceAttributeValue(CALC1_NAME, IADD, "Variation") == 8

addasuMeta.setInterfaceAttributeValue(CALC1_NAME, IADD, "peter", "bob")
assert addasuMeta.getInterfaceAttributeValue(CALC1_NAME, IADD, "peter") == "bob"

addasuMeta.setInterfaceAttributeValue(CALC2_NAME, IADD, "Variation", 77)
assert addasuMeta.getInterfaceAttributeValue(CALC2_NAME, IADD, "Variation") == 77

addasuMeta.setInterfaceAttributeValue(CALC1_NAME, ISUB, "Variation", 98)
assert addasuMeta.getInterfaceAttributeValue(CALC1_NAME, ISUB, "Variation") == 98

addasuMeta.setInterfaceAttributeValue(CALC2_NAME, ISUB, "Variation", 87)
assert addasuMeta.getInterfaceAttributeValue(CALC2_NAME, ISUB, "Variation") == 87

print("Metadata attribute tests passed")

# === Interface & Connection Inspection ===

print("\nConnections to Adder1 IAdd:")
for name in addasuMeta.connectionsToIntf(ADDER_NAME, IADD):
    print(f"↳ {name}")

print("\nConnections from Calculator1 IAdd:")
for name in addasuMeta.connectionsFromRecp(CALC1_NAME, IADD):
    print(f"↳ {name}")

print("\nConnections from Calculator1 ISub:")
for name in addasuMeta.connectionsFromRecp(CALC1_NAME, ISUB):
    print(f"↳ {name}")

# === Introspection ===

print("\nInterfaces and Receptacles:")
for comp in [CALC1_NAME, CALC2_NAME, ADDER_NAME, SUBBER_NAME]:
    print(f"Interfaces on {comp}: {addasuMeta.getInterfaces(comp)}")

print(f"Receptacles on {CALC1_NAME}: {addasuMeta.getReceptacles(CALC1_NAME)}")
print(f"Receptacles on {ADDER_NAME}: {addasuMeta.getReceptacles(ADDER_NAME)}")

# === List All Components ===

print("\nAll Components:")
all_comps = addasuMeta.getAllComponents()
print(all_comps)
assert CALC2_NAME in all_comps

# === Final Deletion ===

assert addasuSec.delete(PLAIN, CALC2_NAME)
all_comps = addasuMeta.getAllComponents()
assert CALC2_NAME not in all_comps
print(f"{CALC2_NAME} successfully deleted.")
