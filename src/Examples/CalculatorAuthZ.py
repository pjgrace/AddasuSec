from AddasuSec.Component import Component
from Examples.ICalculateAuthZ import ICalculateAuthZ 
from Runtimes.Auth.AuthDecorator import protect_component_with_role,\
    role_required

class CalculatorAuthZ(Component, ICalculateAuthZ):

    receptacle1_type = "Examples.IAdd"
    receptacle2_type = "Examples.ISub"

    def __init__(self, name):
        super().__init__({self.receptacle1_type, self.receptacle2_type})
    
    @role_required('admin')
    def add(self, a: int, b: int) -> int:
        adder = self.getReceptacle(self.receptacle1_type)
        return adder.add(a,b)
    
    def sub(self, a, b):
        return self.getReceptacle(self.receptacle2_type).sub(a,b)