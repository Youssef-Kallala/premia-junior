from ..models.base import BaseModel 
from ..methods.base import BaseMethod 
from ..products.base import BaseProduct  


class Pricer:
    def __init__(self, model: BaseModel, method: BaseMethod, product: BaseProduct):
        self.model = model
        self.method = method
        self.product = product
        self._check_compatibility(model, method, product)

    def price(self, S0, T, r):
        return self.method.price(self.product,self.model,S0, T, r)

    def _check_compatibility(self, model, method, product):
        if method.name() not in model.compatible_methods:
            raise ValueError(
                f"{method.name()} is not compatible with {model.name()}.\n"
                f"Allowed methods: {model.compatible_methods}"
            )
        if hasattr(method, 'compatible_exercise_types'):
            if product.exercise_type() not in method.compatible_exercise_types:
                raise ValueError(
                    f"{method.name()} does not support {product.exercise_type()} options.\n"
                    f"Allowed exercise types: {method.compatible_exercise_types}"
            )
