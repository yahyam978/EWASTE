import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Load Parameters from Excel
# -----------------------------
data = pd.read_excel("ewaste_parameters.xlsx", index_col=0)

# -----------------------------
# Evaluation Function
# -----------------------------
def evaluate_method(name, energy, chemicals_cost, capex, recovery):
    energy_cost = energy * 0.1   # assume $0.1 per kWh
    total_cost = chemicals_cost + capex + energy_cost
    
    return {
        "Method": name,
        "Energy (kWh/t)": energy,
        "Chemicals ($/t)": chemicals_cost,
        "Capex ($/t)": capex,
        "Energy cost ($/t)": energy_cost,
        "Total cost ($/t)": total_cost,
        "Au recovery": recovery["Au"],
        "Pd recovery": recovery["Pd"],
        "Cu recovery": recovery["Cu"],
    }

# -----------------------------
# Process All Methods
# -----------------------------
results = []

for method in data.index:
    recovery = {
        "Au": data.loc[method, "Au_recovery"],
        "Pd": data.loc[method, "Pd_recovery"],
        "Cu": data.loc[method, "Cu_recovery"]
    }
    results.append(
        evaluate_method(
            method,
            data.loc[method, "Energy_kWh_per_t"],
            data.loc[method, "Chemicals_cost_per_t"],
            data.loc[method, "Capex_per_t"],
            recovery
        )
    )

results_df = pd.DataFrame(results).set_index("Method")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("E-waste: Cost & Energy Comparison — Pyro vs Hydro vs Bio vs Informal (Egypt)")
st.markdown("Compare energy use, cost breakdown, and metal yield for Au, Pd, Cu using different recycling methods.")

st.header("📊 Simulation Outputs")

# Apply styling for table
styled_df = (
    results_df
    .style
    .background_gradient(subset=["Total cost ($/t)"], cmap="Blues")
    .background_gradient(subset=["Energy (kWh/t)"], cmap="Oranges")
    .bar(subset=["Au recovery", "Pd recovery", "Cu recovery"], color='#c2f7c2')
    .set_properties(**{'font-size': '16px', 'font-weight': 'bold'}, subset=pd.IndexSlice[:, :])
    .set_table_styles([
        {'selector': 'th', 'props': [('font-size', '18px'), ('font-weight', 'bold'), ('background-color', '#f0f0f0')]}
    ])
)

st.dataframe(styled_df, height=350)

# -----------------------------
# Charts - aligned in columns
# -----------------------------
st.subheader("📊 Key Comparisons")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("⚡ **Energy Consumption**")
    fig1, ax1 = plt.subplots()
    results_df["Energy (kWh/t)"].plot(kind="bar", ax=ax1, color="orange")
    ax1.set_ylabel("kWh per ton")
    st.pyplot(fig1)

with col2:
    st.markdown("💰 **Total Cost**")
    fig2, ax2 = plt.subplots()
    results_df["Total cost ($/t)"].plot(kind="bar", ax=ax2, color="blue")
    ax2.set_ylabel("Cost ($/t)")
    st.pyplot(fig2)

with col3:
    st.markdown("🔎 **Metal Recovery**")
    fig3, ax3 = plt.subplots()
    results_df[["Au recovery", "Pd recovery", "Cu recovery"]].plot(kind="bar", ax=ax3)
    ax3.set_ylabel("Recovery efficiency")
    st.pyplot(fig3)

st.success("✅ Simulation completed. Adjust Excel values for sensitivity analysis.")
