import streamlit as st
import numpy as np
import fitz  # PyMuPDF
import plotly.graph_objects as go

st.set_page_config(page_title="CNC Materiaal Calculator & 3D Viewer", page_icon="⚙️", layout="wide")

st.title("⚙️ CNC Uitgangsmateriaal & 3D Opspan-Viewer")
st.write("Sleep je PDF-tekening in de app. De maten worden ingevuld en het doorzichtige ruwe materiaal wordt in 3D getoond.")

col_links, col_rechts = st.columns([1.2, 1])

with col_links:
    st.subheader("📂 2D Tekening / PDF")
    uploaded_file = st.file_uploader("Sleep hier een PDF, PNG of JPG", type=["pdf", "png", "jpg", "jpeg"])
    
    netto_l_default = 150.0
    netto_b_default = 105.0
    netto_d_default = 36.0

    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith('.pdf'):
            try:
                bytes_data = uploaded_file.read()
                doc = fitz.open(stream=bytes_data, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                st.image(pix.tobytes("png"), caption=f"PDF: {uploaded_file.name}", use_container_width=True)
            except Exception as e:
                st.error(f"Fout bij inlezen PDF: {e}")
        else:
            st.image(uploaded_file, caption="Geüploade afbeelding", use_container_width=True)

with col_rechts:
    st.subheader("1. Netto Productmaten")
    netto_l = st.number_input("Netto Lengte (mm)", value=netto_l_default, step=1.0)
    netto_b = st.number_input("Netto Breedte (mm)", value=netto_b_default, step=1.0)
    netto_d = st.number_input("Netto Dikte (mm)", value=netto_d_default, step=1.0)

    st.subheader("2. Opspan- en Freesmarges")
    omtrek_xy = st.number_input("Freesmarge omtrek per zijde (mm)", value=3.0, step=0.5)
    klem_z = st.number_input("Klem-grijphoogte / ondermaat (mm)", value=5.0, step=0.5)
    vlak_z = st.number_input("Vlakmarge bovenzijde (mm)", value=2.0, step=0.5)

st.markdown("---")

# Berekeningen
bruto_l = netto_l + (2 * omtrek_xy)
bruto_b = netto_b + (2 * omtrek_xy)
bruto_dopspan = netto_d + klem_z + vlak_z

st.subheader("📋 Advies Uitgangsmateriaal")
st.info(f"**Minimale Bruto Blokmaat:** {bruto_l:.1f} x {bruto_b:.1f} x **{bruto_dopspan:.1f} mm** (incl. {klem_z} mm klemvlees)")

# --- 3D VISUALISATIE (Doorzichtig ruw materiaal + product erin) ---
st.subheader("🧊 3D Visualisatie: Product in Doorzichtig Uitgangsmateriaal")

fig = go.Figure()

# 1. Het doorzichtige bruto blok (uitgangsmateriaal)
# Coördinaten voor een kubus/blok
bx, by, bz = bruto_l, bruto_b, bruto_dopspan
fig.add_trace(go.Mesh3d(
    x=[0, bx, bx, 0, 0, bx, bx, 0],
    y=[0, 0, by, by, 0, 0, by, by],
    z=[0, 0, 0, 0, bz, bz, bz, bz],
    i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
    j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
    k=[0, 7, 2, 3, 6, 2, 1, 5, 1, 5, 2, 7],
    color='lightblue',
    opacity=0.25, # Maakt het blok doorzichtig!
    name='Bruto Uitgangsmateriaal'
))

# 2. Het netto product erin gepositioneerd (rekening houdend met marges)
# Het product begint op X = omtrek_xy, Y = omtrek_xy, en Z = klem_z
px0, py0, pz0 = omtrek_xy, omtrek_xy, klem_z
px1, py1, pz1 = omtrek_xy + netto_l, omtrek_xy + netto_b, klem_z + netto_d

fig.add_trace(go.Mesh3d(
    x=[px0, px1, px1, px0, px0, px1, px1, px0],
    y=[py0, py0, py1, py1, py0, py0, py1, py1],
    z=[pz0, pz0, pz0, pz0, pz1, pz1, pz1, pz1],
    i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
    j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
    k=[0, 7, 2, 3, 6, 2, 1, 5, 1, 5, 2, 7],
    color='orange',
    opacity=0.85, # Solide product zichtbaar binnenin
    name='Netto Product'
))

# Layout instellingen voor de 3D-viewer
fig.update_layout(
    scene=dict(
        xaxis_title='Lengte (mm)',
        yaxis_title='Breedte (mm)',
        zaxis_title='Dikte / Hoogte (mm)',
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    height=500
)

st.plotly_chart(fig, use_container_width=True)
