import streamlit as st
import matplotlib.pyplot as plt

# Materialwerte
E = 210000  # Elastizitätsmodul [N/mm²]
sigma_zul = 172.5  # zulässige Spannung [N/mm²]

# Mastdaten (Beispiel)
mastdaten = {
    "DP22 (HEB220)": {"Ix": 80900000, "Wx": 736000},
    "DP26 (HEB260)": {"Ix": 149200000, "Wx": 1150000},
    "DPM24 (HEM240)": {"Ix": 242900000, "Wx": 1800000},
}

st.title("Maststatik-Rechner")

mast = st.selectbox("Masttyp", options=list(mastdaten.keys()))
mastlaenge = st.number_input("Mastlänge L [m]", value=10.0, min_value=1.0)
angriffshoehe = st.number_input("Angriffshöhe h [m]", value=5.2, min_value=0.1)

st.header("Lasten längs zum Gleis")
F_A1 = st.number_input("A1) ständige Lasten [kN]", value=4.0, min_value=0.0)
F_A2 = st.number_input("A2) veränderliche Lasten [kN]", value=6.0, min_value=0.0)
F_A3 = st.number_input("A3) Kombination [kN]", value=8.0, min_value=0.0)

st.header("Lasten quer zum Gleis")
F_B1 = st.number_input("B1) Einseitiger Zug [kN]", value=3.0, min_value=0.0)
F_B2 = st.number_input("B2) Symmetrische Querlast [kN]", value=2.0, min_value=0.0)

if st.button("Berechnen"):
    daten = mastdaten[mast]
    L_mm = mastlaenge * 1000
    h_mm = angriffshoehe * 1000

    lastfaelle = {
        "A1 – ständige Lasten": F_A1,
        "A2 – veränderliche Lasten": F_A2,
        "A3 – Kombination": F_A3,
        "B1 – einseitiger Zug": F_B1,
        "B2 – symmetrische Querlast": F_B2,
    }

    for titel, F_kN in lastfaelle.items():
        F = F_kN * 1000
        M = F * h_mm
        sigma = M / daten["Wx"]
        f = F * L_mm**3 / (3 * E * daten["Ix"])

        st.write(f"### Lastfall {titel}")
        st.write(f"- Biegemoment: {M/1e6:.2f} kNm")
        st.write(f"- Spannung: {sigma:.2f} N/mm² {'✅ OK' if sigma < sigma_zul else '❌ ÜBERLAST'}")
        st.write(f"- Durchbiegung Mastspitze: {f:.1f} mm")

    F_max = max(lastfaelle.values()) * 1000
    f_max = F_max * L_mm**3 / (3 * E * daten["Ix"])
    x = [0, L_mm]
    y = [0, f_max]

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(x, y, marker='o')
    ax.set_title("Maximale Durchbiegung (aus stärkstem Lastfall)")
    ax.set_xlabel("Mastlänge [mm]")
    ax.set_ylabel("Seitliche Auslenkung [mm]")
    ax.grid(True)
    st.pyplot(fig)
