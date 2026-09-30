import numpy as np
from scipy.stats import norm
from .base import BaseMethod
from ..registry import register_method
from ..engine.result import PricingResult


@register_method
class Analytical(BaseMethod):
    compatible_exercise_types = ["european"]
    compatible_option_types = ["call", "put", "digital", "barrier"]

    def __init__(self):
        pass

    def _price_vanilla(self, product, S0, T, r, sigma):
        K = product.K
        d1 = (np.log(S0 / K) + (0.5 * sigma**2 + r) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if product.option_type() == "call":
            price = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)
        return price, d1, d2

    def _price_digital(self, product, S0, T, r, sigma):
        K = product.K
        d2 = (np.log(S0 / K) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        match product.name():
            case "CallDigit":
                return product.Q * np.exp(-r * T) * norm.cdf(d2), d2
            case "PutDigit":
                return product.Q * np.exp(-r * T) * norm.cdf(-d2), d2
            case _:
                raise ValueError(f"Unknown digital product: {product.name()}")

    def _price_barrier(self, product, S0, T, r, sigma):
        K = product.K
        B = product.B
        name = product.name()
        rebate = getattr(product, "rebate", 0.0)
        sqrt_T = np.sqrt(T)

        phi = 1 if "Call" in name else -1
        eta = 1 if "Down" in name else -1

        if eta == 1 and S0 <= B:
            raise ValueError(f"Down barrier requires S0 > B, got S0={S0}, B={B}")
        if eta == -1 and S0 >= B:
            raise ValueError(f"Up barrier requires S0 < B, got S0={S0}, B={B}")
        if "Out" in name and rebate != 0.0:
            raise ValueError("Rebates are only supported for knock-in barriers")

        lam = (r / sigma**2) + 0.5          # = 1 + mu
        vol = sigma * sqrt_T
        x1 = np.log(S0 / K) / vol + lam * vol
        x2 = np.log(S0 / B) / vol + lam * vol
        y1 = np.log(B**2 / (S0 * K)) / vol + lam * vol
        y2 = np.log(B / S0) / vol + lam * vol

        disc = np.exp(-r * T)
        ratio = B / S0
        ratio_lam = ratio ** (2 * lam)          
        ratio_lam2 = ratio ** (2 * lam - 2)     

        A = phi * S0 * norm.cdf(phi * x1) \
            - phi * K * disc * norm.cdf(phi * x1 - phi * vol)

        Bv = phi * S0 * norm.cdf(phi * x2) \
            - phi * K * disc * norm.cdf(phi * x2 - phi * vol)

        C = phi * S0 * ratio_lam * norm.cdf(eta * y1) \
            - phi * K * disc * ratio_lam2 * norm.cdf(eta * y1 - eta * vol)

        D = phi * S0 * ratio_lam * norm.cdf(eta * y2) \
            - phi * K * disc * ratio_lam2 * norm.cdf(eta * y2 - eta * vol)

        E = rebate * disc * (norm.cdf(eta * x2 - eta * vol)
                             - ratio_lam2 * norm.cdf(eta * y2 - eta * vol))

        match name:
            case "CallDownIn":
                price = C + E if K >= B else A - Bv + D + E
            case "CallDownOut":
                price = A - C if K >= B else Bv - D
            case "CallUpIn":
                price = A + E if K >= B else Bv - C + D + E
            case "CallUpOut":
                price = 0.0 if K >= B else A - Bv + C - D
            case "PutDownIn":
                price = Bv - C + D + E if K >= B else A + E
            case "PutDownOut":
                price = A - Bv + C - D if K >= B else 0.0
            case "PutUpIn":
                price = A - Bv + D + E if K >= B else C + E
            case "PutUpOut":
                price = Bv - D if K >= B else A - C
            case _:
                raise ValueError(f"Unknown barrier product: {name}")

        return price

    def price(self, product, model, S0: float, T: float, r: float) -> PricingResult:
        if model.name() != "BlackScholes":
            raise ValueError(f"Analytical method only supports BlackScholes, got {model.name()}")
        if product.exercise_type() != "european":
            raise ValueError(f"Analytical method only supports European options, got {product.exercise_type()}")

        sigma = model.sigma

        match product.option_type():
            case "call" | "put":
                price, d1, d2 = self._price_vanilla(product, S0, T, r, sigma)
                metadata = {
                    "method": "Analytical",
                    "model": "BlackScholes",
                    "d1": d1,
                    "d2": d2,
                }
            case "digital":
                price, d2 = self._price_digital(product, S0, T, r, sigma)
                metadata = {
                    "method": "Analytical",
                    "model": "BlackScholes",
                    "d2": d2,
                    "payout": product.Q,
                }
            case "barrier":
                price = self._price_barrier(product, S0, T, r, sigma)
                metadata = {
                    "method": "Analytical",
                    "model": "BlackScholes",
                    "strike": product.K,
                    "barrier": product.B,
                }
            case _:
                raise ValueError(f"Analytical does not support {product.option_type()} products.")

        return PricingResult(price=price, metadata=metadata)

    @classmethod
    def name(cls) -> str:
        return "Analytical"

    @classmethod
    def parameter_info(cls) -> dict:
        return {}