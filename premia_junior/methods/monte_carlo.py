
from .base import BaseMethod
from ..registry import register_method 
from ..engine.result import PricingResult
import numpy as np 

@register_method
class MonteCarlo(BaseMethod):
    def __init__(self,n_paths,n_steps,seed=None):
        compatible_exercise_types = ["european"]
        self.n_paths=n_paths
        self.n_steps=n_steps
        self.seed=seed
    def price(self,product,model,S0:float,T:float,r:float):
        n_steps=self.n_steps
        n_paths=self.n_paths
        seed=self.seed
        paths=model.simulate(S0,r,T,n_steps,n_paths,seed)
        payoff=product.payoff(paths)
        price=payoff.mean()*np.exp(-r*T)
        std=np.std(payoff)
        SE= std/np.sqrt(n_paths)
        lower = (np.mean(payoff) - 1.96 * SE) * np.exp(-r * T)
        upper = (np.mean(payoff) + 1.96 * SE) * np.exp(-r * T)
        metadata={
            "Method": "MonteCarlo",
            "Model": model.name(),
             "Product": product.name()
        }
        Pr = PricingResult(price=price,confidence_interval=(lower,upper),metadata=metadata) 
        return Pr
    @classmethod
    def name(cls) -> str:
        return "Monte Carlo"
    @classmethod 
    def parameter_info(cls)->dict:
        d={
            "n_paths":{"default": 1024, "min": 1, "max": 2**25, "step": 1},
            "n_steps":{"default": 50, "min": 5, "max": 1000000, "step": 1}
           }
        return d 