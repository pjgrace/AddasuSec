from Runtimes.runtime import runtime
import os
from MetaArchitecture.MetaArchitecture import MetaArchitecture

addasuMeta = MetaArchitecture()
addasuSec = runtime(addasuMeta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = addasuSec.create("web_client", "Examples.Calculator", "Calculator1")
y = addasuSec.remoteCreate("http://localhost:8654","web", "Examples.Adder", "Adder1")

print(addasuSec.connect("web_client", x,y,"Examples.IAdd"))

print(x.add(1, 2))

addasuMeta.setInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation", 8)
print(addasuMeta.getInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation"))        

list_connections = addasuMeta.connectionsToIntf("Adder1", "Examples.IAdd")
for index in list_connections:
   print(f"component a: {index} ")
   
list_connections2 = addasuMeta.connectionsFromRecp("Calculator1", "Examples.IAdd")
for index in list_connections2:
   print(f"component b: {index} ")
   
list_connections3 = addasuMeta.connectionsFromRecp("Calculator1", "Examples.ISub")
for index in list_connections3:
   print(f"component v: {index} ")   

# Open inspection: Get Interfaces
print(addasuMeta.getInterfaces("Calculator1"))
print(addasuMeta.getInterfaces("Adder1"))

# Open inspection: List Component
print(addasuMeta.getAllComponents())
      
print(x.add(1, 2))
