"""
MainRemote.py

Tests the remote creation and connection of components from the central
runtime to a separate runtime.

Author: Paul Grace
Created: 2025-07-01
Updated: 2025-07-02
License: MIT
"""

from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
import os, sys
from MetaArchitecture.MetaArchitecture import MetaArchitecture

#initialise the central runtime
addasuMeta = MetaArchitecture()
addasuSec = runtime(addasuMeta)

#Target remote runtime, set for localhost for Github distribution
REMOTE_RUNTIME = "http://localhost:8654"

#create an initial set of components on the remote host
try:
    calc1 = addasuSec.remoteCreate(REMOTE_RUNTIME, "plain", "Examples.Calculator", "Calculator1", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc1)}")
    
    calc2 = addasuSec.remoteCreate(REMOTE_RUNTIME, "plain", "Examples.Calculator", "Calculator2", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc2)}")
    add1 = addasuSec.remoteCreate(REMOTE_RUNTIME, "plain", "Examples.Adder", "Adder1", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
    sub1 = addasuSec.remoteCreate(REMOTE_RUNTIME, "plain", "Examples.Subber", "Subber1", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(sub1)}")
except ComponentException as e:
    print("Exception creating a component:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")

#try to create another component with the same name, this should raise and exception and continue
try:
    add1 = addasuSec.remoteCreate(REMOTE_RUNTIME, "plain", "Examples.Adder", "Adder1", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
except ComponentException as e:
    print("Exception creating a component:", e) 

#connect the remote components on the different host
try:
    if addasuSec.remoteConnect(REMOTE_RUNTIME, "plain", calc1,add1,"Examples.IAdd"):
        print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(add1)}")
    if addasuSec.remoteConnect(REMOTE_RUNTIME, "plain", calc2,add1,"Examples.IAdd"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(add1)}")
    if addasuSec.remoteConnect(REMOTE_RUNTIME, "plain", calc1,sub1,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(sub1)}")
    if addasuSec.remoteConnect(REMOTE_RUNTIME, "plain", calc2,sub1,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(sub1)}")
    
except ConnectionException as e:
    print("Exception connecting components:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")
    

#Our metaarchitecture is local to the central runtime, therefore we can view and change 
addasuMeta.setInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation", 8)
print(addasuMeta.getInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation"))        

# View the connections to the IAdd interface of the Adder component
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

addasuMeta.visualise()
