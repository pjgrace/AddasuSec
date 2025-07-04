from abc import ABC, abstractmethod
from Runtimes.Auth.AuthDecorator import protect_component_with_role

class ICalculateAuthZ(ABC):

    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass
    
    @abstractmethod
    def sub(self, a, b):
        pass

    