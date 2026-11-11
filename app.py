import streamlit as st
import numpy as np

# Pagina ingesteld op 'wide' zodat foto's en tekeningen groot getoond worden
st.set_page_config(page_title="CNC Materiaal Calculator", page_icon="⚙️", layout="wide")

st.title("⚙️ CNC Uitgangsmateriaal & Klem-Calculator")
st.write("Sleep een 2D-tekening (PDF/afbeelding) hierheen of maak direct een foto met je telefoon.")

# We verdelen het scherm nu in twee kolommen: links de afbeelding, rechts de invoer en berekening
col_links, col_rechts = st.columns([1.2, 1])

with col_links:
    st.subheader("📂 Tekening / Foto")
    uploaded_file = st.file_uploader("Sleep hier een afbeelding (PNG/JPG) of PDF", type=["pdf", "png", "jpg", "jpeg"])
    camera_foto = st.camera_input("📸 Of maak een foto met de camera")

    actief_bestand = uploaded_file if uploaded_file is not None else camera_foto

    if actief_bestand is not None:
        if hasattr(actief_bestand, "name") and actief_bestand.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.image(actief_bestand, caption="Geüploade Tekening", use_container_width=True)
        elif camera_foto is not None:
            st.image(camera_foto, caption="Gemaakte Foto", use_container_width=True)
        else:
            st.info(f"PDF-bestand '{uploaded_file.name}' succesvol geladen.")

with col_rechts:
    st.subheader("1. Netto Productmaten")
    netto_l = st.number_input("Netto Lengte (mm)", value=120.0, step=1.0)
    netto_b = st.number_input("Netto Breedte (mm)", value=80.0, step=1.0)
    netto_d = st.number_input("Netto Dikte (mm)", value=20.0, step=1.0)

    st.subheader("2. Bewerkings- en Opspanmarges")
    omtrek_xy = st.number_input("Freesmarge omtrek per zijde (mm)", value=3.0, step=0.5, 
                                help="Extra materiaal rondom om de contouren schoon te frezen.")
    klem_z = st.number_input("Klem-grijphoogte / ondermaat (mm)", value=4.0, step=0.5,
                             help="Hoeveel millimeter het materiaal in de klembekken grijpt.")
    vlak_z = st.number_input("Vlakmarge bovenzijde (mm)", value=1.5, step=0.5,
                             help="Extra dikte om de bovenste huidlaag schoon te vlakken.")

st.markdown("---")

# Berekeningsknop gecentreerd of onderaan
if st.button("🚀 Bereken Uitgangsmateriaal", type="primary"):
    bruto_l = netto_l + (2 * omtrek_xy)
    bruto_b = netto_b + (2 * omtrek_xy)
    bruto_dopspan = netto_d + klem_z + vlak_z

    st.subheader("📋 Advies Uitgangsmateriaal & Opspanning")

    st.info(f"""
    * **Minimale Zaaglengte:** **{bruto_l:.1f} mm** (incl. {omtrek_xy} mm per zijde freesovermaat)
    * **Minimale Zaagbreedte:** **{bruto_b:.1f} mm** (incl. {omtrek_xy} mm per zijde freesovermaat)
    * **Minimale Bruto Dikte:** **{bruto_dopspan:.1f} mm**
    """)

    st.write(f"💡 **Opspan-tip:** Met een blok van **{bruto_dopspan:.1f} mm** dik heb je **{klem_z:.1f} mm** vlees onderin de klem, **{vlak_z:.1f} mm** om de bovenkant te vlakken, en houd je exact je netto productdikte van **{netto_d:.1f} mm** over.")
