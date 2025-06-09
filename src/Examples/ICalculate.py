from abc import ABC, abstractmethod

class ICalculate(ABC):

    @abstractmethod
    def add(self, a: int, b: int) -> int:
        pass
    
    @abstractmethod
    def sub(self, a, b):
        pass

    