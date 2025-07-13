# AddasuSec 🔐

**An adaptive component framework for secure, model-driven runtime architecture.**

AddasuSec enables dynamic management of software components using trust boundaries, access control models, and runtime architectural introspection. It's designed for systems that need to adapt and secure themselves during execution based on runtime threat modeling and metadata inspection.

---

## 🚀 Features

- **Component Lifecycle Management** – Create, delete, connect, and disconnect components dynamically.
- **Meta-Model Support** – Architecture, access control, and dataflow meta-models to manage runtime behavior.
- **Interface-Level Control** – Inspect and modify interface metadata; track receptacles and connections.
- **Security & Adaptability** – Adapt trust boundaries and component logic based on runtime states.

---

## 📁 Project Structure

```
AddasuSec/
├── src/               # Core framework modules
├── tests/             # Functional and metadata test scripts
├── README.md          # This file
├── LICENSE            # MIT License
└── .gitignore         # Exclusion list
```

---

## 🧪 Usage Example

Here’s a sample script that mirrors `tests/main.py`. It shows how to instantiate, connect, use, tag, and remove components at runtime.

```python
from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime
from MetaArchitecture.MetaArchitecture import MetaArchitecture

# Setup runtime and meta-model
meta = MetaArchitecture()
runtime_env = runtime(meta)

# Create components
calc1 = runtime_env.create("plain", "Examples.Calculator", "Calculator1", False)
adder = runtime_env.create("plain", "Examples.Adder", "Adder1", False)

# Connect interface
runtime_env.connect("plain", calc1, adder, "Examples.IAdd")

# Perform operation
result = calc1.add(5, 3)
print(f"5 + 3 = {result}")

# Set and get metadata
meta.setInterfaceAttributeValue("Calculator1", "Examples.IAdd", "Version", 1.0)
assert meta.getInterfaceAttributeValue("Calculator1", "Examples.IAdd", "Version") == 1.0

# Cleanup
runtime_env.disconnect("plain", calc1, adder, "Examples.IAdd")
runtime_env.delete("plain", "Calculator1")
```

> 💡 Full example with validation and introspection: [`tests/main.py`](https://github.com/pjgrace/AddasuSec/blob/main/tests/main.py)

---

## ✅ Running Tests

Use `pytest` to run all validation and regression tests:

```bash
pytest -v
```

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Feel free to fork, open issues, and submit pull requests. Suggested flow:

1. Fork the repo  
2. Create a branch (`feature/your-feature`)  
3. Code and test your feature  
4. Submit a pull request  

---

## 🧠 Why Use AddasuSec?

- Reconfigure software at runtime securely  
- Manage component trust boundaries  
- Model and audit interactions via metadata  
- Simplify adaptive security architectures in dynamic environments  
