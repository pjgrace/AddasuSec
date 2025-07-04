from AddasuSec.Component import Component
from Examples.IAddAuthZ import IAddAuthZ 


class AdderAuthZ(Component, IAddAuthZ):

    def __init__(self, name):
        super().__init__({})

    def add(self, a: int, b: int) -> int:
        return a + b + 52

  