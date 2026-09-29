from ..registry import register_product
from .base import BaseProduct 
import numpy as np 

@register_product
class AmericanCall(BaseProduct):
    def __init__(self,K: float):
        self.K=K 
    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(paths[:,-1]-self.K,0)
    def exercise_type(self)->str:
        return "american"
    @classmethod
    def name(cls)->str: 
        return "AmericanCall"
    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K":    {"default": 100, "min": 0, "max": 100000,  "step": 1},
        }
    def option_type(self):
        return "call"


@register_product
class AmericanPut(BaseProduct):
    def __init__(self,K: float):
        self.K=K 
    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(self.K-paths[:,-1],0)
    def exercise_type(self)->str:
        return "american"
    @classmethod
    def name(cls)->str: 
        return "AmericanPut"
    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K":    {"default": 100, "min": 0, "max": 100000,  "step": 1},
        }
    def option_type(self):
        return "put"


