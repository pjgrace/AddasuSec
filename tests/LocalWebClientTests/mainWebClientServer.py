from Runtimes.runtime import runtime
import requests
import json
from requests.auth import HTTPBasicAuth
from MetaArchitecture.MetaArchitecture import MetaArchitecture

meta = MetaArchitecture()
opencom = runtime(meta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("web_server", "Examples.Calculator", "Calculator1", False)
y = opencom.create("plain", "Examples.Adder", "Adder1", False)

print(opencom.connect("web_server", x,y,"Examples.IAdd"))

basic = HTTPBasicAuth('user', 'pass')

url = 'http://localhost:8000/Calculator1/add?a=676&b=8'

x = requests.post(url, auth=basic)
# parse x:
y = json.loads(x.text)

# the result is a Python dictionary:
print(y["sum"])

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
      
