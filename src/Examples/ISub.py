from abc import ABC, abstractmethod
from Runtimes.Auth.AuthDecorator import protect_component_with_role

class ISub(ABC):

    @abstractmethod
    def sub(self, a: int, b: int)->int:
        pass

    