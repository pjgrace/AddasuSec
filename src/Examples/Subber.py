from AddasuSec.component import component
from Examples.ISub import ISub


class Subber(component, ISub):
  
  def __init__(self, name):
      super().__init__({})

  def sub(self, a, b):
      return a -b

  