from .BaseGreekScheme import CentralDifference2


class FiniteDifference():
    def __init__(self, scheme, h):
        self.scheme = scheme
        self.h = h

    def delta(self, pricer, S0, T, r):
        def P(s): return pricer.price(s, T, r).price
        return self.scheme(self.h, S0, P)

    def gamma(self, pricer, S0, T, r):
        def P(s): return pricer.price(s, T, r).price
        return CentralDifference2()(self.h, S0, P)

    def rho(self, pricer, S0, T, r):
        def P(r): return pricer.price(S0, T, r).price
        return self.scheme(self.h, r, P)

    def theta(self, pricer, S0, T, r):
        def P(T): return pricer.price(S0, T, r).price
        return -self.scheme(self.h, T, P)

    def vega(self, pricer, S0, T, r):
        sigma = pricer.model.sigma
        def P(x):
            model = pricer.model.with_params(sigma=x)
            return type(pricer)(model, pricer.method, pricer.product).price(S0, T, r).price
        return self.scheme(self.h, sigma, P)
    