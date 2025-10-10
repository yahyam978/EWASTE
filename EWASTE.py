import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import io

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

# --- Fixed QR code for References & Data in corner ---

pdf_url = "https://github.com/yahyam978/EWASTE/raw/main/references_and_data.pdf"
qr_img = qrcode.make(pdf_url)
buf = io.BytesIO()
qr_img.save(buf, format="PNG")
buf.seek(0)

# Custom HTML/CSS for fixed corner QR
st.markdown(
    """
    <style>
    .corner-qr {
        position: fixed;
        top: 25px;
        right: 30px;
        z-index: 9999;
        text-align: center;
    }
    .corner-qr img {
        width: 100px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .corner-qr-label {
        font-size: 12px;
        margin-top: -2px;
        color: #555;
        background: #fff9;
        border-radius: 6px;
        padding: 2px 6px;
        display: inline-block;
    }
    </style>
    <div class="corner-qr">
        <img src="data:image/png;base64,{qr_b64}" alt="References QR">
        <div class="corner-qr-label">References & Data PDF</div>
    </div>
    """.format(qr_b64=Image.open(buf).tobytes().hex()),
    unsafe_allow_html=True
)

st.header("📊 Simulation Outputs")

# -- Rest of your code stays unchanged --
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
