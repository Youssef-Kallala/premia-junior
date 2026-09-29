MODEL_REGISTRY={}
METHOD_REGISTRY={}
PRODUCT_REGISTRY={}

def register_model(Model):
    MODEL_REGISTRY[Model.name()]=Model
    return Model 
def register_method(Method):
    METHOD_REGISTRY[Method.name()]=Method
    return Method 
def register_product(Product):
    PRODUCT_REGISTRY[Product.name()]=Product
    return Product 