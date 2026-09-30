from ..registry import register_product
from .base import BaseProduct
import numpy as np


@register_product
class CallUpIn(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(paths[:, -1] - self.K, 0) * (np.max(paths, axis=1) > self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "CallUpIn"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 120, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class CallUpOut(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(paths[:, -1] - self.K, 0) * (np.max(paths, axis=1) < self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "CallUpOut"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 120, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class CallDownIn(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(paths[:, -1] - self.K, 0) * (np.min(paths, axis=1) <= self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "CallDownIn"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class CallDownOut(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(paths[:, -1] - self.K, 0) * (np.min(paths, axis=1) > self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "CallDownOut"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class PutUpIn(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(-paths[:, -1] + self.K, 0) * (np.max(paths, axis=1) > self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "PutUpIn"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 120, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class PutUpOut(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(-paths[:, -1] + self.K, 0) * (np.max(paths, axis=1) < self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "PutUpOut"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 120, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class PutDownIn(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(-paths[:, -1] + self.K, 0) * (np.min(paths, axis=1) <= self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "PutDownIn"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"


@register_product
class PutDownOut(BaseProduct):
    def __init__(self, K: float, B: float):
        self.K = K
        self.B = B

    def payoff(self, paths: np.ndarray) -> np.ndarray:
        return np.maximum(-paths[:, -1] + self.K, 0) * (np.min(paths, axis=1) > self.B)

    def exercise_type(self) -> str:
        return "european"

    @classmethod
    def name(cls) -> str:
        return "PutDownOut"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "K": {"default": 100, "min": 0, "max": 100000, "step": 1},
            "B": {"default": 80, "min": 0, "max": 100000, "step": 1},
        }

    def option_type(self) -> str:
        return "barrier"