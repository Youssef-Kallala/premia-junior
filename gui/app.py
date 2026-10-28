import sys
from pathlib import Path
import pandas as pd
import inspect
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1])) 
import premia_junior.products
import premia_junior.methods
import premia_junior.models
from premia_junior.utils.BaseGreekScheme import (
    CentralDifference1, ForwardDifference, BackwardDifference,
)
from premia_junior.utils.greek import FiniteDifference
from premia_junior.engine.pricer import Pricer
from premia_junior.registry import MODEL_REGISTRY, METHOD_REGISTRY, PRODUCT_REGISTRY
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


SCHEMES = {
    "Central": CentralDifference1,
    "Forward": ForwardDifference,
    "Backward": BackwardDifference,
}


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
for parameter, info in ModelClass.parameter_info().items():
    model_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
    )

method_params = {}
for parameter, info in MethodClass.parameter_info().items():
    method_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
    )

product_params = {}
for parameter, info in ProductClass.parameter_info().items():
    product_params[parameter] = st.sidebar.number_input(
        parameter,
        min_value=info["min"],
        max_value=info["max"],
        value=info["default"],
        step=info["step"],
    )


st.sidebar.subheader("Greeks")
compute_greeks = st.sidebar.checkbox("Compute Greeks (finite differences)")
if compute_greeks:
    scheme_name = st.sidebar.selectbox("Scheme", list(SCHEMES))
    h = st.sidebar.number_input(
        "Bump size h", value=0.1, min_value=1e-6, format="%.6f")


st.sidebar.subheader("Market Parameters")
S0 = st.sidebar.number_input("S0 (Initial price)", value=100.0)
T = st.sidebar.number_input("T (Time horizon)", value=1.0)
r = st.sidebar.number_input("r (Risk-free rate)", value=0.05)

st.sidebar.subheader("Randomness")
if "seed" in inspect.signature(MethodClass.__init__).parameters:
    if st.sidebar.checkbox("Fix random seed", value=True):
        method_params["seed"] = int(st.sidebar.number_input("Seed", value=42, step=1))
else:
    st.sidebar.caption(f"{method_name} is deterministic, so no seed is needed.")
        
        
if st.button("Price"):
    model = ModelClass(**model_params)
    method = MethodClass(**method_params)
    product = ProductClass(**product_params)

    if compute_greeks and getattr(method, "seed", False) is None:
        if compute_greeks and getattr(method, "seed", 0) is None:
            st.warning("No fixed seed: each bumped price uses different random numbers, "
                    "so the Greeks will be very noisy.")
        st.caption(
            "Seed fixed to 42 so every bumped price uses the same random numbers.")

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
        if compute_greeks:
            fd = FiniteDifference(SCHEMES[scheme_name](), h)
            greeks = {"Delta": fd.delta, "Gamma": fd.gamma, "Rho": fd.rho, "Theta": fd.theta}
            if hasattr(model, "sigma"):
                greeks["Vega"] = fd.vega

            st.subheader("Greeks")
            rows = []
            with st.spinner("Computing Greeks..."):
                for name, fn in greeks.items():
                    try:
                        val, se = fn(pricer, S0, T, r)
                        ci = f"[{val - 1.96*se:.5f}, {val + 1.96*se:.5f}]" if se is not None else "—"
                        rows.append({"Greek": name, "Value": f"{val:.5f}", "95% CI": ci})
                    except Exception as e:
                        rows.append({"Greek": name, "Value": "error", "95% CI": str(e)})
            st.table(pd.DataFrame(rows).set_index("Greek"))

            if not hasattr(model, "sigma"):
                st.caption("Vega is not available for this model (no sigma parameter).")
            if getattr(method, "seed", 0) is None:
                st.warning("No fixed seed: each bumped price uses different random numbers, "
                        "so the intervals above are wide on purpose.")
            if product.option_type() in ("digital", "barrier") and hasattr(method, "n_paths"):
                st.warning("Finite differences on a discontinuous payoff with Monte Carlo are unreliable.")

    except ValueError as e:
        st.error(str(e))
