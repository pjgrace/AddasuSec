from receptacle import Receptacle
from Runtimes.rpcRuntime import rpcRuntime
import os
import requests
import json
from requests.auth import HTTPBasicAuth

opencom = rpcRuntime()
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("Examples.Calculator", "Calculator1")
y = opencom.create("Examples.Adder", "Adder1")

lst_comps = opencom.getAllComponents()

for index in lst_comps:
   print(f"component: {index} ")
   
print(opencom.connect(x,y,"Examples.IAdd"))

basic = HTTPBasicAuth('user', 'pass')

url = 'http://localhost:8000/Calculator1/add?a=676&b=8'

x = requests.post(url, auth=basic)
# parse x:
y = json.loads(x.text)

# the result is a Python dictionary:
print(y["sum"])