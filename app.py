import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from PIL import Image

# Materialwerte
E = 210000  # Elastizitätsmodul [N/mm²]
sigma_zul = 172.5  # zulässige Spannung [N/mm²]

# Mastdaten
mastdaten = {
    "DP22 (HEB220)": {"Ix": 80900000, "Wx": 736000},
    "DP26 (HEB260)": {"Ix": 149200000, "Wx": 1150000},
    "DPM24 (HEM240)": {"Ix": 242900000, "Wx": 1800000},
}

# Fundament-Faktoren
fundament_faktoren = {
    "D16":    {"EK1_x": 0.20, "EK1_y": 0.20, "EK2_x": 0.25, "EK2_y": 0.25, "EK3_x": 0.29, "EK3_y": 0.29},
    "DP18":   {"EK1_x": 0.23, "EK1_y": 0.23, "EK2_x": 0.28, "EK2_y": 0.28, "EK3_x": 0.33, "EK3_y": 0.33},
    "DP20":   {"EK1_x": 0.25, "EK1_y": 0.25, "EK2_x": 0.31, "EK2_y": 0.31, "EK3_x": 0.36, "EK3_y": 0.36},
    "DP22":   {"EK1_x": 0.28, "EK1_y": 0.28, "EK2_x": 0.34, "EK2_y": 0.34, "EK3_x": 0.40, "EK3_y": 0.40},
    "DP24":   {"EK1_x": 0.30, "EK1_y": 0.30, "EK2_x": 0.37, "EK2_y": 0.37, "EK3_x": 0.44, "EK3_y": 0.44},
    "DP26":   {"EK1_x": 0.33, "EK1_y": 0.33, "EK2_x": 0.40, "EK2_y": 0.40, "EK3_x": 0.47, "EK3_y": 0.47},
    "DGP24/5.5": {"EK1_x": 0.30, "EK1_y": 0.33, "EK2_x": 0.37, "EK2_y": 0.40, "EK3_x": 0.44, "EK3_y": 0.48},
    "DGP26/5.5": {"EK1_x": 0.33, "EK1_y": 0.36, "EK2_x": 0.40, "EK2_y": 0.43, "EK3_x": 0.47, "EK3_y": 0.51},
    "DPM24":  {"EK1_x": 0.31, "EK1_y": 0.34, "EK2_x": 0.38, "EK2_y": 0.42, "EK3_x": 0.45, "EK3_y": 0.49},
    "DGP24/10.0": {"EK1_x": 0.30, "EK1_y": 0.36, "EK2_x": 0.37, "EK2_y": 0.43, "EK3_x": 0.44, "EK3_y": 0.52},
    "DGP26/10.0": {"EK1_x": 0.33, "EK1_y": 0.39, "EK2_x": 0.40, "EK2_y": 0.48, "EK3_x": 0.47, "EK3_y": 0.56},
}

# Mastbilder (URLs)
mastbilder = {
    "DP22 (HEB220)": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Heb_profile.png/120px-Heb_profile.png",
    "DP26 (HEB260)": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/IPE_profile.svg/120px-IPE_profile.svg.png",
    "DPM24 (HEM240)": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/HEM_profile.png/120px-HEM_profile.png",
}

# PDF-Erzeugungsfunktion mit Logo und Layout
def erstelle_pdf_bericht(bericht_lines, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=30)
        pdf.set_y(30)
    else:
        pdf.set_y(10)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Maststatik Berechnungsbericht", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    for line in bericht_lines:
        pdf.multi_cell(0, 8, line)
    
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Logo lokal einbinden
logo_path = "492a83b2-c148-4843-ad75-9544f8d35c6d.png"

# UI Aufbau
import os
if not os.path.isfile(logo_path):
    logo_path = None  # Falls Logo nicht da, kein Fehler

import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Maststatik Tool", layout="wide")

col1, col2 = st.columns([1, 5])
with col1:
    if logo_path:
        st.image(logo_path, width=120)
with col2:
    st.markdown("<h1 style='margin-bottom: 0;'>Maststatik-Rechner mit Bericht-Download</h1>", unsafe_allow_html=True)

