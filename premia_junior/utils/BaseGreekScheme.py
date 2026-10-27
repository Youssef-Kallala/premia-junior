from abc import abstractmethod, ABC


class BaseGreekScheme(ABC):

    @abstractmethod
    def __call__(self, h, x, P):
        pass


class CentralDifference1(BaseGreekScheme):
    def __call__(self, h, x, P):
        return (P(x+h) - P(x-h)) / (2*h)


class ForwardDifference(BaseGreekScheme):
    def __call__(self, h, x, P):
        return (P(x+h) - P(x)) / h


class BackwardDifference(BaseGreekScheme):
    def __call__(self, h, x, P):
        return (P(x) - P(x-h)) / h


class CentralDifference2(BaseGreekScheme):
    def __call__(self, h, x, P):
        return (P(x+h)+P(x-h)-2*P(x))/(h**2)
