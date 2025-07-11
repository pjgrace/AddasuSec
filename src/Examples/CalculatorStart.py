from AddasuSec.Component import Component

class CalculatorStart(Component):

    receptacle1_type = "Examples.ICalculate"

    def __init__(self, name):
        super().__init__({self.receptacle1_type})

    def start(self):
        calc = self.getReceptacle(self.receptacle1_type)
        print(f"The value of 9 + 10 = {calc.add(9,10)}")
        print(f"The value of 6 - 4 = {calc.sub(6,4)}")
    