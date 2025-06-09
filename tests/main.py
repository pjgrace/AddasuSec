from AddasuSec.receptacle import Receptacle
from Runtimes.runtime import runtime
import os

opencom = runtime()
#receptacles = {"IAdd": Receptacle("IAdd"), "ISub": Receptacle("ISub")}
x = opencom.create("Examples.Calculator", "Calculator 1")
w = opencom.create("Examples.Calculator", "Calculator 2")
y = opencom.create("Examples.Adder", "Adder 1")
z = opencom.create("Examples.Subber", "Subber 1")

print(opencom.connect(x,y,"Examples.IAdd"))
print(opencom.connect(w,y,"Examples.IAdd"))
print(opencom.connect(x,z,"Examples.ISub"))

print(x.add(1, 2))
print(x.sub(8, 1))

opencom.setInterfaceAttributeValue("Calculator 1", "Examples.IAdd",  "Variation", 8)
print(opencom.getInterfaceAttributeValue("Calculator 1", "Examples.IAdd",  "Variation"))        

list_connections = opencom.connectionsToIntf("Adder 1", "Examples.IAdd")
for index in list_connections:
   print(f"component a: {index} ")
   
list_connections2 = opencom.connectionsFromRecp("Calculator 1", "Examples.IAdd")
for index in list_connections2:
   print(f"component b: {index} ")
   
list_connections3 = opencom.connectionsFromRecp("Calculator 1", "Examples.ISub")
for index in list_connections3:
   print(f"component v: {index} ")   

# Open inspection: Get Interfaces
print(opencom.getInterfaces("Calculator 1"))
print(opencom.getInterfaces("Calculator 2"))
print(opencom.getInterfaces("Adder 1"))
print(opencom.getInterfaces("Subber 1"))
 
# Open inspection: Get Receptacles
print(opencom.getReceptacles("Calculator 2"))
print(opencom.getReceptacles("Adder 1"))
print(opencom.getReceptacles("Subber 1"))

# Open inspection: List Component
print(opencom.getAllComponents())
      
opencom.delete("Calculator 2")
print(opencom.getAllComponents())

print(x.add(1, 2))
