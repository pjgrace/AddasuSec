"""Local integration checks for Addasu component lifecycle and wiring.

This script exercises component creation, connection management, metadata
updates, and basic introspection against the local runtime. It is written as an
executable test script rather than a `unittest` module because the surrounding
project appears to use direct runtime assertions for local validation.
"""

import sys
from pathlib import Path

# Resolve the repository's ``src`` directory so the script can be run directly
# from ``tests/LocalTests`` without first installing the project into the active
# Python environment.
PROJECT_SRC = Path(__file__).resolve().parents[2] / "src"
if str(PROJECT_SRC) not in sys.path:
    # Prepend the path so the local checkout takes precedence over any older
    # globally installed copy of the package.
    sys.path.insert(0, str(PROJECT_SRC))

from MetaArchitecture.MetaArchitecture import MetaArchitecture
from Runtimes.runtime import ComponentException, runtime

RUNTIME_TYPE = "plain"

# Stable component labels used throughout the test so that metadata and
# introspection queries can refer to the same identifiers after creation.
CALC1_NAME = "Calculator1"
CALC2_NAME = "Calculator2"
ADDER_NAME = "Adder1"
SUBBER_NAME = "Subber1"

# Interface identifiers expected by the example components.
IADD = "Examples.IAdd"
ISUB = "Examples.ISub"

# Concrete classes instantiated by the runtime during the lifecycle tests.
CALC_CLASS = "Examples.Calculator"
ADDER_CLASS = "Examples.Adder"
SUBBER_CLASS = "Examples.Subber"

# ``MetaArchitecture`` records the structural model, while ``runtime`` performs
# creation, connection, and deletion against that model.
meta = MetaArchitecture()
local_runtime = runtime(meta)


def create_component(component_class, label):
    """Create a component and stop the script with context if creation fails."""
    try:
        return local_runtime.create(RUNTIME_TYPE, component_class, label, False)
    except ComponentException as exc:
        # Component creation is a prerequisite for the remaining checks, so fail
        # fast with a useful message instead of letting later assertions cascade.
        sys.exit(f"Component creation failed for {label}: {exc}")


def expect_component_error(action, description):
    """Run an action that should fail with a component-level validation error."""
    try:
        action()
    except ComponentException as exc:
        # These failures are part of the expected behavior, so report them and
        # continue rather than treating them as test failures.
        print(f"Expected failure for {description}: {exc}")
        return
    raise AssertionError(f"Expected ComponentException for {description}")


def connect_all(calc1, calc2, add1, sub1):
    """Connect both calculators to the adder and subber services."""
    # Each assert confirms that the runtime accepted the requested wiring and
    # updated the internal model accordingly.
    assert local_runtime.connect(RUNTIME_TYPE, calc1, add1, IADD)
    assert local_runtime.connect(RUNTIME_TYPE, calc2, add1, IADD)
    assert local_runtime.connect(RUNTIME_TYPE, calc1, sub1, ISUB)
    assert local_runtime.connect(RUNTIME_TYPE, calc2, sub1, ISUB)
    print("All components successfully connected")


def assert_basic_operations(calc1, calc2):
    """Verify that both calculators can delegate add and subtract calls."""
    # The calculator components expose the public API; successful results here
    # prove that the connected adder and subber dependencies are reachable.
    assert calc1.add(1, 2) == 3
    assert calc2.add(1, 2) == 3
    assert calc1.sub(8, 2) == 6
    assert calc2.sub(8, 2) == 6
    print("Basic math operation tests passed")


def disconnect_and_assert_failures(calc1, calc2, add1, sub1):
    """Disconnect each dependency and ensure the delegated call no longer works."""
    # Pair each disconnection with the operation that should fail afterward.
    disconnections = [
        (calc1, add1, IADD, lambda component: component.add(1, 2)),
        (calc2, add1, IADD, lambda component: component.add(1, 2)),
        (calc1, sub1, ISUB, lambda component: component.sub(1, 2)),
        (calc2, sub1, ISUB, lambda component: component.sub(1, 2)),
    ]

    for component, target, interface, operation in disconnections:
        assert local_runtime.disconnect(RUNTIME_TYPE, component, target, interface)
        try:
            # Any exception is acceptable here: the key contract is that the
            # disconnected call must no longer succeed.
            operation(component)
        except Exception:
            continue
        raise AssertionError(
            f"Disconnected call unexpectedly succeeded for interface {interface}"
        )

    print("All disconnected calls failed as expected")


