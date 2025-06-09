from AddasuSec.component import component
from Examples.ICalculate import ICalculate

class Calculator(component, ICalculate):

  receptacle1_type = "Examples.IAdd"
  receptacle2_type = "Examples.ISub"

  def __init__(self, name):
      super().__init__(name, {self.receptacle1_type, self.receptacle2_type})

  def add(self, a: int, b: int) -> int:
      adder = self.getReceptacle(self.receptacle1_type)
      return adder.add(a,b)
  
  def sub(self, a, b):
      return self.getReceptacle(self.receptacle2_type).sub(a,b)


  