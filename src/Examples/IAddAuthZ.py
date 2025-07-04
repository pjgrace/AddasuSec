from abc import ABC, abstractmethod
from Runtimes.Auth.AuthDecorator import protect_component_with_role

@protect_component_with_role('admin')
class IAddAuthZ(ABC):

    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass

    