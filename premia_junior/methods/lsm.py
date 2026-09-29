from .base import BaseMethod
from ..registry import register_method 
from ..engine.result import PricingResult
import numpy as np 

@register_method
class LSM(BaseMethod):
    def __init__(self,n_steps,n_paths,degree=3,seed=None):
        self.n_steps=n_steps
        self.n_paths=n_paths 
        self.degree=degree
        self.seed=seed  
        compatible_exercise_types = ["american"]
    def price(self, product, model, S0, T, r):
        n_steps = self.n_steps
        n_paths = self.n_paths
        dt = T / n_steps

        paths = model.simulate(S0, r, T, n_steps, n_paths, self.seed)

        if product.option_type() == 'call':
            intrinsic = np.maximum(paths - product.K, 0)
        else:
            intrinsic = np.maximum(product.K - paths, 0)

        cash_flow = intrinsic[:, -1] * np.exp(-r * T)

        for i in range(n_steps - 1, 0, -1):
            itm = intrinsic[:, i] > 0
            if itm.sum() == 0:
                continue

            x = paths[itm, i]
            y = cash_flow[itm]

            c = np.polynomial.laguerre.lagfit(x, y, self.degree)
            continuation_pv = np.polynomial.laguerre.lagval(x, c)
            intrinsic_pv = intrinsic[itm, i] * np.exp(-r * i * dt)

            exercise = intrinsic_pv > continuation_pv
            itm_indices = np.where(itm)[0]
            exercise_indices = itm_indices[exercise]
            cash_flow[exercise_indices] = intrinsic_pv[exercise]

        price = np.mean(cash_flow)
        half_width = 1.96 * np.std(cash_flow) / np.sqrt(n_paths)

        metadata = {"Method": "LSM", "Model": model.name(), "Product": product.name()}
        return PricingResult(price, confidence_interval=(price - half_width, price + half_width), metadata=metadata)
    @classmethod
    def name(cls) -> str:
        return "LSM"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "n_paths": {"default": 10000, "min": 100, "max": 100000, "step": 100},
            "n_steps": {"default": 50, "min": 5, "max": 500, "step": 1},
            "degree":  {"default": 3, "min": 1, "max": 10, "step": 1},
        }