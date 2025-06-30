from Runtimes.runtime import runtime
import os
from MetaArchitecture.MetaArchitecture import MetaArchitecture

meta = MetaArchitecture()
opencom = runtime(meta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("web_client", "Examples.Calculator", "Calculator1")
y = opencom.create("web", "Examples.Adder", "Adder1")

print(opencom.connect("web_client", x,y,"Examples.IAdd"))

print(x.add(1, 2))

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
      
print(x.add(1, 2))
