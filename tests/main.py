from AddasuSec.receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
import os, sys
from MetaArchitecture.MetaArchitecture import MetaArchitecture

#initialise the central runtime
addasuMeta = MetaArchitecture()
addasuSec = runtime(addasuMeta)

#create an initial set of components
try:
    calc1 = addasuSec.create("plain", "Examples.Calculator", "Calculator1")
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc1)}")
    calc2 = addasuSec.create("plain", "Examples.Calculator", "Calculator2")
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc2)}")
    add1 = addasuSec.create("plain", "Examples.Adder", "Adder1")
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
    sub1 = addasuSec.create("plain", "Examples.Subber", "Subber1")
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
except ComponentException as e:
    print("Exception creating a component:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")

#try to create another component with the same name, this should raise and exception and continue
try:
    add1 = addasuSec.create("plain", "Examples.Adder", "Adder1")
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
except ComponentException as e:
    print("Exception creating a component:", e) 

try:
    if addasuSec.connect("plain", calc1,add1,"Examples.IAdd"):
        print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(add1)}")
    if addasuSec.connect("plain", calc2,add1,"Examples.IAdd"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(add1)}")
    if addasuSec.connect("plain", calc1,sub1,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(sub1)}")
    if addasuSec.connect("plain", calc2,sub1,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(sub1)}")
    
except ConnectionException as e:
    print("Exception connecting components:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")
    
#addasuMeta.visualise()

print(calc1.add(1, 2))
print(calc1.sub(8, 1))

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
print(addasuMeta.getInterfaces("Calculator2"))
print(addasuMeta.getInterfaces("Adder1"))
print(addasuMeta.getInterfaces("Subber1"))
 
# Open inspection: Get Receptacles
print(addasuMeta.getReceptacles("Calculator2"))
print(addasuMeta.getReceptacles("Adder1"))
print(addasuMeta.getReceptacles("Subber1"))

# Open inspection: List Component
print(addasuMeta.getAllComponents())
      
addasuSec.delete("plain", "Calculator2")
print(addasuMeta.getAllComponents())

print(calc1.add(1, 2))
