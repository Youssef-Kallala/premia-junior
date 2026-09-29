import numpy as np
from scipy.stats import norm
from .base import BaseMethod
from ..registry import register_method 
from ..engine.result import PricingResult


@register_method
class Analytical(BaseMethod):
    def __init__(self):
        compatible_exercise_types = ["european"]
        pass 
    def price(self, product, model, S0: float , T: float , r:float)->PricingResult:
        if model.name() != "BlackScholes":
            raise ValueError(f"Analytical method only supports BlackScholes, got {model.name()}")
        if product.exercise_type() != "european":
            raise ValueError(f"Analytical method only supports European options, got {product.exercise_type()}")
        sigma=model.sigma
        K=product.K 
        d1=(np.log(S0/K)+(0.5*sigma**2+r)*T)/(sigma*np.sqrt(T))
        d2=d1-sigma*np.sqrt(T)
        if product.option_type()=='call':
            s1=S0*norm.cdf(d1)
            s2=K*np.exp(-r*T)*norm.cdf(d2)
            price=s1-s2
        else : 
            s1=S0*norm.cdf(-d1)
            s2=K*np.exp(-r*T)*norm.cdf(-d2)
            price=s2-s1
        metadata={
            "method": "Analytical",
            "model": "BlackScholes",
            "d1": d1,
            "d2": d2
        }
        Pr = PricingResult(price=price,metadata=metadata)
        return Pr 
    @classmethod
    def name(cls) -> str:
        return "Analytical"
    
    @classmethod
    def parameter_info(cls) -> dict:
        return {}

