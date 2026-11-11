import streamlit as st
import numpy as np
import fitz  # PyMuPDF voor PDF verwerking en tekstextractie
import re    # Voor het zoeken naar getallen in de tekst

# Pagina ingesteld op 'wide' zodat de tekening links groot getoond wordt
st.set_page_config(page_title="CNC Materiaal & Klem Calculator", page_icon="⚙️", layout="wide")

st.title("⚙️ CNC Uitgangsmateriaal & Klem-Calculator")
st.write("Sleep je 2D-tekening (PDF of afbeelding) hierheen. De app leest de maten uit en berekent direct je bruto uitgangsmateriaal.")

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
                
                # Toon de eerste pagina van de PDF groot als afbeelding
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                st.image(pix.tobytes("png"), caption=f"PDF Tekening: {uploaded_file.name}", use_container_width=True)
                
                # Haal tekst op om maten te detecteren
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

# Bepaal slimme defaults uit de PDF (of standaardwaarden)
default_l = gedetecteerde_maten[0] if len(gedetecteerde_maten) > 0 else 150.0
default_b = gedetecteerde_maten[1] if len(gedetecteerde_maten) > 1 else 105.0
default_d = gedetecteerde_maten[2] if len(gedetecteerde_maten) > 2 else 36.0

with col_rechts:
    st.subheader("1. Netto Productmaten")
    if gedetecteerde_maten:
        st.info(f"💡 Gevonden getallen: {', '.join(map(str, gedetecteerde_maten[:8]))} ...")

    netto_l = st.number_input("Netto Lengte (mm)", value=float(default_l), step=1.0)
    netto_b = st.number_input("Netto Breedte (mm)", value=float(default_b), step=1.0)
    netto_d = st.number_input("Netto Dikte (mm)", value=float(default_d), step=1.0)

    st.subheader("2. Bewerkings- en Opspanmarges")
    omtrek_xy = st.number_input("Freesmarge omtrek per zijde (mm)", value=3.0, step=0.5, 
                                help="Extra materiaal rondom om de contouren schoon te frezen.")
    klem_z = st.number_input("Klem-grijphoogte / ondermaat (mm)", value=5.0, step=0.5,
                             help="Hoeveel millimeter het materiaal in de klembekken grijpt.")
    vlak_z = st.number_input("Vlakmarge bovenzijde (mm)", value=2.0, step=0.5,
                             help="Extra dikte om de bovenste huidlaag schoon te vlakken.")

st.markdown("---")

# Berekeningsknop
if st.button("🚀 Bereken Bruto Uitgangsmateriaal", type="primary"):
    bruto_l = netto_l + (2 * omtrek_xy)
    bruto_b = netto_b + (2 * omtrek_xy)
    bruto_dopspan = netto_d + klem_z + vlak_z

    st.subheader("📋 Advies Uitgangsmateriaal & Opspanning")

    st.info(f"""
    * **Minimale Zaaglengte:** **{bruto_l:.1f} mm** (incl. {omtrek_xy} mm freesovermaat per zijde)
    * **Minimale Zaagbreedte:** **{bruto_b:.1f} mm** (incl. {omtrek_xy} mm freesovermaat per zijde)
    * **Minimale Bruto Dikte:** **{bruto_dopspan:.1f} mm**
    """)

    st.write(f"💡 **Opspan-tip:** Met een blok van **{bruto_dopspan:.1f} mm** dik heb je **{klem_z:.1f} mm** vlees onderin de klem, **{vlak_z:.1f} mm** om de bovenkant te vlakken, en houd je exact je netto productdikte van **{netto_d:.1f} mm** over.")
