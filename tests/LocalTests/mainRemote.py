"""Remote integration checks for Addasu components.

This script drives a remote runtime endpoint, creates a small component graph,
connects and disconnects it, triggers execution through the start component,
and prints metadata and introspection state for manual inspection.
"""

import sys
from pathlib import Path

# Allow the script to be executed directly from ``tests/LocalTests`` while still
# importing packages from the repository's ``src`` layout.
PROJECT_SRC = Path(__file__).resolve().parents[2] / "src"
if str(PROJECT_SRC) not in sys.path:
    # Prefer the checked-out source tree over any globally installed version.
    sys.path.insert(0, str(PROJECT_SRC))

from MetaArchitecture.MetaArchitecture import MetaArchitecture
from Runtimes.runtime import ComponentException, ConnectionException, runtime

# Base URL for the remote runtime process that hosts the components.
REMOTE_RUNTIME = "http://localhost:8654"
RUNTIME_TYPE = "plain"

# Stable labels used for creation, metadata queries, and connection reports.
CALC1 = "Calculator1"
CALC2 = "Calculator2"
ADDER = "Adder1"
SUBBER = "Subber1"
START = "Start1"

# Interfaces used by the example components.
ICALCULATE = "Examples.ICalculate"
IADD = "Examples.IAdd"
ISUB = "Examples.ISub"

# ``MetaArchitecture`` tracks the architecture model locally while the runtime
# proxy issues create/connect/start requests to the remote address space.
meta = MetaArchitecture()
remote_runtime = runtime(meta)


def safe_create(label, module):
    """Create a remote component and report the result."""
    try:
        component = remote_runtime.remoteCreate(
            REMOTE_RUNTIME, RUNTIME_TYPE, module, label, False
        )
        print(f"Created {label} ({module}) -> ID: {meta.getLabel(component)}")
        return component
    except ComponentException as exc:
        # Duplicate names and invalid definitions are expected in some checks, so
        # report them and let the script continue.
        print(f"Failed to create {label} ({module}): {exc}")
        return None


def safe_connect(source_id, target_id, interface):
    """Connect two remote components and print the outcome."""
    try:
        if remote_runtime.remoteConnect(
            REMOTE_RUNTIME, RUNTIME_TYPE, source_id, target_id, interface
        ):
            print(
                f"Connected {meta.getLabel(source_id)} -> "
                f"{meta.getLabel(target_id)} ({interface})"
            )
    except ConnectionException as exc:
        print(f"Failed to connect {source_id} -> {target_id}: {exc}")


def safe_disconnect(source_id, target_id, interface):
    """Disconnect two remote components and print the outcome."""
    try:
        if remote_runtime.remoteDisconnect(
            REMOTE_RUNTIME, RUNTIME_TYPE, source_id, target_id, interface
        ):
            print(
                f"Disconnected {meta.getLabel(source_id)} -> "
                f"{meta.getLabel(target_id)} ({interface})"
            )
    except ConnectionException as exc:
        print(f"Failed to disconnect {source_id} -> {target_id}: {exc}")


def print_connections(title, connections):
    """Render connection lists in a readable format for manual inspection."""
    print(f"\n{title}")
    for connection in connections:
        print(f" -> {connection}")


def connect_application(start1, calc1, calc2, add1, sub1):
    """Wire the start component to the calculator graph and service providers."""
    safe_connect(start1, calc1, ICALCULATE)
    safe_connect(calc1, add1, IADD)
    safe_connect(calc2, add1, IADD)
    safe_connect(calc1, sub1, ISUB)
    safe_connect(calc2, sub1, ISUB)


def disconnect_application(calc1, calc2, add1, sub1):
    """Remove the calculator-to-service bindings one by one."""
    for component, target, interface in [
        (calc1, add1, IADD),
        (calc2, add1, IADD),
        (calc1, sub1, ISUB),
        (calc2, sub1, ISUB),
    ]:
        safe_disconnect(component, target, interface)


def main():
    # Phase 1: create the remote components needed for the runtime scenario.
    print("\nCreating components")
    start1 = safe_create(START, "Examples.CalculatorStart")
    calc1 = safe_create(CALC1, "Examples.Calculator")
    calc2 = safe_create(CALC2, "Examples.Calculator")
    add1 = safe_create(ADDER, "Examples.Adder")
    sub1 = safe_create(SUBBER, "Examples.Subber")

    # Intentionally repeat one label to confirm the remote runtime rejects
    # duplicate component creation requests.
    print("\nDuplicate component creation test")
    safe_create(ADDER, "Examples.Adder")

    # Phase 2: connect the graph and trigger execution through the start
    # component so the remote runtime exercises the assembled configuration.
    print("\nConnecting components")
    connect_application(start1, calc1, calc2, add1, sub1)
    remote_runtime.remoteStart(REMOTE_RUNTIME, RUNTIME_TYPE, start1)

    # Phase 3: disconnect each dependency and start the configuration after each
    # change so the effect of the missing binding can be observed remotely.
    print("\nDisconnecting components")
    for component, target, interface in [
        (calc1, add1, IADD),
        (calc2, add1, IADD),
        (calc1, sub1, ISUB),
        (calc2, sub1, ISUB),
    ]:
        safe_disconnect(component, target, interface)
        remote_runtime.remoteStart(REMOTE_RUNTIME, RUNTIME_TYPE, start1)

    # Phase 4: rebuild the graph and run it again to confirm the configuration
    # can recover after the disconnect sequence.
    print("\nReconnecting components")
    connect_application(start1, calc1, calc2, add1, sub1)
    remote_runtime.remoteStart(REMOTE_RUNTIME, RUNTIME_TYPE, start1)

    # Phase 5: verify metadata read/write behavior using one of the interfaces.
    print("\nMetadata attribute test")
    meta.setInterfaceAttributeValue(CALC1, IADD, "Variation", 8)
    variation_value = meta.getInterfaceAttributeValue(CALC1, IADD, "Variation")
    print(f"{CALC1}.{IADD}.Variation = {variation_value}")

    # Phase 6: print the current architectural model for manual debugging.
    print_connections(f"Connections TO {ADDER}.{IADD}", meta.connectionsToIntf(ADDER, IADD))
    print_connections(
        f"Connections FROM {CALC1}.{IADD}", meta.connectionsFromRecp(CALC1, IADD)
    )
    print_connections(
        f"Connections FROM {CALC1}.{ISUB}", meta.connectionsFromRecp(CALC1, ISUB)
    )

    print("\nInterface inspection")
    for component_name in [CALC1, CALC2, ADDER, SUBBER]:
        print(f"Interfaces on {component_name}: {meta.getInterfaces(component_name)}")

    print("\nReceptacle inspection")
    for component_name in [CALC2, ADDER, SUBBER]:
        print(f"Receptacles on {component_name}: {meta.getReceptacles(component_name)}")

    # Phase 7: show the complete component list before and after deleting one
    # component so the remote runtime cleanup is visible in the meta-model.
    print("\nAll components before deletion")
    all_components_before = meta.getAllComponents()
    print(all_components_before)

    print(f"\nDeleting {CALC2}")
    remote_runtime.delete(RUNTIME_TYPE, CALC2)

    print("\nAll components after deletion")
    all_components_after = meta.getAllComponents()
    print(all_components_after)


if __name__ == "__main__":
    main()
