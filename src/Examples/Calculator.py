from AddasuSec.Component import Component
from Examples.ICalculate import ICalculate

class Calculator(Component, ICalculate):

    receptacle1_type = "Examples.IAdd"
    receptacle2_type = "Examples.ISub"

    def __init__(self, name):
        super().__init__({self.receptacle1_type, self.receptacle2_type})

    def add(self, a: int, b: int) -> int:
        adder = self.getReceptacle(self.receptacle1_type)
        return adder.add(a,b)
    
    def sub(self, a: int, b: int) -> int:
        return self.getReceptacle(self.receptacle2_type).sub(a,b)


  