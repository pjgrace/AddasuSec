from Runtimes.runtime import runtime
import requests
import json
from requests.auth import HTTPBasicAuth
from MetaArchitecture.MetaArchitecture import MetaArchitecture

meta = MetaArchitecture()
opencom = runtime(meta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("plain", "Examples.CalculatorAuthZ", "Calculator1")
y = opencom.create("plain", "Examples.Adder", "Adder1")

print(opencom.connect("web_server", x,y,"Examples.IAdd"))

# Step 1: Obtain token from Auth Server
auth_url = "http://localhost:8001/token"
auth_data = {"username": "alice", "password": "password123"}
resp = requests.post(auth_url, data=auth_data)
resp.raise_for_status()
token = resp.json().get("access_token")
print("Obtained JWT token:", token)

url = 'http://localhost:8000/Calculator1/add?a=676&b=8'
headers = {"Authorization": f"Bearer {token}"}

#x = requests.post(url, headers=headers)
# parse x:
#y = json.loads(x.text)

# the result is a Python dictionary:
#print(y["sum"])

print(x.add(1,8))

meta.setInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation", 8)
print(meta.getInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation"))        

list_connections = meta.connectionsToIntf("Adder1", "Examples.IAdd")
for index in list_connections:
   print(f"component a: {index} ")
   
list_connections2 = meta.connectionsFromRecp("Calculator1", "Examples.IAdd")
for index in list_connections2:
   print(f"component b: {index} ")
   
list_connections3 = meta.connectionsFromRecp("Calculator1", "Examples.ISub")
for index in list_connections3:
   print(f"component v: {index} ")   

# Open inspection: Get Interfaces
print(meta.getInterfaces("Calculator1"))
print(meta.getInterfaces("Adder1"))
 

# Open inspection: List Component
print(meta.getAllComponents())
      
# Step 1: Obtain token from Auth Server
auth_url = "http://localhost:8001/token"
auth_data = {"username": "bob", "password": "password123"}
resp = requests.post(auth_url, data=auth_data)
resp.raise_for_status()
token = resp.json().get("access_token")
print("Obtained JWT token:", token)

url = 'http://localhost:8000/Calculator1/add?a=676&b=8'
headers = {"Authorization": f"Bearer {token}"}

#x = requests.post(url, headers=headers)
# parse x:
#y = json.loads(x.text)

# the result is a Python dictionary:
#print(y["sum"])
