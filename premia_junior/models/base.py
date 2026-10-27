from abc import ABC, abstractmethod
import numpy as np


class BaseModel(ABC):
    
    compatible_methods : list =[]
    
    @abstractmethod
    def simulate(self, S0: float,r:float, T: float, n_steps: int, n_paths: int, seed=None) -> np.ndarray:
        pass

    def characteristic_function(self,u:float,t:float)->float | None :
        pass 
    @abstractmethod

    def parameters(self)->dict:
        pass
    @classmethod
    @abstractmethod
    def name(cls)-> str:
        pass 
    
    def with_params(self, **changes):
        names = self.parameter_info().keys()
        params = {k: v for k, v in self.parameters().items() if k in names}
        return type(self)(**{**params, **changes})
    
    @classmethod 
    @abstractmethod 
    def parameter_info(cls)->dict :
        pass 
    

    