from AddasuSec.Receptacle import Receptacle
from Runtimes.runtime import runtime, ComponentException, ConnectionException
import os, sys
from MetaArchitecture.MetaArchitecture import MetaArchitecture
import requests

#initialise the central runtime
addasuMeta = MetaArchitecture()
addasuSec = runtime(addasuMeta)

def run_tests():
    try:
        print(f"Caclulator2(1 + 2) = {calc2.add(1, 2)}")
        print(f"Caclulator2(8 - 2) = {calc2.sub(8, 2)}")
    except:
        print("Call failed - incorrect configuration")
    
def full_connection():
    # Connect the components together. So two separate Calculator components using the adder
# and subber components.
    try:
        if addasuSec.connect("plain", calc1,add1,"Examples.IAdd"):
            print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(add1)}")
        if addasuSec.connect("plain", calc2,add2,"Examples.IAdd"):
            print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(add1)}")
        if addasuSec.connect("plain", calc1,sub1,"Examples.ISub"):
            print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(sub1)}")
        if addasuSec.connect("plain", calc2,sub2,"Examples.ISub"):
            print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(sub1)}")
    except ConnectionException as e:
        print("Exception connecting components:", e)
        sys.exit("Exiting due to incorrect component configuration during startup")

#create an initial set of components
try:
    calc1 = addasuSec.create("plain", "Examples.CalculatorAuthZ", "Calculator1", True)
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc1)}")
    calc2 = addasuSec.create("plain", "Examples.Calculator", "Calculator2", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(calc2)}")
    add1 = addasuSec.create("plain", "Examples.AdderAuthZ", "Adder1", True)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
    sub1 = addasuSec.create("plain", "Examples.SubberAuthZ", "Subber1", True)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
    add2 = addasuSec.create("plain", "Examples.Adder", "Adder2", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
    sub2 = addasuSec.create("plain", "Examples.Subber", "Subber2", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
except ComponentException as e:
    print("Exception creating a component:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")

#try to create another component with the same name, this should raise and exception and continue
try:
    add1 = addasuSec.create("plain", "Examples.Adder", "Adder1", False)
    print(f"Component created: component identifier is {addasuMeta.getLabel(add1)}")
except ComponentException as e:
    print("Exception creating a component:", e) 

full_connection()

# Step 1: Obtain token from Auth Server
auth_url = "http://localhost:8001/token"
auth_data = {"username": "alice", "password": "password123"}
resp = requests.post(auth_url, data=auth_data)
resp.raise_for_status()
token = resp.json().get("access_token")
print("Obtained JWT token:", token)

print(calc1.call_with_token(calc1.add, token, 1, 2))
print(calc1.call_with_token(calc1.sub, token, 8, 1))
run_tests()


# Disconnect the components one by one and test that when disconnected
# the call will fail
try:
    if addasuSec.disconnect("plain", calc1,add1,"Examples.IAdd"):
        print(f"Successfully disconnected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(add1)}")
        try:
             print(f"Caclulator1(1 + 2) = {calc1.add(1, 2)}")
             print("Error - call should not succeed, disconnect has failed")
        except:
            print("Correctly failed add call as components not connected")
        
    if addasuSec.disconnect("plain", calc2,add2,"Examples.IAdd"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(add1)}")
        try:
             print(f"Caclulator1(1 + 2) = {calc2.add(1, 2)}")
             print("Error - call should not succeed, disconnect has failed")
        except:
            print("Correctly failed add call as components not connected")
        
    if addasuSec.disconnect("plain", calc1,sub1,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc1)} to {addasuMeta.getLabel(sub1)}")
        try:
             print(f"Caclulator1(1 + 2) = {calc1.sub (8, 2)}")
             print("Error - call should not succeed, disconnect has failed")
        except:
            print("Correctly failed sub call as components not connected")
        
    if addasuSec.disconnect("plain", calc2,sub2,"Examples.ISub"):
        print(f"Successfully connected {addasuMeta.getLabel(calc2)} to {addasuMeta.getLabel(sub1)}")
        try:
             print(f"Caclulator1(1 + 2) = {calc2.sub(1, 2)}")
             print("Error - call should not succeed, disconnect has failed")
        except:
            print("Correctly failed sub call as components not connected")

except ConnectionException as e:
    print("Exception connecting components:", e)
    sys.exit("Exiting due to incorrect component configuration during startup")

# Reconnect all the components and then run the calls
full_connection()
run_tests()

# Add metadata to each interface and check that it can be read dynamically
addasuMeta.setInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation", 8)
if addasuMeta.getInterfaceAttributeValue("Calculator1", "Examples.IAdd",  "Variation") == 8:
    print("Calc1.IAdd meta data set correctly")
else:
    print("Calc1.IAdd meta data set incorrectly")
        
addasuMeta.setInterfaceAttributeValue("Calculator2", "Examples.IAdd",  "peter", "bob")
if addasuMeta.getInterfaceAttributeValue("Calculator2", "Examples.IAdd",  "peter") == "bob":      
    print("Calc1.IAdd meta data set correctly")
else:
    print("Calc1.IAdd meta data set incorrectly")

addasuMeta.setInterfaceAttributeValue("Adder1", "Examples.IAdd",  "Variation", 77)
if addasuMeta.getInterfaceAttributeValue("Adder1", "Examples.IAdd",  "Variation") == 77:        
    print("Adder1.IAdd meta data set correctly")
else:
    print("Adder1.IAdd meta data set incorrectly")
    
addasuMeta.setInterfaceAttributeValue("Subber1", "Examples.ISub",  "Variation", 98)
if addasuMeta.getInterfaceAttributeValue("Subber1", "Examples.ISub",  "Variation") == 98:       
    print("Subber1.ISub meta data set correctly")
else:
    print("Subber1.ISub meta data set incorrectly")
    
addasuMeta.setInterfaceAttributeValue("Calculator2", "Examples.ISub",  "Variation", 87)
if addasuMeta.getInterfaceAttributeValue("Calculator2", "Examples.ISub",  "Variation") == 87:       
    print("Calc2.ISub meta data set correctly")
else:
    print("Calc2.ISub meta data set incorrectly")

print("Listing the components connected to Adder1 IAdd interface")
list_connections = addasuMeta.connectionsToIntf("Adder1", "Examples.IAdd")
for index in list_connections:
   print(f"component name: {index} ")

print("Listing the components connected from Calculator1 IAdd Receptacle")
list_connections2 = addasuMeta.connectionsFromRecp("Calculator1", "Examples.IAdd")
for index in list_connections2:
   print(f"component name: {index} ")

print("Listing the components connected from Calculator1 ISub Receptacle")  
list_connections3 = addasuMeta.connectionsFromRecp("Calculator1", "Examples.ISub")
for index in list_connections3:
   print(f"component name: {index} ")   

# Open inspection: Get Interfaces on components
print("The Interfaces on Calculator1 are:")
print(addasuMeta.getInterfaces("Calculator1"))
print("The Interfaces on Calculator2 are:")
print(addasuMeta.getInterfaces("Calculator2"))
print("The Interfaces on Adder1 are:")
print(addasuMeta.getInterfaces("Adder1"))
print("The Interfaces on Subber1 are:")
print(addasuMeta.getInterfaces("Subber1"))
 
# Open inspection: Get Receptacles
print("The Receptacles on Calculator1 are:")
recps = addasuMeta.getReceptacles("Calculator1")
for recp in recps:
     print(f"Receptacle type is {recp}")
     
print("The Receptacles on Adder1 are:")
recps = addasuMeta.getReceptacles("Adder1")
for recp in recps:
     print(f"Receptacle type is {recp}")

# Open inspection: List Component
print("The following is the list of all components running")
print(addasuMeta.getAllComponents())
      
addasuSec.delete("plain", "Calculator2")
print("The following is the list of all components running after deleting Calculator2")
print(addasuMeta.getAllComponents())
