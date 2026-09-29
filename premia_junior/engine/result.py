from dataclasses import dataclass , field 

@dataclass 
class PricingResult : 
    price : float
    confidence_interval : tuple | None= None 
    metadata : dict=field(default_factory=dict)
    