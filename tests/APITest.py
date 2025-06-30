
import requests

BASE_URL = "http://localhost:8000"

def create_component(type_, module, component):
    resp = requests.post(f"{BASE_URL}/create", json={
        "type": type_,
        "module": module,
        "component": component
    })
    print(resp.json())

def delete_component(type_, component_id):
    resp = requests.post(f"{BASE_URL}/delete", json={
        "type": type_,
        "component_id": component_id
    })
    print(resp.json())

def connect_components(type_, src, intf, intf_type):
    resp = requests.post(f"{BASE_URL}/connect", json={
        "type": type_,
        "component_src": src,
        "component_intf": intf,
        "intf_type": intf_type
    })
    print(resp.json())

def disconnect_components(type_, src, intf, intf_type):
    resp = requests.post(f"{BASE_URL}/disconnect", json={
        "type": type_,
        "component_src": src,
        "component_intf": intf,
        "intf_type": intf_type
    })
    print(resp.json())

# Example usage:
if __name__ == "__main__":
    create_component("plain", "Examples.Calculator", "Caclulator1")
    create_component("plain", "Examples.Adder", "Adder1")
    #connect_components("plain", "Caclulator1", "Adder1", "Examples.IAdd")

if __name__ == '__main__':
    pass