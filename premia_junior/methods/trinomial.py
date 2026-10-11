from .base import BaseMethod
from ..registry import register_method
from ..engine.result import PricingResult
import numpy as np


@register_method
class TrinomialTree(BaseMethod):
    compatible_exercise_types = ["european", "american"]
    compatible_option_types = ["call", "put"]
    def __init__(self, n_steps):
        self.n_steps = n_steps
    def price(self, product, model, S0, T, r):
        sigma = model.sigma
        N = self.n_steps
        dt = T / N
        
        dx = sigma * np.sqrt(3 * dt)
        nu = r - 0.5 * sigma**2
        
        p_u = 1/6 + (nu * np.sqrt(dt / 3)) / (2 * sigma)
        p_m = 2/3
        p_d = 1/6 - (nu * np.sqrt(dt / 3)) / (2 * sigma)

        j_values = np.arange(2 * N + 1)
        stocks = S0 * np.exp((j_values - N) * dx)
        
        if product.option_type() == 'call':
            prices = np.maximum(stocks - product.K, 0)
        else:
            prices = np.maximum(product.K - stocks, 0)

        discount = np.exp(-r * dt)
        for _ in range(N):
            prices = (p_d * prices[:-2] + p_m * prices[1:-1] + p_u * prices[2:]) * discount
            
        price = prices[0]
        
        metadata = {
            "Method": "TrinomialTree",
            "Model": model.name(),
            "Product": product.name()
        }
        
        Pr = PricingResult(price, confidence_interval=None, metadata=metadata)
        return Pr

    @classmethod
    def name(cls):
        return "TrinomialTree"

    @classmethod
    def parameter_info(cls) -> dict:
        d = {
            "n_steps": {"default": 50, "min": 5, "max": 1000000, "step": 1}
        }
        return d