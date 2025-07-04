from abc import ABC, abstractmethod

class IAdd(ABC):

    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass

    