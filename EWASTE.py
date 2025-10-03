"""
ewaste_method_comparison_app.py
Streamlit app to compare Pyro, Hydro, Bio, and Informal Egyptian methods
for recovery of Au, Pd, Cu from e-waste (per 1 tonne feed or user-specified feed).

Run: streamlit run ewaste_method_comparison_app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="E-waste Recovery Method Comparison", layout="wide")

st.title("E-waste: Cost & Energy Comparison — Pyro vs Hydro vs Bio vs Informal (Egypt)")
st.markdown(
    "Compare energy use, cost breakdown, and metal yield for Au, Pd, Cu "
    "using different recycling methods. Replace placeholder parameters with lab/local values."
)

# -------------------------
# Sidebar input parameters
# -------------------------
st.sidebar.header("Simulation Inputs")

# Feed specification
feed_tonnes = st.sidebar.number_input("E-waste feed (tonnes)", value=1.0, min_value=0.1, step=0.1)
st.sidebar.markdown("**Metal composition in feed (fraction by mass)** — change to match your sample assays")
au_frac = st.sidebar.number_input("Au fraction (kg Au per tonne -> fraction)", value=0.0005, format="%.6f")  # e.g., 0.0005 -> 0.5 kg/tonne
pd_frac = st.sidebar.number_input("Pd fraction (fraction)", value=0.0002, format="%.6f")  # e.g., 0.0002 -> 0.2 kg/tonne
cu_frac = st.sidebar.number_input("Cu fraction (fraction)", value=0.20, format="%.6f")  # e.g., 0.20 -> 200 kg/tonne

# Electricity & economic inputs
st.sidebar.subheader("Economic parameters (localize these!)")
energy_cost = st.sidebar.number_input("Electricity cost ($ per kWh)", value=0.06, format="%.4f")
labor_cost_per_tonne = st.sidebar.number_input("Labor cost ($ per tonne)", value=50.0)
env_cost_proxy = st.sidebar.number_input("Environmental cost proxy ($ per tonne processed)", value=20.0)
currency = st.sidebar.selectbox("Currency label (display)", ["USD", "EGP"], index=0)

# CAPEX amortization assumptions
st.sidebar.subheader("CAPEX amortization")
capex_per_tonne_pyro = st.sidebar.number_input("Pyro CAPEX amortized ($/tonne)", value=200.0)
capex_per_tonne_hydro = st.sidebar.number_input("Hydro CAPEX amortized ($/tonne)", value=150.0)
capex_per_tonne_bio = st.sidebar.number_input("Bio CAPEX amortized ($/tonne)", value=50.0)
capex_per_tonne_informal = st.sidebar.number_input("Informal CAPEX amortized ($/tonne)", value=10.0)

# Method baseline placeholders (editable)
st.sidebar.subheader("Method baseline parameters (edit!)")
# Pyro (placeholders)
pyro_energy_kwh_per_t = st.sidebar.number_input("Pyro energy (kWh per tonne)", value=1500.0)
pyro_chemicals_cost_per_t = st.sidebar.number_input("Pyro chemicals & fluxes ($/tonne)", value=30.0)
pyro_recovery = {
    "Au": st.sidebar.number_input("Pyro recovery % Au", value=95.0, min_value=0.0, max_value=100.0)/100.0,
    "Pd": st.sidebar.number_input("Pyro recovery % Pd", value=90.0, min_value=0.0, max_value=100.0)/100.0,
    "Cu": st.sidebar.number_input("Pyro recovery % Cu", value=95.0, min_value=0.0, max_value=100.0)/100.0,
}

# Hydro (placeholders)
hydro_energy_kwh_per_t = st.sidebar.number_input("Hydro energy (kWh per tonne)", value=300.0)
hydro_chemicals_cost_per_t = st.sidebar.number_input("Hydro chemicals ($/tonne)", value=300.0)
hydro_recovery = {
    "Au": st.sidebar.number_input("Hydro recovery % Au", value=98.0, min_value=0.0, max_value=100.0)/100.0,
    "Pd": st.sidebar.number_input("Hydro recovery % Pd", value=95.0, min_value=0.0, max_value=100.0)/100.0,
    "Cu": st.sidebar.number_input("Hydro recovery % Cu", value=98.0, min_value=0.0, max_value=100.0)/100.0,
}

# Bio (placeholders / microbes)
st.sidebar.subheader("Bio parameters & microbes")
bio_energy_kwh_per_t_base = st.sidebar.number_input("Bio energy baseline (kWh per tonne)", value=50.0)
bio_base_chemicals_cost_per_t = st.sidebar.number_input("Bio reagents & nutrients ($/tonne)", value=30.0)

microbe_choice = st.sidebar.selectbox("Choose microorganism for Bioleaching", 
                                      ["A. ferrooxidans", "A. thiooxidans", "Leptospirillum", "Consortium"])
# default recovery per microbe - placeholders (editable)
if microbe_choice == "A. ferrooxidans":
    bio_recovery = {"Au": 0.40, "Pd": 0.30, "Cu": 0.85}  # placeholders
    microbe_cost_factor = 1.0
elif microbe_choice == "A. thiooxidans":
    bio_recovery = {"Au": 0.30, "Pd": 0.25, "Cu": 0.80}
    microbe_cost_factor = 0.9
elif microbe_choice == "Leptospirillum":
    bio_recovery = {"Au": 0.35, "Pd": 0.28, "Cu": 0.82}
    microbe_cost_factor = 1.1
else:  # Consortium
    bio_recovery = {"Au": 0.55, "Pd": 0.40, "Cu": 0.90}
    microbe_cost_factor = 1.4

# Allow editing recovery values for bio
st.sidebar.markdown("**Adjust bio recovery rates (editable)**")
bio_recovery["Au"] = st.sidebar.number_input("Bio recovery % Au", value=float(bio_recovery["Au"]*100.0), min_value=0.0, max_value=100.0)/100.0
bio_recovery["Pd"] = st.sidebar.number_input("Bio recovery % Pd", value=float(bio_recovery["Pd"]*100.0), min_value=0.0, max_value=100.0)/100.0
bio_recovery["Cu"] = st.sidebar.number_input("Bio recovery % Cu", value=float(bio_recovery["Cu"]*100.0), min_value=0.0, max_value=100.0)/100.0

# Informal Egyptian method (placeholders)
st.sidebar.subheader("Informal (Egypt) baseline — user must localize")
informal_energy_kwh_per_t = st.sidebar.number_input("Informal energy (kWh per tonne)", value=10.0)
informal_chem_cost_per_t = st.sidebar.number_input("Informal chemical cost ($/tonne) — acid baths etc.", value=5.0)
informal_recovery = {
    "Au": st.sidebar.number_input("Informal recovery % Au", value=20.0, min_value=0.0, max_value=100.0)/100.0,
    "Pd": st.sidebar.number_input("Informal recovery % Pd", value=15.0, min_value=0.0, max_value=100.0)/100.0,
    "Cu": st.sidebar.number_input("Informal recovery % Cu", value=50.0, min_value=0.0, max_value=100.0)/100.0,
}

# Microbial condition costs breakdown (estimates modifiable)
st.sidebar.subheader("Bio condition costs (per tonne) — editable")
bio_aeration_energy_per_t = st.sidebar.number_input("Aeration energy (kWh/tonne)", value=30.0)
bio_pH_control_cost_per_t = st.sidebar.number_input("pH control chemicals ($/tonne)", value=20.0)
bio_culture_cost_per_t = st.sidebar.number_input("Microbial culture cost & maintenance ($/tonne)", value=15.0) * microbe_cost_factor

# Allow overriding bio energy
bio_energy_kwh_per_t = st.sidebar.number_input("Total Bio energy (kWh per tonne)", value=bio_energy_kwh_per_t_base + bio_aeration_energy_per_t)

# Output currency formatting
def fmt(x):
    return f"{x:,.2f} {currency}"

# -------------
# Calculations
# -------------
st.header("Simulation Outputs")

# feed metal mass (kg) per tonne feed
feed_kg = feed_tonnes * 1000.0
au_mass_kg = feed_kg * au_frac
pd_mass_kg = feed_kg * pd_frac
cu_mass_kg = feed_kg * cu_frac * 1000.0/1000.0  # already kg

# Create function to compute cost-energy for a method
def evaluate_method(name, energy_kwh_per_t, chem_cost_per_t, recovery_dict, capex_per_t):
    # metal recovered (kg)
    au_rec_kg = au_mass_kg * recovery_dict["Au"]
    pd_rec_kg = pd_mass_kg * recovery_dict["Pd"]
    cu_rec_kg = cu_mass_kg * recovery_dict["Cu"]
    # energy cost
    energy_cost_total = energy_kwh_per_t * energy_cost
    # base operating cost
    op_cost = energy_cost_total + chem_cost_per_t + labor_cost_per_t + env_cost_proxy
    total_cost_per_t = op_cost + capex_per_t
    # cost per kg metal (distribute cost to metals by recovered mass)
    total_recovered_mass_kg = (au_rec_kg + pd_rec_kg + cu_rec_kg)
    if total_recovered_mass_kg > 0:
        cost_per_kg_mixture = total_cost_per_t / total_recovered_mass_kg
    else:
        cost_per_kg_mixture = np.nan
    # cost per metal (if recovered mass > 0)
    cost_per_kg = {}
    for k, val in [("Au", au_rec_kg), ("Pd", pd_rec_kg), ("Cu", cu_rec_kg)]:
        cost_per_kg[k] = (total_cost_per_t * (val/total_recovered_mass_kg)) / val if val>0 and total_recovered_mass_kg>0 else np.nan
    return dict(
        name=name,
        energy_kwh_per_t=energy_kwh_per_t,
        energy_cost_total=energy_cost_total,
        chem_cost_per_t=chem_cost_per_t,
        op_cost=op_cost,
        capex_per_t=capex_per_t,
        total_cost_per_t=total_cost_per_t,
        au_rec_kg=au_rec_kg,
        pd_rec_kg=pd_rec_kg,
        cu_rec_kg=cu_rec_kg,
        total_recovered_mass_kg=total_recovered_mass_kg,
        cost_per_kg=cost_per_kg,
        cost_per_kg_mixture=cost_per_kg_mixture
    )

# Evaluate methods
pyro = evaluate_method("Pyrometallurgy", pyro_energy_kwh_per_t, pyro_chemicals_cost_per_t, pyro_recovery, capex_per_t=capex_per_t_pyro)
hydro = evaluate_method("Hydrometallurgy", hydro_energy_kwh_per_t, hydro_chemicals_cost_per_t, hydro_recovery, capex_per_t=capex_per_t_hydro)
bio = evaluate_method("Bioleaching ("+microbe_choice+")", bio_energy_kwh_per_t, bio_base_chemicals_cost_per_t + bio_pH_control_cost_per_t + bio_culture_cost_per_t, bio_recovery, capex_per_t=bio_per_t if (bio_per_t:=capex_per_t_bio) else capex_per_t_bio)
informal = evaluate_method("Informal (Egypt)", informal_energy_kwh_per_t, informal_chem_cost_per_t, informal_recovery, capex_per_t=capex_per_t_informal)

methods = [pyro, hydro, bio, informal]

# Display results: table of recovered masses
rec_table = []
for m in methods:
    rec_table.append({
        "Method": m["name"],
        "Au_recovered_kg": m["au_rec_kg"],
        "Pd_recovered_kg": m["pd_rec_kg"],
        "Cu_recovered_kg": m["cu_rec_kg"],
        "Total_recovered_kg": m["total_recovered_mass_kg"],
        "Energy_kWh_per_t": m["energy_kwh_per_t"],
        "Total_cost_per_t": m["total_cost_per_t"]
    })
rec_df = pd.DataFrame(rec_table)
st.subheader("Recovered metals & total cost (per feed batch)")
st.dataframe(rec_df.style.format({
    "Au_recovered_kg":"{:.4f}",
    "Pd_recovered_kg":"{:.4f}",
    "Cu_recovered_kg":"{:.2f}",
    "Total_recovered_kg":"{:.2f}",
    "Energy_kWh_per_t":"{:.1f}",
    "Total_cost_per_t":"{:.2f}"
}))

# Cost per kg outputs table
cost_rows = []
for m in methods:
    cost_rows.append({
        "Method": m["name"],
        "Cost_per_kg_Au": m["cost_per_kg"]["Au"],
        "Cost_per_kg_Pd": m["cost_per_kg"]["Pd"],
        "Cost_per_kg_Cu": m["cost_per_kg"]["Cu"],
        "Cost_per_kg_mixture": m["cost_per_kg_mixture"]
    })
cost_df = pd.DataFrame(cost_rows)
st.subheader("Cost per kg of recovered metal")
st.dataframe(cost_df.style.format({
    "Cost_per_kg_Au":"{:.2f}",
    "Cost_per_kg_Pd":"{:.2f}",
    "Cost_per_kg_Cu":"{:.2f}",
    "Cost_per_kg_mixture":"{:.2f}"
}))

# Charts
st.subheader("Charts")
fig, ax = plt.subplots(1,2, figsize=(12,4))
# Bar: energy per method
ax[0].bar([m["name"] for m in methods], [m["energy_kwh_per_t"] for m in methods])
ax[0].set_ylabel("Energy (kWh per tonne)")
ax[0].tick_params(axis='x', rotation=25)

# Stacked bar: recovered mass per metal per method
names = [m["name"] for m in methods]
au_vals = [m["au_rec_kg"] for m in methods]
pd_vals = [m["pd_rec_kg"] for m in methods]
cu_vals = [m["cu_rec_kg"] for m in methods]
ax[1].bar(names, cu_vals, label="Cu (kg)")
ax[1].bar(names, pd_vals, bottom=cu_vals, label="Pd (kg)")
bottoms = np.array(cu_vals)+np.array(pd_vals)
ax[1].bar(names, au_vals, bottom=bottoms, label="Au (kg)")
ax[1].set_ylabel("Recovered mass (kg)")
ax[1].tick_params(axis='x', rotation=25)
ax[1].legend()
st.pyplot(fig)

# Download results as CSV
st.subheader("Download results")
out_df = rec_df.merge(cost_df, on="Method")
csv_bytes = out_df.to_csv(index=False).encode()
st.download_button("Download CSV of results", csv_bytes, file_name="method_comparison_results.csv", mime="text/csv")

st.info("⚠️ IMPORTANT: All default numeric values are placeholders. Replace them with lab-calibrated recovery rates, local electricity prices, and CAPEX estimates for accurate results. See resource list below for where to get these numbers.")

# End of app
