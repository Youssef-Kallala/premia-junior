
from .base import BaseMethod
from ..registry import register_method
from ..engine.result import PricingResult
import numpy as np


@register_method
class CRR(BaseMethod):
    def __init__(self, n_steps):
        self.n_steps = n_steps
        compatible_exercise_types = ["european", "american"]
    def price(self, product, model, S0, T, r):
        sigma = model.sigma
        N = self.n_steps
        dt = T/N
        u = np.exp(sigma*(dt**0.5))
        d = 1/u
        p = (np.exp(r*dt)-d)/(u-d)
        stocks = np.array([S0*u**j*d**(N-j) for j in range(N+1)])
        if product.option_type() == 'call':
            prices = np.maximum(stocks - product.K, 0)
        else:
            prices = np.maximum(product.K - stocks, 0)
        is_american = product.exercise_type() == "american"

        for i in range(N):
            continuation = np.exp(-r*dt) * (p*prices[1:] + (1-p)*prices[:-1])
            if is_american:
                n_nodes = N - i  
                current_stocks = np.array([S0*u**j*d**(N-i-j-1) for j in range(n_nodes)])
                if product.option_type() == 'call':
                    intrinsic = np.maximum(current_stocks - product.K, 0)
                else:
                    intrinsic = np.maximum(product.K - current_stocks, 0)
                prices = np.maximum(continuation, intrinsic)
            else:
                prices = continuation
        price = prices[0]
        metadata = {
            "Method": "CRR",
            "Model": model.name(),
            "Product": product.name()
        }
        Pr = PricingResult(price, confidence_interval=None, metadata=metadata)
        return Pr

    @classmethod
    def name(cls):
        return "CRR"

    @classmethod
    def parameter_info(cls) -> dict:
        d = {
            "n_steps": {"default": 50, "min": 5, "max": 1000000, "step": 1}
        }
        return d
