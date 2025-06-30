from AddasuSec.component import component
from Examples.IAdd import IAdd


class Adder(component, IAdd):

  def __init__(self, name):
      super().__init__({})

  def add(self, a: int, b: int) -> int:
      return a + b + 52

  