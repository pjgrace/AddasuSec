from AddasuSec.receptacle import Receptacle
from Runtimes.runtime import runtime
import os
from MetaArchitecture.MetaArchitecture import MetaArchitecture

meta = MetaArchitecture()
opencom = runtime(meta)
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("plain", "Examples.Calculator", "Calculator 1")
w = opencom.create("plain", "Examples.Calculator", "Calculator 2")
y = opencom.create("plain", "Examples.Adder", "Adder 1")
z = opencom.create("plain", "Examples.Subber", "Subber 1")

print(opencom.connect("plain", x,y,"Examples.IAdd"))
print(opencom.connect("plain", w,y,"Examples.IAdd"))
print(opencom.connect("plain", x,z,"Examples.ISub"))

print(x.add(1, 2))
print(x.sub(8, 1))

meta.setInterfaceAttributeValue("Calculator 1", "Examples.IAdd",  "Variation", 8)
print(meta.getInterfaceAttributeValue("Calculator 1", "Examples.IAdd",  "Variation"))        

list_connections = meta.connectionsToIntf("Adder 1", "Examples.IAdd")
for index in list_connections:
   print(f"component a: {index} ")
   
list_connections2 = meta.connectionsFromRecp("Calculator 1", "Examples.IAdd")
for index in list_connections2:
   print(f"component b: {index} ")
   
list_connections3 = meta.connectionsFromRecp("Calculator 1", "Examples.ISub")
for index in list_connections3:
   print(f"component v: {index} ")   

# Open inspection: Get Interfaces
print(meta.getInterfaces("Calculator 1"))
print(meta.getInterfaces("Calculator 2"))
print(meta.getInterfaces("Adder 1"))
print(meta.getInterfaces("Subber 1"))
 
# Open inspection: Get Receptacles
print(meta.getReceptacles("Calculator 2"))
print(meta.getReceptacles("Adder 1"))
print(meta.getReceptacles("Subber 1"))

# Open inspection: List Component
print(meta.getAllComponents())
      
opencom.delete("plain", "Calculator 2")
print(meta.getAllComponents())

print(x.add(1, 2))
