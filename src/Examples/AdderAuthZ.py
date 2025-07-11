from AddasuSec.Component import Component
from Examples.IAdd import IAdd 
from Runtimes.Auth.AuthDecorator import role_required

class AdderAuthZ(Component, IAdd):

    def __init__(self, name):
        super().__init__({})

    @role_required('admin')
    def add(self, a: int, b: int) -> int:
        return a + b 

  