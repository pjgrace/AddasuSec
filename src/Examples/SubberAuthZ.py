from AddasuSec.Component import Component
from Examples.ISub import ISub 
from Runtimes.Auth.AuthDecorator import role_required

class SubberAuthZ(Component, ISub):

    def __init__(self, name):
        super().__init__({})

    @role_required('admin')
    def sub(self, a: int, b: int) -> int:
        return a - b

  