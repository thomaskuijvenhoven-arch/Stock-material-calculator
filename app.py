import streamlit as st
import numpy as np
import fitz  # PyMuPDF
import re

# Pagina ingesteld op 'wide'
st.set_page_config(page_title="CNC Materiaal & Klem Calculator", page_icon="⚙️", layout="wide")

st.title("⚙️ CNC Uitgangsmateriaal & Handelsmaten-Calculator")
st.write("Upload je tekening. Kies het profieltype en de app kiest de dichtstbijzijnde, meest efficiënte handelsmaat.")

# --- DATABANK MET HANDELSMATEN (Inclusief 110x45 e.d.) ---
ROND_MATEN = [3, 4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32, 35, 36, 38, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100, 110, 120, 130, 140, 150, 160, 180, 200]
VIERKANT_MATEN = [6, 8, 10, 12, 14, 15, 16, 18, 20, 22, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100, 110, 120]
PLAT_MATEN = [
    (15,3), (15,4), (15,5),
    (20,3), (20,4), (20,5), (20,6), (20,8), (20,10),
    (25,3), (25,4), (25,5), (25,6), (25,8), (25,10),
    (30,3), (30,4), (30,5), (30,6), (30,8), (30,10), (30,12),
    (35,4), (35,5), (35,6), (35,8), (35,10),
    (40,3), (40,4), (40,5), (40,6), (40,8), (40,10), (40,12), (40,15), (40,20),
    (50,3), (50,4), (50,5), (50,6), (50,8), (50,10), (50,12), (50,15), (50,20), (50,25),
    (60,5), (60,6), (60,8), (60,10), (60,12), (60,15), (60,20),
    (70,6), (70,8), (70,10), (70,12), (70,15),
    (80,5), (80,6), (80,8), (80,10), (80,12), (80,15), (80,20), (80,25),
    (100,5), (100,6), (100,8), (100,10), (100,12), (100,15), (100,20), (100,25), (100,30),
    (110,40), (110,45), (110,50),  # Toegevoegd voor jouw specifieke maat!
    (120,10), (120,12), (120,15), (120,20), (120,25), (120,30), (120,40),
    (150,10), (150,12), (150,15), (150,20), (150,25), (150,30), (150,40),
    (200,10), (200,15), (200,20), (200,25), (200,30), (200,40),
    (250,10), (250,15), (250,20), (250,25), (250,30), (250,40),
    (300,10), (300,15), (300,20), (300,25), (300,30)
]

col_links, col_rechts = st.columns([1.3, 1])

gedetecteerde_maten = []

