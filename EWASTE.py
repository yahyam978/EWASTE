import qrcode
from io import BytesIO
from PIL import Image

# GitHub raw link to your hosted PDF
PDF_URL = "https://github.com/yahyam978/EWASTE/blob/848584bf15a13f2442a69a06561c3172fcfe93c9/references_and_data.pdf"

# Generate QR code
qr = qrcode.make(PDF_URL)
buf = BytesIO()
qr.save(buf, format="PNG")
qr_img = Image.open(buf)

# Display QR code in the top-right corner
st.sidebar.image(qr_img, caption="📄 References & Data PDF", width=150)
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
st.dataframe(results_df.style.highlight_min(color="lightgreen", axis=0))

# -----------------------------
# Charts
# -----------------------------
st.subheader("⚡ Energy Consumption (kWh per ton)")
fig, ax = plt.subplots()
results_df["Energy (kWh/t)"].plot(kind="bar", ax=ax, color="orange")
plt.ylabel("kWh per ton")
st.pyplot(fig)

st.subheader("💰 Total Cost ($ per ton)")
fig, ax = plt.subplots()
results_df["Total cost ($/t)"].plot(kind="bar", ax=ax, color="blue")
plt.ylabel("Cost ($/t)")
st.pyplot(fig)

st.subheader("🔎 Metal Recovery Comparison")
fig, ax = plt.subplots()
results_df[["Au recovery", "Pd recovery", "Cu recovery"]].plot(kind="bar", ax=ax)
plt.ylabel("Recovery efficiency")
st.pyplot(fig)

st.success("✅ Simulation completed. Adjust Excel values for sensitivity analysis.")
