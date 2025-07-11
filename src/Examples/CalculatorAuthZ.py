from AddasuSec.Component import Component
from Examples.ICalculate import ICalculate 
from Runtimes.Auth.AuthDecorator import role_required

class CalculatorAuthZ(Component, ICalculate):

    receptacle1_type = "Examples.IAdd"
    receptacle2_type = "Examples.ISub"

    def __init__(self, name):
        super().__init__({self.receptacle1_type, self.receptacle2_type})
    
    @role_required('admin')
    def add(self, a: int, b: int) -> int:
        adder = self.getReceptacle(self.receptacle1_type)
        return adder.receptacle_with_token(adder.add, a, b)
    
    @role_required('admin')
    def sub(self, a: int, b: int) -> int:
        subber = self.getReceptacle(self.receptacle2_type)
        return subber.receptacle_with_token(subber.sub, a, b)