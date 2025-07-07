import AddasuSec.WebReceptacle

def data_storage_method(func):
    func.is_data_storage = True
    return func

class WebClientComponent:
    receptacles = {}
    
    def __init__(self, component):
        self.innerComponent = component
        for item in component.receptacles:
            rcp = AddasuSec.WebReceptacle.WebReceptacle(item)
            self.innerComponent.receptacles[item] = rcp
    
    def dynamic_call(self, name: str, *args, **kwargs):
        do = f"get_{name}"
        if hasattr(self, do) and callable(getattr(self, do)):
            func = getattr(self, do)
            func(*args, **kwargs)

    def getReceptacle(self, r_type):
        rp = self.receptacles.get(r_type)
        return rp._Comp
    
    
    def connect(self, component, intf, rt):
        try:
            return self.innerComponent.receptacles.get(intf).connect(component, intf, rt)
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
        