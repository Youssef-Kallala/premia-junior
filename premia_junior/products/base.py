import numpy as np 
from abc import ABC, abstractmethod 

class BaseProduct(ABC):
    
    @abstractmethod
    def payoff(self,paths: np.ndarray) -> np.ndarray:
        pass 
    @abstractmethod
    def exercise_type(self)-> str  :
        pass 
    @classmethod
    @abstractmethod
    def name(cls)-> str:
        pass 
    @classmethod
    @abstractmethod
    def parameter_info(cls) -> dict:
        pass
    
    @abstractmethod 
    def option_type(self)->str:
        pass 