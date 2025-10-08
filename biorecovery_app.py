import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import exp
from io import BytesIO
import qrcode
from PIL import Image

st.set_page_config(layout="wide", page_title="Bioleaching Recovery Simulator")

# ---------- Load data ----------
@st.cache_data
def load_params():
    # make sure ewaste_parameters.xlsx is in same folder
    df = pd.read_excel("ewaste_parameters.xlsx")
    return df

params_df = load_params()

# ---------- QR Code for references PDF ----------
PDF_URL = "https://raw.githubusercontent.com/YourUsername/EWASTE/main/references_and_data.pdf"
qr = qrcode.make(PDF_URL)
buf = BytesIO()
qr.save(buf, format="PNG")
qr_img = Image.open(buf)

st.sidebar.image(qr_img, caption="📄 References & Data", width=150)

# ---------- Page title ----------
st.title("Bioleaching Metal Recovery Simulator")
st.markdown("Explore how pH, temperature, and oxygen affect predicted metal recovery for different bacteria.")

# ---------- Organism parameters (from literature) ----------
organisms = {
    "Acidithiobacillus ferrooxidans": {
        "pH_opt": 2.0, "pH_sigma": 0.7,
        "T_opt": 30.0, "T_sigma": 6.0,
        "K_O": 0.5,
        "recovery_max": {"Cu": 0.85, "Au": 0.50, "Pd": 0.35}
    },
    "Leptospirillum spp.": {
        "pH_opt": 1.5, "pH_sigma": 0.6,
        "T_opt": 40.0, "T_sigma": 6.0,
        "K_O": 0.6,
        "recovery_max": {"Cu": 0.80, "Au": 0.40, "Pd": 0.30}
    },
    "Acidithiobacillus thiooxidans": {
        "pH_opt": 1.8, "pH_sigma": 0.6,
        "T_opt": 28.0, "T_sigma": 6.0,
        "K_O": 0.6,
        "recovery_max": {"Cu": 0.82, "Au": 0.35, "Pd": 0.28}
    }
}

# ---------- Helper functions ----------
def gauss_factor(x, x_opt, sigma):
    if sigma <= 0:
        return 0.0
    return float(np.exp(-0.5 * ((x - x_opt) / sigma)**2))

def monod_factor(O, K):
    if O < 0:
        O = 0.0
    return float(O / (K + O))

def recovery_fraction(org, pH, T, O, metal):
    p = organisms[org]
    f_pH = gauss_factor(pH, p["pH_opt"], p["pH_sigma"])
    f_T = gauss_factor(T, p["T_opt"], p["T_sigma"])
    f_O = monod_factor(O, p["K_O"])
    base = p["recovery_max"].get(metal, 0.0)
    combined = base * f_pH * f_T * (0.6 + 0.4 * f_O)
    return max(0.0, min(1.0, combined))

# ---------- Sidebar inputs ----------
st.sidebar.header("Operating Conditions")
pH = st.sidebar.slider("pH", 0.5, 4.0, 2.0, 0.1)
temperature = st.sidebar.slider("Temperature (°C)", 15, 50, 30, 1)
oxygen = st.sidebar.slider("Dissolved O₂ (mg/L)", 0.0, 10.0, 3.0, 0.1)

st.sidebar.markdown("**Select metal to analyze**")
metal_choice = st.sidebar.selectbox("Metal", ["Cu", "Au", "Pd"])

st.markdown(f"### Conditions: pH = **{pH:.2f}**, Temperature = **{temperature} °C**, DO = **{oxygen:.2f} mg/L**")
st.markdown(f"Predicted {metal_choice} recovery by species:")

# ---------- Calculate recoveries ----------
records = []
for org in organisms.keys():
    rec = recovery_fraction(org, pH, temperature, oxygen, metal_choice)
    records.append({"Bacteria": org, "Recovery (%)": rec * 100})

df_out = pd.DataFrame(records).set_index("Bacteria")

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(8,4))
vals = df_out["Recovery (%)"]
bars = ax.bar(vals.index, vals.values, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
ax.set_ylim(0, 100)
ax.set_ylabel("Recovery (%)")
ax.set_title(f"{metal_choice} Recovery by Bacteria")

for bar in bars:
    h = bar.get_height()
    ax.annotate(f"{h:.1f}%", xy=(bar.get_x()+bar.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points",
                ha="center", va="bottom")

plt.xticks(rotation=15, ha="right")
st.pyplot(fig)

# ---------- Numeric table ----------
st.subheader("Numeric Results")
st.table(df_out.style.format("{:.2f}"))

st.markdown("---")
st.markdown("🔍 Use the QR code (sidebar) to access the **References & Data PDF** which lists all citations and the dataset.")
