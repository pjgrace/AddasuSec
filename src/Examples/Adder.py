from AddasuSec.Component import Component
from Examples.IAdd import IAdd


class Adder(Component, IAdd):

  def __init__(self, name):
      super().__init__({})

  def add(self, a: int, b: int) -> int:
      return a + b + 52

  