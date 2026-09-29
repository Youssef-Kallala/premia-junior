import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from premia_junior.registry import MODEL_REGISTRY, METHOD_REGISTRY, PRODUCT_REGISTRY
from premia_junior.engine.pricer import Pricer

import premia_junior.models
import premia_junior.methods
import premia_junior.products

st.title("Premia Junior")
# Sidebar
st.sidebar.header("Configuration")
model_name = st.sidebar.selectbox(
    "Model",
    list(MODEL_REGISTRY.keys())
)
method_name = st.sidebar.selectbox(
    "Method",
    list(METHOD_REGISTRY.keys())
)
product_name = st.sidebar.selectbox(
    "Product",
    list(PRODUCT_REGISTRY.keys())
)

ModelClass = MODEL_REGISTRY[model_name]
MethodClass = METHOD_REGISTRY[method_name]
ProductClass = PRODUCT_REGISTRY[product_name]

model_params = {}
for parameter,info in ModelClass.parameter_info().items() : 
        model_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
        )

method_params = {}
for parameter,info in MethodClass.parameter_info().items() : 
        method_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
        )
        
product_params = {}
for parameter,info in ProductClass.parameter_info().items() : 
        product_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
        )


    
    
st.sidebar.subheader("Market Parameters")
S0 = st.sidebar.number_input("S0 (Initial price)", value=100.0)
T = st.sidebar.number_input("T (Time horizon)", value=1.0)
r = st.sidebar.number_input("r (Risk-free rate)", value=0.05)

if st.button("Price"):
    model = ModelClass(**model_params)
    method = MethodClass(**method_params)
    product = ProductClass(**product_params)

    try:
        pricer = Pricer(model=model, method=method, product=product)
        result = pricer.price(S0=S0, T=T, r=r)

        st.metric("Price", f"{result.price:.4f}")

        if result.confidence_interval:
            lower, upper = result.confidence_interval
            st.write(f"Confidence interval: [{lower:.4f}, {upper:.4f}]")

        with st.expander("Details"):
            for key, value in result.metadata.items():
                st.write(f"**{key}:** {value}")

        if hasattr(method, 'n_paths'):
            st.subheader("Simulated Paths")
            import matplotlib.pyplot as plt
            import numpy as np

            try:
                display_paths = model.simulate(
                    S0, r, T, method.n_steps,
                    min(50, method.n_paths), seed=42
                )
                fig, ax = plt.subplots(figsize=(10, 4))
                t_grid = np.linspace(0, T, method.n_steps + 1)
                for path in display_paths:
                    ax.plot(t_grid, path, alpha=0.3, linewidth=0.8)
                ax.axhline(
                    y=product.K, color='red',
                    linestyle='--', label=f'Strike K={product.K}'
                )
                ax.set_xlabel("Time")
                ax.set_ylabel("Asset Price")
                ax.set_title(f"{model_name} — Simulated Paths")
                ax.legend()
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Could not display paths: {e}")

    except ValueError as e:
        st.error(str(e))