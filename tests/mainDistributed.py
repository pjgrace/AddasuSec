from Runtimes.runtime import runtime
import os
from requests.auth import HTTPBasicAuth
from MetaArchitecture.MetaArchitecture import MetaArchitecture
import requests
import json

meta = MetaArchitecture()
opencom = runtime(meta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("web", "Examples.Calculator", "Calculator1")
y = opencom.create("web", "Examples.Adder", "Adder1")

lst_comps = meta.getAllComponents()

for index in lst_comps:
   print(f"component: {index} ")
   
print(opencom.connect("web", x,y,"Examples.IAdd"))

basic = HTTPBasicAuth('user', 'pass')

url = 'http://localhost:8000/Calculator1/add?a=676&b=8'

x = requests.post(url, auth=basic)
# parse x:
y = json.loads(x.text)

# the result is a Python dictionary:
print(y["sum"])