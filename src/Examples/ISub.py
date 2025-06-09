from abc import ABC, abstractmethod


class ISub(ABC):

    @abstractmethod
    def sub(self, a, b):
        pass

    