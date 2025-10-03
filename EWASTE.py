import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import qrcode
from io import BytesIO

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# QR Code Generation
# -----------------------------
# IMPORTANT: Replace this with the raw URL to your PDF file on GitHub
# Example: "https://github.com/YOUR_USERNAME/YOUR_REPO/raw/main/references_and_data.pdf"
PDF_URL = "https://github.com/yahyam978/EWASTE/raw/main/references_and_data.pdf"

def generate_qr_code_in_memory(url):
    """Generates a QR code image and returns it as a byte stream."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to a bytes buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# -----------------------------
# Load Parameters from CSV
# -----------------------------
try:
    # Read data from the CSV file
    data = pd.read_csv("ewaste_parameters.csv", index_col=0)
except FileNotFoundError:
    st.error("Error: `ewaste_parameters.csv` not found. Please make sure the data file is in the same directory.")
    st.stop()

# -----------------------------
# User Editable Parameters (Sidebar)
# -----------------------------
st.sidebar.header("⚙️ Adjust Parameters")
editable_data = data.copy()

for method in data.index:
    st.sidebar.subheader(method)
    editable_data.loc[method, "Energy_kWh_per_t"] = st.sidebar.number_input(
        f"Energy (kWh/t) for {method}",
        value=float(data.loc[method, "Energy_kWh_per_t"]),
        min_value=0.0,
        key=f"energy_{method}"
    )
    editable_data.loc[method, "Chemicals_cost_per_t"] = st.sidebar.number_input(
        f"Chemicals ($/t) for {method}",
        value=float(data.loc[method, "Chemicals_cost_per_t"]),
        min_value=0.0,
        key=f"chemicals_{method}"
    )
    editable_data.loc[method, "Capex_per_t"] = st.sidebar.number_input(
        f"Capex ($/t) for {method}",
        value=float(data.loc[method, "Capex_per_t"]),
        min_value=0.0,
        key=f"capex_{method}"
    )
    editable_data.loc[method, "Au_recovery"] = st.sidebar.slider(
        f"Au Recovery for {method}", 0.0, 1.0, float(data.loc[method, "Au_recovery"]), key=f"au_{method}"
    )
    editable_data.loc[method, "Pd_recovery"] = st.sidebar.slider(
        f"Pd Recovery for {method}", 0.0, 1.0, float(data.loc[method, "Pd_recovery"]), key=f"pd_{method}"
    )
    editable_data.loc[method, "Cu_recovery"] = st.sidebar.slider(
        f"Cu Recovery for {method}", 0.0, 1.0, float(data.loc[method, "Cu_recovery"]), key=f"cu_{method}"
    )

# -----------------------------
# Evaluation Function
# -----------------------------
def evaluate_method(name, energy, chemicals_cost, capex, recovery):
    """Calculates costs and formats the results for a given method."""
    energy_cost = energy * 0.1  # assume $0.1 per kWh
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
for method in editable_data.index:
    recovery_rates = {
        "Au": editable_data.loc[method, "Au_recovery"],
        "Pd": editable_data.loc[method, "Pd_recovery"],
        "Cu": editable_data.loc[method, "Cu_recovery"]
    }
    results.append(
        evaluate_method(
            method,
            editable_data.loc[method, "Energy_kWh_per_t"],
            editable_data.loc[method, "Chemicals_cost_per_t"],
            editable_data.loc[method, "Capex_per_t"],
            recovery_rates
        )
    )

results_df = pd.DataFrame(results).set_index("Method")

# -----------------------------
# Streamlit UI Layout
# -----------------------------
# Main layout with two columns: one for content, one for the QR code
main_col, qr_col = st.columns([4, 1])

with main_col:
    st.title("E-waste: Cost & Energy Comparison — Pyro vs Hydro vs Bio vs Informal (Egypt)")
    st.markdown("Compare energy use, cost breakdown, and metal yield for Au, Pd, Cu using different recycling methods.")

with qr_col:
    st.write("") # Spacer
    qr_code_image = generate_qr_code_in_memory(PDF_URL)
    st.image(qr_code_image, width=150)
    st.caption("📄 References & Data (scan QR code)")

st.header("📊 Simulation Outputs")
# Highlight the minimum value in each column with a light yellow color ('khaki')
st.dataframe(results_df.style.highlight_min(color="khaki", axis=0))

st.success("✅ Adjust parameters in the sidebar to see the real-time impact on costs and recoveries.")

# --- Charts in a 2x2 Grid Layout ---
st.header("📈 Visualizations")
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Energy Consumption (kWh per ton)")
    fig, ax = plt.subplots(figsize=(5, 4))
    results_df["Energy (kWh/t)"].plot(kind="bar", ax=ax, color="orange")
    plt.ylabel("kWh per ton")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("💰 Total Cost ($ per ton)")
    fig, ax = plt.subplots(figsize=(5, 4))
    results_df["Total cost ($/t)"].plot(kind="bar", ax=ax, color="#4682B4") # SteelBlue
    plt.ylabel("Cost ($/t)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    st.subheader("🏅 Metal Recovery (Au)")
    fig, ax = plt.subplots(figsize=(5, 4))
    results_df["Au recovery"].plot(kind="bar", ax=ax, color="gold")
    ax.set_ylim(0, 1.0)
    plt.ylabel("Recovery efficiency")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

with col4:
    st.subheader("🥈 Metal Recovery (Pd & Cu)")
    fig, ax = plt.subplots(figsize=(5, 4))
    results_df[["Pd recovery", "Cu recovery"]].plot(kind="bar", ax=ax)
    ax.set_ylim(0, 1.0)
    plt.ylabel("Recovery efficiency")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
