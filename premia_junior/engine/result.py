from dataclasses import dataclass, field
import numpy as np


@dataclass
class PricingResult:
    price: float
    confidence_interval: tuple | None = None
    metadata: dict = field(default_factory=dict)
    samples: np.ndarray | None = field(default=None, repr=False)
