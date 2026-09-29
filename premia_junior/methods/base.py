from abc import ABC, abstractmethod
from ..engine.result import PricingResult

class BaseMethod(ABC):
    
    
    @abstractmethod
    def price(self, product, model, S0: float , T: float , r:float)->PricingResult:
        pass 
    @classmethod
    @abstractmethod
    def name(cls)-> str:
        pass 
    @classmethod
    @abstractmethod 
    def parameter_info(cls)->dict :
        pass 