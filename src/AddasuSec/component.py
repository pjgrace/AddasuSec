from AddasuSec.receptacle import Receptacle

class component:
    receptacles = {}
    
    def __init__(self, name, receptacle_list):
        for item in receptacle_list:
            rcp = Receptacle(item)
            self.receptacles[item] = rcp
        
        self.label = name
    
    def dynamic_call(self, name: str, *args, **kwargs):
        do = f"get_{name}"
        if hasattr(self, do) and callable(getattr(self, do)):
            func = getattr(self, do)
            func(*args, **kwargs)

    def getReceptacle(self, r_type):
        rp = self.receptacles.get(r_type)
        return rp._Comp
    
    def connect(self, component, intf):
        try:
            return self.receptacles.get(intf).connect(component, intf)
        except ValueError:
            return False

    def disconnect(self, intf):
        try:
            return self.receptacles.get(intf).disconnect()
        except ValueError:
            return False
        
    def start(self, param):
        return True
        
    def stop(self):
        return True
        