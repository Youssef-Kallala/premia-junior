from ..registry import register_model
from .base import BaseModel
import numpy as np


@register_model
class BlackScholes(BaseModel):
    compatible_methods = ["Analytical","CRR", "Monte Carlo", "FDM", "FFT","TrinomialTree","LSM"]

    def __init__(self, mu, sigma):
        self.sigma = sigma
        self.mu = mu

    def simulate(self, S0: float, r: float, T: float, n_steps: int, n_paths: int, seed=None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        dt = T / n_steps
        Z = rng.standard_normal((n_paths, n_steps))
        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = S0
        for i in range(1, n_steps + 1):
            paths[:, i] = paths[:, i-1] * np.exp(
                (r - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z[:, i-1]
            )
        return paths

    def parameters(self) -> dict:
        d = {}
        d['mu'] = self.mu
        d['sigma'] = self.sigma
        return d

    @classmethod
    def name(cls) -> str:
        return "BlackScholes"

    @classmethod
    def parameter_info(cls) -> dict:
        d = {
            "mu": {"default": 0.05, "min": -1.0, "max": 1.0, "step": 0.01},
            "sigma": {"default": 0.2, "min": 0.01, "max": 2.0, "step": 0.01}
        }
        return d