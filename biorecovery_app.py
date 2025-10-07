import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Mock recovery functions for 3 bacteria (replace with real models or data if available)
# Inputs: pH (1-7), temperature (20-60°C), oxygen (0-10 mg/L)
def recovery_acidithiobacillus_ferrooxidans(pH, temp, oxygen):
    # Just for demonstration, real function should be based on experimental data
    return max(0, min(1, 0.8 - 0.1 * abs(pH-2) + 0.01 * (temp-30) + 0.03 * oxygen))

def recovery_leptospirillum_ferrooxidans(pH, temp, oxygen):
    return max(0, min(1, 0.7 - 0.08 * abs(pH-2.5) + 0.012 * (temp-35) + 0.025 * oxygen))

def recovery_acidithiobacillus_thiooxidans(pH, temp, oxygen):
    return max(0, min(1, 0.6 - 0.09 * abs(pH-1.5) + 0.015 * (temp-25) + 0.02 * oxygen))

# -----------------------------
# Streamlit App UI
# -----------------------------
st.title("Bioleaching Metal Recovery Simulation")
st.markdown("""
Interactively explore how **pH**, **temperature**, and **oxygen** affect metal recovery for three key bacteria in bioleaching.

- **Bacteria:**
    - *Acidithiobacillus ferrooxidans*
    - *Leptospirillum ferrooxidans*
    - *Acidithiobacillus thiooxidans*
""")

st.sidebar.header("Bioleaching Parameters")
pH = st.sidebar.slider("pH", 1.0, 7.0, 2.0, 0.1)
temperature = st.sidebar.slider("Temperature (°C)", 20, 60, 30, 1)
oxygen = st.sidebar.slider("Oxygen (mg/L)", 0.0, 10.0, 3.0, 0.1)

# Calculate recoveries
recoveries = {
    "Acidithiobacillus ferrooxidans": recovery_acidithiobacillus_ferrooxidans(pH, temperature, oxygen),
    "Leptospirillum ferrooxidans": recovery_leptospirillum_ferrooxidans(pH, temperature, oxygen),
    "Acidithiobacillus thiooxidans": recovery_acidithiobacillus_thiooxidans(pH, temperature, oxygen)
}

# Convert to DataFrame for plotting
df = pd.DataFrame({
    "Bacteria": list(recoveries.keys()),
    "Recovery (%)": [100*v for v in recoveries.values()]
})

# Plot
st.subheader("Metal Recovery by Bacteria (at selected conditions)")
fig, ax = plt.subplots()
bars = ax.bar(df["Bacteria"], df["Recovery (%)"], color=["#8dd3c7", "#bebada", "#fb8072"])
ax.set_ylim(0, 100)
ax.set_ylabel("Recovery (%)")

# FIXED: Rotate x-labels to avoid overlap
ax.set_xticks(range(len(df["Bacteria"])))
ax.set_xticklabels(df["Bacteria"], rotation=20, ha="right", fontsize=10)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f"{height:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
st.pyplot(fig)

st.info(f"**Selected Parameters:**  pH={pH}, Temperature={temperature}°C, Oxygen={oxygen} mg/L")

st.markdown(
"""
---
*You can replace the mock recovery functions in the code with your experimental or literature-based models for more accurate predictions.*
"""
)