def assert_metadata_updates():
    """Verify interface attribute writes and reads across several components."""
    # These updates exercise metadata storage independently of the runtime calls
    # above. Each tuple is ``(component, interface, key, value)``.
    updates = [
        (CALC1_NAME, IADD, "Variation", 8),
        (CALC1_NAME, IADD, "peter", "bob"),
        (CALC2_NAME, IADD, "Variation", 77),
        (CALC1_NAME, ISUB, "Variation", 98),
        (CALC2_NAME, ISUB, "Variation", 87),
    ]

    for component_name, interface, key, value in updates:
        meta.setInterfaceAttributeValue(component_name, interface, key, value)
        # Read back immediately so the failing key is obvious if a write does not
        # persist correctly.
        assert meta.getInterfaceAttributeValue(component_name, interface, key) == value

    print("Metadata attribute tests passed")


def print_connection_summary():
    """Print connection information that is useful during manual debugging."""
    # These reports are intentionally left as prints because they are useful when
    # manually inspecting the current architecture after the assertions pass.
    print(f"\nConnections to {ADDER_NAME} {IADD}:")
    for name in meta.connectionsToIntf(ADDER_NAME, IADD):
        print(f" -> {name}")

    print(f"\nConnections from {CALC1_NAME} {IADD}:")
    for name in meta.connectionsFromRecp(CALC1_NAME, IADD):
        print(f" -> {name}")

    print(f"\nConnections from {CALC1_NAME} {ISUB}:")
    for name in meta.connectionsFromRecp(CALC1_NAME, ISUB):
        print(f" -> {name}")


def print_component_summary():
    """Print interfaces, receptacles, and the current component list."""
    print("\nInterfaces and Receptacles:")
    for component_name in [CALC1_NAME, CALC2_NAME, ADDER_NAME, SUBBER_NAME]:
        print(f"Interfaces on {component_name}: {meta.getInterfaces(component_name)}")

    print(f"Receptacles on {CALC1_NAME}: {meta.getReceptacles(CALC1_NAME)}")
    print(f"Receptacles on {ADDER_NAME}: {meta.getReceptacles(ADDER_NAME)}")

    print("\nAll Components:")
    all_components = meta.getAllComponents()
    print(all_components)
    # ``Calculator2`` is checked here so the final deletion test can prove that
    # the component list actually changes afterward.
    assert CALC2_NAME in all_components


def main():
    # Phase 1: create a small component graph that will be reused across all
    # later checks in this script.
    calc1 = create_component(CALC_CLASS, CALC1_NAME)
    calc2 = create_component(CALC_CLASS, CALC2_NAME)
    add1 = create_component(ADDER_CLASS, ADDER_NAME)

    # Delete and recreate one component to prove the runtime cleans up correctly
    # and allows the same logical label to be used again.
    assert local_runtime.delete(RUNTIME_TYPE, ADDER_NAME)
    add1 = create_component(ADDER_CLASS, ADDER_NAME)

    sub1 = create_component(SUBBER_CLASS, SUBBER_NAME)

    # Phase 2: validate common failure cases that the runtime should reject.
    assert not local_runtime.delete(RUNTIME_TYPE, "Adder5")
    expect_component_error(
        lambda: local_runtime.create(RUNTIME_TYPE, ADDER_CLASS, ADDER_NAME, False),
        "duplicate component creation",
    )
    expect_component_error(
        lambda: local_runtime.create(RUNTIME_TYPE, ADDER_CLASS, "Adder 1", False),
        "invalid component name",
    )

    # Phase 3: connect the graph and prove that delegated operations work.
    connect_all(calc1, calc2, add1, sub1)
    assert_basic_operations(calc1, calc2)

    # Phase 4: remove each dependency and confirm that calls fail once the graph
    # has been torn down.
    disconnect_and_assert_failures(calc1, calc2, add1, sub1)

    # Phase 5: reconnect the graph to confirm the runtime can recover cleanly
    # after disconnection.
    connect_all(calc1, calc2, add1, sub1)
    assert_basic_operations(calc1, calc2)

    # Phase 6: exercise metadata and reporting APIs after the structural tests.
    assert_metadata_updates()
    print_connection_summary()
    print_component_summary()

    # Phase 7: remove a component and verify that the architecture view updates.
    assert local_runtime.delete(RUNTIME_TYPE, CALC2_NAME)
    all_components = meta.getAllComponents()
    assert CALC2_NAME not in all_components
    print(f"{CALC2_NAME} successfully deleted.")


if __name__ == "__main__":
    # Keep the script executable as a direct entrypoint for local manual testing.
    main()
