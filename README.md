# Premia Junior

An educational Python library for derivatives pricing, inspired by Inria's **Premia** (originally written in C). Built to grow with you — every time you read a new paper, adding a new model or method costs exactly one file.

---

## What it does

Premia Junior prices financial options using a variety of models and numerical methods, all accessible through a clean Python API and an interactive Streamlit GUI.

```python
from premia_junior.models.black_scholes import BlackScholes
from premia_junior.methods.monte_carlo import MonteCarlo
from premia_junior.products.european import EuropeanCall
from premia_junior.engine.pricer import Pricer

model   = BlackScholes(mu=0.05, sigma=0.2)
method  = MonteCarlo(n_paths=100000, n_steps=252)
product = EuropeanCall(K=100)

result = Pricer(model=model, method=method, product=product).price(S0=100, T=1.0, r=0.05)
print(result.price)                  # e.g. 10.45
print(result.confidence_interval)    # e.g. (10.39, 10.51)
```

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/your-username/premia-junior.git
cd premia-junior
pip install -e .
```

---

## Run the GUI

```bash
streamlit run gui/app.py
```

The GUI has two pages:
- **Pricing** — choose a model, method and product, fill in parameters, get a price with confidence interval and path visualization
- **Compare Methods** — price the same option with multiple methods side by side

---

## What's implemented

### Models
| Model | Dynamics | Status |
|-------|----------|--------|
| Black-Scholes | GBM with constant volatility | ✓ |
| Heston | Stochastic volatility (CIR variance process) | coming soon |

### Methods
| Method | Description | European | American |
|--------|-------------|----------|----------|
| Analytical | Closed-form Black-Scholes formulas | ✓ | ✗ |
| Monte Carlo | Path simulation with confidence interval | ✓ | ✗ |
| CRR | Cox-Ross-Rubinstein binomial tree | ✓ | ✓ |
| Trinomial Tree | Kamrad-Ritchken trinomial tree | ✓ | ✓ |
| LSM | Longstaff-Schwartz regression-based MC | ✗ | ✓ |

### Products
| Product | Type | Analytical | Monte Carlo | Trees | LSM |
|---------|------|------------|-------------|-------|-----|
| EuropeanCall / EuropeanPut | Vanilla | ✓ | ✓ | ✓ | ✗ |
| AmericanCall / AmericanPut | Early exercise | ✗ | ✗ | ✓ | ✓ |
| CallUpIn/Out, CallDownIn/Out | Barrier | ✓ | ✓ | ✗ | ✗ |
| PutUpIn/Out, PutDownIn/Out | Barrier | ✓ | ✓ | ✗ | ✗ |
| DigitalCall / PutDigit | Binary | ✓ | ✓ | ✗ | ✗ |

---

## How to add a new model

This is the core design goal of the library — adding a model from a new paper should cost exactly **one new file** and **one import line**. Nothing else changes.

### Step 1 — create `premia_junior/models/your_model.py`

```python
from ..registry import register_model
from .base import BaseModel
import numpy as np

@register_model
class YourModel(BaseModel):
    compatible_methods = ["Monte Carlo"]  # which methods work with this model

    def __init__(self, param1: float, param2: float):
        self.param1 = param1
        self.param2 = param2

    def simulate(self, S0: float, r: float, T: float,
                 n_steps: int, n_paths: int, seed=None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        dt = T / n_steps
        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = S0
        # implement your SDE discretization here
        return paths

    def parameters(self) -> dict:
        return {"param1": self.param1, "param2": self.param2}

    @classmethod
    def name(cls) -> str:
        return "YourModel"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "param1": {"default": 0.5, "min": 0.0, "max": 5.0, "step": 0.01},
            "param2": {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01},
        }
```

### Step 2 — add one import line to `premia_junior/models/__init__.py`

```python
from .your_model import YourModel
```

That's it. Your model now appears automatically in:
- The GUI dropdown
- The registry (`MODEL_REGISTRY["YourModel"]`)
- The compatibility checker

### Step 3 — write one test in `tests/test_models.py`

```python
def test_your_model_simulate_shape():
    model = YourModel(param1=0.5, param2=0.1)
    paths = model.simulate(S0=100, r=0.05, T=1.0, n_steps=50, n_paths=1000)
    assert paths.shape == (1000, 51)
    assert np.allclose(paths[:, 0], 100)
```

---

## How to add a new method

Same pattern — one file, one import line.

```python
from ..registry import register_method
from .base import BaseMethod
from ..engine.result import PricingResult

@register_method
class YourMethod(BaseMethod):
    compatible_exercise_types = ["european"]
    compatible_option_types   = ["call", "put"]

    def __init__(self, your_param: int):
        self.your_param = your_param

    def price(self, product, model, S0: float, T: float, r: float) -> PricingResult:
        # implement pricing logic here
        price = 0.0
        return PricingResult(price=price, metadata={"method": "YourMethod"})

    @classmethod
    def name(cls) -> str:
        return "YourMethod"

    @classmethod
    def parameter_info(cls) -> dict:
        return {
            "your_param": {"default": 100, "min": 10, "max": 10000, "step": 10},
        }
```

Then add to `premia_junior/methods/__init__.py`:

```python
from .your_method import YourMethod
```

---

## Known issues and limitations

### 1. Single model
Only Black-Scholes is currently implemented. Heston, SABR, and local volatility models are planned. The architecture fully supports them — they just need to be written.

### 2. Barrier option analytical formula (Reiner-Rubinstein)
The closed-form barrier formulas are implemented but some edge cases (barrier at the money, very short maturities) can produce slightly inaccurate results. Monte Carlo is the recommended method for barrier options when precision matters.

### 3. LSM underpricing
LSM (Longstaff-Schwartz) is a lower bound estimator by construction — it slightly underestimates the true American option price. Use CRR or Trinomial Tree for a more accurate benchmark. Increasing `n_paths` and `n_steps` reduces the bias.

### 4. No calibration
The library does not currently support calibrating model parameters to market implied volatility surfaces. This is planned for a future version. All model parameters must be specified manually.

### 5. No Greeks
Greeks (delta, gamma, vega, theta) are not yet implemented. They are planned via finite differences in `utils/greeks.py` — a generic bump-and-reprice approach that will work with any model+method combination.

### 6. Monte Carlo for American options
Standard Monte Carlo (`MonteCarlo` method) prices American options as if they were European — it ignores early exercise. Use `LSM`, `CRR`, or `TrinomialTree` for American options.

### 7. No multi-asset support
All products assume a single underlying asset. Multi-asset products (basket options, spread options) are not yet supported.

---

## Project structure

```
premia_junior/
├── models/          ← asset dynamics (BlackScholes, ...)
├── methods/         ← numerical solvers (Analytical, MonteCarlo, CRR, ...)
├── products/        ← payoff definitions (European, American, Barrier, ...)
├── engine/          ← Pricer orchestrator + PricingResult
├── registry.py      ← auto-discovery of all classes
└── utils/           ← shared tools (greeks, plotting, regressors)

gui/
├── app.py           ← Pricing page
└── pages/
    └── 01_Compare_Methods.py

tests/
notebooks/
pyproject.toml
```

---

## Dependencies

- Python >= 3.11
- numpy
- scipy
- matplotlib
- streamlit (GUI only)

---

## License

MIT