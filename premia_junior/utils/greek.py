from .BaseGreekScheme import CentralDifference2
import numpy as np


class FiniteDifference():
    def _value(self, result):
        return result.price if result.samples is None else result.samples


    def _estimate(self,q):
        if np.ndim(q)==0:
            return float(q),None 
        return q.mean(), q.std(ddof=1)/np.sqrt(len(q))
            
        
        
        
    def __init__(self, scheme, h):
            self.scheme = scheme
            self.h = h

    def delta(self, pricer, S0, T, r):
        def P(s): return self._value(pricer.price(s,T,r)) 
        return self._estimate(self.scheme(self.h, S0, P))

    def gamma(self, pricer, S0, T, r):
        def P(s): return self._value(pricer.price(s,T,r)) 
        return self._estimate(CentralDifference2()(self.h, S0, P))

    def rho(self, pricer, S0, T, r):
        def P(r): return self._value(pricer.price(S0,T,r)) 
        return self._estimate(self.scheme(self.h, r, P))

    def theta(self, pricer, S0, T, r):
        def P(T): return -self._value(pricer.price(S0,T,r)) 
        return self._estimate(self.scheme(self.h, T, P))

    def vega(self, pricer, S0, T, r):
        sigma = pricer.model.sigma
        def P(x):
            model = pricer.model.with_params(sigma=x)
            return self._value(type(pricer)(model, pricer.method, pricer.product).price(S0, T, r))
        return self._estimate(self.scheme(self.h, sigma, P))
