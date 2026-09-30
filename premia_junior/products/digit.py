from ..registry import register_product
from .base import BaseProduct
import numpy as np


@register_product
class PutDigit(BaseProduct):
    def __init__(self, K: float, Q:float):
        self.K = K
        self.Q=Q 
    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return self.Q *(paths[:, -1] > self.K)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "PutDigit"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "PutDigit"


@register_product
class CallDigit(BaseProduct):
    def __init__(self, K: float, Q:float):
        self.K = K
        self.Q=Q
    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return self.Q * (paths[:, -1] < self.K)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "CallDigit"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "CallDigit"
