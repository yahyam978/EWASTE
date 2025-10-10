# ... previous code unchanged ...

st.markdown("---")
st.subheader("📊 Optimum Conditions Summary (from model)")

opt_data = []
for org, p in organisms.items():
    for metal, max_r in p["recovery_max"].items():
        opt_data.append({
            "Bacteria": org,
            "Metal": metal,
            "Optimum pH": p["pH_opt"],
            "Optimum Temp (°C)": p["T_opt"],
            "O₂ Half-sat (K_O)": p["K_O"],
            "Max Recovery (%)": max_r * 100
        })

opt_df = pd.DataFrame(opt_data)

# Format numeric columns to 2 decimal places as strings for display
show_df = opt_df.copy()
for col in ["Optimum pH", "Optimum Temp (°C)", "O₂ Half-sat (K_O)", "Max Recovery (%)"]:
    show_df[col] = show_df[col].map("{:.2f}".format)

st.dataframe(show_df, use_container_width=True)

st.markdown("---")
st.markdown("🔍 Use the QR code (sidebar) to access the **References & Data PDF** which lists all citations and the dataset.")
