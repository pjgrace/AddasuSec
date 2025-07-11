from AddasuSec.Component import Component
from Examples.ISub import ISub


class Subber(Component, ISub):
  
  def __init__(self, name):
      super().__init__({})

  def sub(self, a: int, b: int)->int:
      return a-b

  