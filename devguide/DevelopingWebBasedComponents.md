# 🌐 AddasuSec Developer Guide: Writing and Wiring Web Components

This guide walks through creating, running, and connecting web components using the **secure API server** in AddasuSec, then validating the setup using the scripts in `tests/WebServerTests`.

It is based on the current runtime/server code and test flows in this repository.

---

## What this guide covers

You will learn how to:

1. Start the secure remote orchestration server (`src/API/SecureWebAPIServer.py`).
2. Build a web-based component graph (Calculator + Adder + Subber + Start component).
3. Connect/disconnect components through the remote runtime API.
4. Validate behavior using `tests/WebServerTests/mainWebServerRemote.py` and `tests/WebServerTests/mainWebServerSecure.py`.

---

## Prerequisites

- Python 3.9+
- Repository cloned locally
- `PYTHONPATH` set so `src/` is importable
- Required Python dependencies installed (for example: `falcon`, `PyJWT`, `requests`)

From repository root:

```bash
export PYTHONPATH="$PWD/src"
```

---

## 1) Start the secure web API server

The secure server exposes the orchestration endpoints:

- `POST /create`
- `POST /delete`
- `POST /connect`
- `POST /disconnect`
- `POST /start`

Default bind/port: `0.0.0.0:8654`.

Run it from repo root:

```bash
export PYTHONPATH="$PWD/src"
python src/API/SecureWebAPIServer.py
```

Expected startup output:

```text
Starting API server on 0.0.0.0:8654...
Serving on http://0.0.0.0:8654
```

> The secure server includes JWT-aware logging middleware. If a bearer token is provided in `Authorization`, user/roles are decoded and included in request logs.

---

## 2) Component topology used by WebServerTests

The web-server tests build this topology:

- `Start1` (`Examples.CalculatorStart`, runtime type `web`)
- `Calculator1` (`Examples.Calculator`, runtime type `web_server`)
- `Calculator2` (`Examples.Calculator`, runtime type `web_server`)
- `Adder1` (`Examples.Adder`, runtime type `plain`)
- `Subber1` (`Examples.Subber`, runtime type `plain`)

Primary interface wiring:

- `Start1` → `Calculator1` via `Examples.ICalculate`
- `Calculator1` → `Adder1` via `Examples.IAdd`
- `Calculator2` → `Adder1` via `Examples.IAdd`
- `Calculator1` → `Subber1` via `Examples.ISub`
- `Calculator2` → `Subber1` via `Examples.ISub`

The remote test script that exercises this graph is:

```bash
python tests/WebServerTests/mainWebServerRemote.py
```

---

## 3) End-to-end run sequence (recommended)

Open two terminals.

### Terminal A: Start orchestration API

```bash
export PYTHONPATH="$PWD/src"
python src/API/SecureWebAPIServer.py
```

### Terminal B: Build, connect, and run remote graph

```bash
export PYTHONPATH="$PWD/src"
python tests/WebServerTests/mainWebServerRemote.py
```

What this script does:

1. Creates components remotely using `runtime.remoteCreate(...)`.
2. Tests duplicate creation failure (intentional).
3. Connects components remotely using `runtime.remoteConnect(...)`.
4. Starts the graph with `runtime.remoteStart(...)`.
5. Disconnects/reconnects interfaces and starts again.
6. Performs metadata checks and prints graph introspection.

---

## 4) Secure invocation flow

For authenticated web component calls, use:

```bash
export PYTHONPATH="$PWD/src"
python tests/WebServerTests/mainWebServerSecure.py
```

This script:

- Creates secure variants (`CalculatorAuthZ`, `AdderAuthZ`, `SubberAuthZ`).
- Connects them through runtime type `web_server`.
- Fetches a bearer token from `http://localhost:8676/token`.
- Verifies unauthorized requests fail and authorized requests succeed.
- Performs metadata, connection, and component lifecycle checks.

> Note: `mainWebServerSecure.py` expects an auth/token service running at port `8676`. Start that service separately before running this test.

---

## 5) Useful direct API payloads (for debugging)

If you want to call the server directly, these are the payload shapes expected by the Falcon resources.

### Create

```json
{
  "type": "web_server",
  "module": "Examples.Calculator",
  "component": "Calculator1",
  "secure": false
}
```

### Connect

```json
{
  "type": "web_server",
  "component_src": "Calculator1",
  "component_intf": "Adder1",
  "intf_type": "Examples.IAdd"
}
```

### Start

```json
{
  "type": "web",
  "component_id": "Start1"
}
```

---

## 6) Troubleshooting

### `ModuleNotFoundError` for local packages

Set `PYTHONPATH` correctly:

```bash
export PYTHONPATH="$PWD/src"
```

### `Connection refused` to `localhost:8654`

Ensure `SecureWebAPIServer.py` is running and listening on port `8654`.

### Auth failures in secure test

- Confirm token service is up at `http://localhost:8676/token`.
- Confirm test credentials are valid (`alice` / `password123` in current test script).

### Duplicate component creation errors

This is expected in the remote test; duplicate creation is intentionally exercised as a negative test.

---

## 7) Quick command summary

```bash
# from repo root
export PYTHONPATH="$PWD/src"

# terminal A
python src/API/SecureWebAPIServer.py

# terminal B (remote create/connect/start flow)
python tests/WebServerTests/mainWebServerRemote.py

# terminal B (secure authz flow)
python tests/WebServerTests/mainWebServerSecure.py
```

---

## 8) Reference files

- `src/API/SecureWebAPIServer.py`
- `src/API/WebAPI.py`
- `src/Runtimes/runtime.py`
- `tests/WebServerTests/mainWebServerRemote.py`
- `tests/WebServerTests/mainWebServerSecure.py`

