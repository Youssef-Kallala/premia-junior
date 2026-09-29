import sys
sys.path.insert(0, '../..')

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from premia_junior.registry import MODEL_REGISTRY, METHOD_REGISTRY, PRODUCT_REGISTRY
from premia_junior.engine.pricer import Pricer

import premia_junior.models
import premia_junior.methods
import premia_junior.products

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Compare Methods — Premia Junior", layout="wide")
st.title("Compare Methods")
st.caption("Price the same option with multiple numerical methods and compare results side by side.")

# ── Sidebar — model, product, market params ───────────────────────────────────
st.sidebar.header("Configuration")

# Model
model_name = st.sidebar.selectbox("Model", list(MODEL_REGISTRY.keys()))
ModelClass  = MODEL_REGISTRY[model_name]

st.sidebar.subheader(f"{model_name} parameters")
model_params = {}
for param, info in ModelClass.parameter_info().items():
    model_params[param] = st.sidebar.number_input(
        param,
        min_value=float(info["min"]),
        max_value=float(info["max"]),
        value=float(info["default"]),
        step=float(info["step"]),
        key=f"model_{param}",
    )

# Product
product_name = st.sidebar.selectbox("Product", list(PRODUCT_REGISTRY.keys()))
ProductClass  = PRODUCT_REGISTRY[product_name]

st.sidebar.subheader(f"{product_name} parameters")
product_params = {}
for param, info in ProductClass.parameter_info().items():
    product_params[param] = st.sidebar.number_input(
        param,
        min_value=float(info["min"]),
        max_value=float(info["max"]),
        value=float(info["default"]),
        step=float(info["step"]),
        key=f"product_{param}",
    )

# Market
st.sidebar.subheader("Market parameters")
S0 = st.sidebar.number_input("S0 — initial price",  value=100.0, step=1.0)
T  = st.sidebar.number_input("T — time horizon",    value=1.0,   step=0.1)
r  = st.sidebar.number_input("r — risk-free rate",  value=0.05,  step=0.01)

# ── Main area — method selector ───────────────────────────────────────────────
st.subheader("Select methods to compare")

all_method_names = list(METHOD_REGISTRY.keys())
selected_methods = st.multiselect(
    "Methods",
    all_method_names,
    default=all_method_names,
)

# ── Per-method parameter inputs in columns ────────────────────────────────────
method_params_all = {}

if selected_methods:
    st.subheader("Method parameters")
    cols = st.columns(len(selected_methods))

    for col, mname in zip(cols, selected_methods):
        MClass = METHOD_REGISTRY[mname]
        params = {}
        with col:
            st.markdown(f"**{mname}**")
            info_dict = MClass.parameter_info()
            if info_dict:
                for param, info in info_dict.items():
                    params[param] = st.number_input(
                        param,
                        min_value=float(info["min"]),
                        max_value=float(info["max"]),
                        value=float(info["default"]),
                        step=float(info["step"]),
                        key=f"method_{mname}_{param}",
                    )
            else:
                st.caption("No parameters needed.")
        method_params_all[mname] = params

# ── Compare button ────────────────────────────────────────────────────────────
st.divider()

if st.button("Compare", type="primary", disabled=not selected_methods):

    model   = ModelClass(**model_params)
    product = ProductClass(**product_params)

    rows = []
    errors = []

    for mname in selected_methods:
        MClass = METHOD_REGISTRY[mname]
        try:
            # cast int params (n_paths, n_steps) back to int
            raw = method_params_all[mname]
            cast = {}
            for k, v in raw.items():
                cast[k] = int(v) if float(v) == int(v) else v

            method = MClass(**cast)
            pricer = Pricer(model=model, method=method, product=product)
            result = pricer.price(S0=S0, T=T, r=r)

            ci = "—"
            if result.confidence_interval:
                lo, hi = result.confidence_interval
                ci = f"[{lo:.4f}, {hi:.4f}]"

            rows.append({
                "Method":              mname,
                "Price":               f"{result.price:.6f}",
                "95% CI":              ci,
            })
        except Exception as e:
            errors.append(f"**{mname}**: {e}")

    # ── Results table ─────────────────────────────────────────────────────────
    if rows:
        st.subheader("Results")
        df = pd.DataFrame(rows).set_index("Method")
        st.dataframe(df, use_container_width=True)

        # ── Bar chart of prices ───────────────────────────────────────────────
        prices = {r["Method"]: float(r["Price"]) for r in rows}
        if len(prices) > 1:
            st.subheader("Price comparison")
            fig, ax = plt.subplots(figsize=(max(4, len(prices) * 2), 4))
            bars = ax.bar(prices.keys(), prices.values(), color="#6c63ff", alpha=0.85, width=0.5)
            ax.bar_label(bars, fmt="%.4f", padding=4, fontsize=10)
            ax.set_ylabel("Price")
            ax.set_title(f"{model_name} · {product_name} · S0={S0} K={product_params.get('K','?')} T={T} r={r}")
            ax.set_ylim(0, max(prices.values()) * 1.2)
            ax.spines[["top", "right"]].set_visible(False)
            st.pyplot(fig)

    if errors:
        st.subheader("Errors")
        for e in errors:
            st.error(e)

elif not selected_methods:
    st.info("Select at least one method above to compare.")