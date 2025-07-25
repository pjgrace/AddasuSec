"""
RemoteComponentManager.py

Remotely creates, connects, and inspects Addasu components using secure runtime.

Author: Paul Grace
"""

from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
from MetaArchitecture.MetaArchitecture import MetaArchitecture

import os
import sys

# === Constants ===
REMOTE_RUNTIME = "http://localhost:8654"

CALC1 = "Calculator1"
CALC2 = "Calculator2"
ADDER = "Adder1"
SUBBER = "Subber1"
START = "Start1"

IADD = "Examples.IAdd"
ISUB = "Examples.ISub"

# === Initialise Runtime and MetaArchitecture ===
meta = MetaArchitecture()
secure_runtime = runtime(meta)

# === Helper Functions ===

def safe_create(label, module):
    try:
        comp = secure_runtime.remoteCreate(REMOTE_RUNTIME, "plain", module, label, False)
        print(f"✅ Created {label} ({module}) → ID: {meta.getLabel(comp)}")
        return comp
    except ComponentException as e:
        print(f"⚠️  Failed to create {label} ({module}): {e}")
        return None

def safe_connect(src_id, tgt_id, intf):
    try:
        if secure_runtime.remoteConnect(REMOTE_RUNTIME, "plain", src_id, tgt_id, intf):
            print(f"🔗 Connected {meta.getLabel(src_id)} → {meta.getLabel(tgt_id)} ({intf})")
    except ConnectionException as e:
        print(f"❌ Failed to connect {src_id} → {tgt_id}: {e}")
        
def safe_disconnect(src_id, tgt_id, intf):
    try:
        if secure_runtime.remoteDisconnect(REMOTE_RUNTIME, "plain", src_id, tgt_id, intf):
            print(f"🔗 Disconnected {meta.getLabel(src_id)} → {meta.getLabel(tgt_id)} ({intf})")
    except ConnectionException as e:
        print(f"❌ Failed to connect {src_id} → {tgt_id}: {e}")

def print_connections(title, conn_list):
    print(f"\n🔍 {title}")
    for c in conn_list:
        print(f" ↳ {c}")

# === Component Creation ===

print("\n=== 🚀 Creating Components ===")
start1 = safe_create(START, "Examples.CalculatorStart")
calc1 = safe_create(CALC1, "Examples.Calculator")
calc2 = safe_create(CALC2, "Examples.Calculator")
add1 = safe_create(ADDER, "Examples.Adder")
sub1 = safe_create(SUBBER, "Examples.Subber")

# Intentional duplicate (should fail)
print("\n=== ⚠️ Duplicate Component Creation Test ===")
safe_create(ADDER, "Examples.Adder")

# === Component Connections ===

print("\n=== 🔗 Connecting Components ===")
safe_connect(start1, calc1, "Examples.ICalculate")
safe_connect(calc1, add1, IADD)
safe_connect(calc2, add1, IADD)
safe_connect(calc1, sub1, ISUB)
safe_connect(calc2, sub1, ISUB)

# === Test component configuration runs ===
secure_runtime.remoteStart(REMOTE_RUNTIME, "plain", start1)

# === Test disconnects ===


for c, t, iface in [
        (calc1, add1, IADD),
        (calc2, add1, IADD),
        (calc1, sub1, ISUB),
        (calc2, sub1, ISUB),
    ]:
    safe_disconnect(c, t, iface)
    secure_runtime.remoteStart(REMOTE_RUNTIME, "plain", start1)

# === Call start to see if the configuration runs ===
print("\n=== 🔗 Connecting Components Again===")
safe_connect(calc1, add1, IADD)
safe_connect(calc2, add1, IADD)
safe_connect(calc1, sub1, ISUB)
safe_connect(calc2, sub1, ISUB)
secure_runtime.remoteStart(REMOTE_RUNTIME, "plain", start1)


print("\n=== 🧪 Metadata Attribute Test ===")
meta.setInterfaceAttributeValue(CALC1, IADD, "Variation", 8)
variation_val = meta.getInterfaceAttributeValue(CALC1, IADD, "Variation")
print(f"📌 {CALC1}.{IADD}.Variation = {variation_val}")

# === Inspection & Debugging ===

print_connections(f"Connections TO {ADDER}.{IADD}", meta.connectionsToIntf(ADDER, IADD))
print_connections(f"Connections FROM {CALC1}.{IADD}", meta.connectionsFromRecp(CALC1, IADD))
print_connections(f"Connections FROM {CALC1}.{ISUB}", meta.connectionsFromRecp(CALC1, ISUB))

# === Interface & Receptacle Introspection ===

print("\n=== 🧠 Interface Inspection ===")
for comp in [CALC1, CALC2, ADDER, SUBBER]:
    print(f"Interfaces on {comp}: {meta.getInterfaces(comp)}")

print("\n=== 🧠 Receptacle Inspection ===")
for comp in [CALC2, ADDER, SUBBER]:
    print(f"Receptacles on {comp}: {meta.getReceptacles(comp)}")

# === Component Listing & Deletion ===

print("\n=== 📋 All Components (Before Deletion) ===")
all_comps_before = meta.getAllComponents()
print(all_comps_before)

print(f"\n🗑️ Deleting {CALC2}")
secure_runtime.delete("plain", CALC2)

print("\n📋 All Components (After Deletion):")
all_comps_after = meta.getAllComponents()
print(all_comps_after)


