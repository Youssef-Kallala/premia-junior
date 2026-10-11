from ..registry import register_model
from .base import BaseModel
import numpy as np


@register_model
class Heston(BaseModel):
    compatible_methods = ["Monte Carlo"]
    def __init__(self,v0,kappa,theta,xi,rho):
        self.v0=v0
        self.kappa=kappa 
        self.theta=theta
        self.xi=xi 
        self.rho=rho
        if 2*kappa*theta > xi**2 :
            print("Feller Condition is verified So the variance is always positive")
    def simulate(self,S0,r,T,n_steps,n_paths,seed=None):
        rng = np.random.default_rng(seed)
        dt=T/n_steps
        Z=rng.standard_normal((n_paths,n_steps)) 
        Z1=rng.standard_normal((n_paths,n_steps))
        pho=self.rho
        Zv=pho*Z+np.sqrt(1-pho*pho)*Z1 
        Zs=Z
        S=np.zeros((n_paths,n_steps+1))
        S[:,0]=S0
        V=np.zeros((n_paths,n_steps+1))
        V[:,0]=self.v0
        kappa=self.kappa 
        theta=self.theta 
        xi=self.xi 
        rho=self.rho 
        for i in range(1,n_steps+1):
            V_plus=np.maximum(V[:,i-1],0)
            V[:,i]=V_plus+kappa*(theta-V_plus)*dt+xi*np.sqrt(V_plus)*Zv[:,i-1]*np.sqrt(dt)
            V[:,i]=np.maximum(V[:,i],0)
            S[:,i] = S[:,i-1] * np.exp((r - 0.5*V_plus)*dt + np.sqrt(V_plus)*np.sqrt(dt)*Zs[:,i-1])
        return S 
    def parameters(self):
        d={
            "v0":self.v0,
            "kappa":self.kappa,
            "theta":self.theta,
            "xi":self.xi,
            "rho":self.rho
        }
        return d 
    @classmethod
    def name(cls):
        return "Heston"
    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "v0":    {"default": 0.04,  "min": 0.001, "max": 1.0,  "step": 0.001},
            "kappa": {"default": 1.5,   "min": 0.01,  "max": 10.0, "step": 0.01},
            "theta": {"default": 0.04,  "min": 0.001, "max": 1.0,  "step": 0.001},
            "xi":    {"default": 0.3,   "min": 0.01,  "max": 2.0,  "step": 0.01},
            "rho":   {"default": -0.7,  "min": -1.0,  "max": 1.0,  "step": 0.01},
        }
        
    