masttyp = st.selectbox("Masttyp auswählen", options=list(mastdaten.keys()))
mastlaenge = st.number_input("Mastlänge L [m]", min_value=1.0, value=10.0)
angriffshoehe = st.number_input("Angriffshöhe h [m]", min_value=0.1, value=5.2)

st.header("Lastfälle längs und quer zum Gleis")
F_A1 = st.number_input("A1) ständige Lasten [kN]", min_value=0.0, value=4.0)
F_A2 = st.number_input("A2) veränderliche Lasten [kN]", min_value=0.0, value=6.0)
F_A3 = st.number_input("A3) Kombination [kN]", min_value=0.0, value=8.0)
F_B1 = st.number_input("B1) einseitiger Zug [kN]", min_value=0.0, value=3.0)
F_B2 = st.number_input("B2) symmetrische Querlast [kN]", min_value=0.0, value=2.0)

st.header("Fundament-Auswahl")
fundament_masttyp = st.selectbox("Fundament Masttyp", options=list(fundament_faktoren.keys()))
fundament_ek = st.selectbox("Einwirkungskombination (EK)", options=["EK1", "EK2", "EK3"])

if st.button("Berechnen"):
    L_mm = mastlaenge * 1000
    h_mm = angriffshoehe * 1000
    daten = mastdaten[masttyp]
    
    lastfaelle = {
        "A1 – ständige Lasten": F_A1,
        "A2 – veränderliche Lasten": F_A2,
        "A3 – Kombination": F_A3,
        "B1 – einseitiger Zug": F_B1,
        "B2 – symmetrische Querlast": F_B2,
    }
    
    bericht = []
    bericht.append(f"Masttyp: {masttyp}")
    bericht.append(f"Mastlänge L: {mastlaenge} m")
    bericht.append(f"Angriffshöhe h: {angriffshoehe} m\n")
    bericht.append("Lastfälle:")
    
    st.write("## Maststatik Ergebnisse")
    for titel, F_kN in lastfaelle.items():
        F = F_kN * 1000
        M = F * h_mm
        sigma = M / daten["Wx"]
        f = F * L_mm**3 / (3 * E * daten["Ix"])
        status = "OK" if sigma < sigma_zul else "ÜBERLAST"
        st.write(f"**{titel}:**")
        st.write(f"- Biegemoment: {M/1e6:.2f} kNm")
        st.write(f"- Spannung: {sigma:.2f} N/mm² ({status})")
        st.write(f"- Durchbiegung Mastspitze: {f:.1f} mm")
        
        bericht.append(f"{titel}:")
        bericht.append(f"  Biegemoment: {M/1e6:.2f} kNm")
        bericht.append(f"  Spannung: {sigma:.2f} N/mm² ({status})")
        bericht.append(f"  Durchbiegung Mastspitze: {f:.1f} mm\n")
    
    faktor_x = fundament_faktoren[fundament_masttyp][f"{fundament_ek}_x"]
    faktor_y = fundament_faktoren[fundament_masttyp][f"{fundament_ek}_y"]
    
    M_max = lastfaelle["A3 – Kombination"] * 1000 * h_mm
    
    bemessung_x = M_max * faktor_x / 1000
    bemessung_y = M_max * faktor_y / 1000
    
    st.write("## Fundamentschrauben-Bemessung")
    st.write(f"- Bemessungslast in x-Richtung: {bemessung_x:.2f} kN")
    st.write(f"- Bemessungslast in y-Richtung: {bemessung_y:.2f} kN")
    
    bericht.append("Fundamentschrauben-Bemessung:")
    bericht.append(f"  Bemessungslast in x-Richtung: {bemessung_x:.2f} kN")
    bericht.append(f"  Bemessungslast in y-Richtung: {bemessung_y:.2f} kN")
    
    # Bericht generieren und Download anbieten
    pdf_data = erstelle_pdf_bericht(bericht, logo_path=logo_path)
    st.download_button(
        label="PDF Bericht herunterladen",
        data=pdf_data,
        file_name="maststatik_bericht.pdf",
        mime="application/pdf"
    )