with col_links:
    st.subheader("📂 Geüploade Tekening / PDF")
    uploaded_file = st.file_uploader("Sleep hier een PDF, PNG of JPG", type=["pdf", "png", "jpg", "jpeg"])
    camera_foto = st.camera_input("📸 Of maak direct een foto met de camera")

    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith('.pdf'):
            try:
                bytes_data = uploaded_file.read()
                doc = fitz.open(stream=bytes_data, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                st.image(pix.tobytes("png"), caption=f"PDF Tekening: {uploaded_file.name}", use_container_width=True)
                
                pdf_tekst = ""
                for p in doc:
                    pdf_tekst += p.get_text()
                
                gevonden_getallen = re.findall(r'\b\d+[\.,]?\d*\b', pdf_tekst)
                unieke_getallen = sorted(list(set([float(g.replace(',', '.')) for g in gevonden_getallen if float(g.replace(',', '.')) > 0])), reverse=True)
                
                if unieke_getallen:
                    gedetecteerde_maten = unieke_getallen
                    st.success(f"🔍 {len(unieke_getallen)} mogelijke maten gedetecteerd uit de PDF!")
                
            except Exception as e:
                st.error(f"Kon de PDF niet verwerken: {e}")
                
        elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.image(uploaded_file, caption=f"Afbeelding: {uploaded_file.name}", use_container_width=True)
            
    elif camera_foto is not None:
        st.image(camera_foto, caption="Gemaakte Foto", use_container_width=True)

# Defaults ophalen
default_l = gedetecteerde_maten[0] if len(gedetecteerde_maten) > 0 else 150.0
default_b = gedetecteerde_maten[1] if len(gedetecteerde_maten) > 1 else 105.0
default_d = gedetecteerde_maten[2] if len(gedetecteerde_maten) > 2 else 36.0

with col_rechts:
    st.subheader("1. Keuze Profieltype")
    profiel_type = st.selectbox("Selecteer profielvorm", ["Plat", "Vierkant", "Rond"])

    st.subheader("2. Netto Productmaten")
    netto_l = st.number_input("Netto Lengte (mm)", value=float(default_l), step=1.0)
    netto_b = st.number_input("Netto Breedte / Diameter (mm)", value=float(default_b), step=1.0)
    netto_d = st.number_input("Netto Dikte (mm) / Hoogte", value=float(default_d), step=1.0)

    st.subheader("3. Bewerkings- en Opspanmarges")
    omtrek_xy = st.number_input("Freesmarge omtrek per zijde (mm)", value=3.0, step=0.5)
    klem_z = st.number_input("Klem-grijphoogte / ondermaat (mm)", value=5.0, step=0.5)
    vlak_z = st.number_input("Vlakmarge bovenzijde (mm)", value=2.0, step=0.5)

st.markdown("---")

if st.button("🚀 Bereken & Zoek Beste Handelsmaat", type="primary"):
    bruto_l_min = netto_l + (2 * omtrek_xy)
    bruto_b_min = netto_b + (2 * omtek_xy) if 'omtek_xy' not in locals() else netto_b + (2 * omtrek_xy)
    bruto_d_min = netto_d + klem_z + vlak_z

    st.subheader("📋 Advies & Handelsmaatingeschiktheid")

    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📐 Berekende Minimale Maat")
        st.write(f"* **Min. Zaaglengte:** **{bruto_l_min:.1f} mm**")
        st.write(f"* **Min. Breedte:** {bruto_b_min:.1f} mm")
        st.write(f"* **Min. Dikte:** {bruto_d_min:.1f} mm")

    with col2:
        st.write("### 🛒 Gevonden Handelsmaat (Meest Efficiënt)")
        
        if profiel_type == "Rond":
            gekozen_d = min([d for d in ROND_MATEN if d >= max(bruto_b_min, bruto_d_min)], default=max(ROND_MATEN))
            st.success(f"""
            * **Profiel:** Rond
            * **Diameter:** **Ø{gekozen_d} mm**
            * **Af te zagen lengte:** **{bruto_l_min:.1f} mm**[cite: 2]
            * **Leverlengte:** 3m of 6m[cite: 2]
            """)
            
        elif profiel_type == "Vierkant":
            gekozen_v = min([v for v in VIERKANT_MATEN if v >= max(bruto_b_min, bruto_d_min)], default=max(VIERKANT_MATEN))
            st.success(f"""
            * **Profiel:** Vierkant[cite: 2]
            * **Afmeting:** **{gekozen_v} x {gekozen_v} mm**[cite: 2]
            * **Af te zagen lengte:** **{bruto_l_min:.1f} mm**[cite: 2]
            * **Leverlengte:** 3m of 6m[cite: 2]
            """)
            
        elif profiel_type == "Plat":
            # Filter alle platstaf maten waar zowel breedte >= bruto_b_min EN dikte >= bruto_d_min
            passende_plats = [m for m in PLAT_MATEN if m[0] >= bruto_b_min and m[1] >= bruto_d_min]
            
            if passende_plats:
                # Sorteer op 'kleinst totalen oppervlak' (meest efficiënte/lichtste staf die past)
                gekozen_plat = min(passende_plats, key=lambda x: x[0] * x[1])
            else:
                gekozen_plat = PLAT_MATEN[-1]
                
            st.success(f"""
            * **Profiel:** Platstaf[cite: 2]
            * **Breedte x Dikte:** **{gekozen_plat[0]} x {gekozen_plat[1]} mm**[cite: 2]
            * **Af te zagen lengte:** **{bruto_l_min:.1f} mm**[cite: 2]
            * **Leverlengte:** 3m of 6m[cite: 2]
            """)

    st.info(f"💡 **Resultaat:** Je zaagt dit product af op **{bruto_l_min:.1f} mm** uit het gekozen standaard handelsmaten-profiel[cite: 2]!")
