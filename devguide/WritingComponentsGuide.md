# 🧩 AddasuSec Developer Guide: Writing a Component

This guide provides a complete walkthrough for creating components in the **AddasuSec** framework. Components in AddasuSec are plug-and-play modules that communicate via typed interfaces and dynamic runtime bindings. This design enables adaptive, secure architectures that can respond to changes during execution.

---

## 📌 Prerequisites

Before starting, ensure you have:

- Python 3.9+
- AddasuSec repository cloned
- Familiarity with Python classes and type annotations
- `AddasuSec.Component` available in your Python path

---

## 🧠 Key Principle: Type Annotations Are Mandatory

**All component methods must use Python type annotations for both parameters and return values.**

Incorrect:
```python
def add(a, b):  # ❌ Missing types
    ...
```

Correct:
```python
def add(a: int, b: int) -> int:  # ✅ Types required
    ...
```

---

## 🧱 Step 1: Define an Interface

Interfaces define the operations a component must implement. Use Python's `abc` module.

**Example: `ICalculate.py`**

```python
from abc import ABC, abstractmethod

class ICalculate(ABC):

    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def sub(self, a: int, b: int) -> int:
        pass
```

✅ **Use `@abstractmethod`** to enforce implementation  
✅ **Always annotate parameters and return types**

---

## ⚙️ Step 2: Implement the Component

Components extend both the interface and the AddasuSec `Component` base class.

**Example: `Calculator.py`**

```python
from AddasuSec.Component import Component
from Examples.ICalculate import ICalculate

class Calculator(Component, ICalculate):

    receptacle1_type = "Examples.IAdd"
    receptacle2_type = "Examples.ISub"

    def __init__(self, name):
        super().__init__({self.receptacle1_type, self.receptacle2_type})

    def add(self, a: int, b: int) -> int:
        adder = self.getReceptacle(self.receptacle1_type)
        return adder.add(a, b)

    def sub(self, a: int, b: int) -> int:
        subber = self.getReceptacle(self.receptacle2_type)
        return subber.sub(a, b)
```

### 🔍 Key Points

- Receptacles are outbound interface dependencies.
- `getReceptacle()` connects to other components implementing a matching interface.
- You must **match method names and signatures** exactly as defined in your interface.

---

## 🔗 Step 3: Runtime Integration

Here’s how to create and use the component in a running system:

```python
from Runtimes.runtime import runtime
from MetaArchitecture.MetaArchitecture import MetaArchitecture

meta = MetaArchitecture()
env = runtime(meta)

calc = env.create("plain", "Examples.Calculator", "Calc1", False)
```

Assuming proper connections to `IAdd` and `ISub`, you can call:

```python
print(calc.add(2, 3))  # Will invoke connected Adder's add()
print(calc.sub(10, 4)) # Will invoke connected Subber's sub()
```

---

## 🛡️ Step 4: Metadata & Inspection

AddasuSec supports rich introspection via its meta-architecture engine:

```python
meta.setInterfaceAttributeValue("Calc1", "Examples.IAdd", "version", 1.0)
val = meta.getInterfaceAttributeValue("Calc1", "Examples.IAdd", "version")
print(val)  # 1.0
```

You can also list:

- Interfaces: `meta.getInterfaces("Calc1")`
- Receptacles: `meta.getReceptacles("Calc1")`
- Connections: `meta.connectionsFromRecp("Calc1", "Examples.IAdd")`

---

## ✅ Step 5: Validation and Cleanup

Always validate component behavior and clean up at the end:

```python
env.disconnect("plain", calc, adder, "Examples.IAdd")
env.delete("plain", "Calc1")
```

---

## 📋 Component Checklist

| Feature | Required | Example |
|--------|----------|---------|
| Inherit from `Component` | ✅ | `class MyComp(Component)` |
| Implement interface | ✅ | `class MyComp(MyInterface)` |
| Annotate method parameters | ✅ | `def add(a: int, b: int)` |
| Annotate return types | ✅ | `-> int` |
| Define receptacle strings | ✅ | `"Examples.IAdd"` |
| Use `super().__init__()` with receptacles | ✅ | `{ "IAdd", "ISub" }` |
| Use `getReceptacle()` | ✅ | To access other components |
| Use `MetaArchitecture` to tag interfaces | Optional | `setInterfaceAttributeValue(...)` |

---

## 🧪 Bonus: Testing Your Component

Try the full lifecycle in `tests/main.py`:

- Create components
- Connect interfaces
- Verify math functions
- Test disconnection failures
- Explore metadata

Run tests using:

```bash
pytest -v
```

---

## 📦 Conclusion

The AddasuSec framework enables secure, adaptive component systems. Following interface-driven design with strict type annotations ensures your components are compatible with the runtime engine.

> 🧠 Want more? Extend this with logging, dynamic switching, or trust-policy tagging.

---
