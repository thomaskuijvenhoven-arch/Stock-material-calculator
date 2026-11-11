import streamlit as st
import numpy as np
import fitz  # PyMuPDF
import cv2
import plotly.graph_objects as go

st.set_page_config(page_title="CNC Materiaal Calculator & 3D Contour Viewer", page_icon="⚙️", layout="wide")

st.title("⚙️ CNC Uitgangsmateriaal & 3D Contour-Viewer")
st.write("Sleep je PDF-tekening in de app. De app detecteert de buitenlijnen en toont het 3D-product in het ruwe materiaal.")

col_links, col_rechts = st.columns([1.3, 1])

netto_l_default = 150.0
netto_b_default = 105.0
netto_d_default = 36.0

# Opslag voor gedetecteerde contour punten
contour_punten = None

with col_links:
    st.subheader("📂 2D Tekening / PDF")
    uploaded_file = st.file_uploader("Sleep hier een PDF, PNG of JPG", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        try:
            img_array = None
            if uploaded_file.name.lower().endswith('.pdf'):
                bytes_data = uploaded_file.read()
                doc = fitz.open(stream=bytes_data, filetype="pdf")
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                st.image(pix.tobytes("png"), caption=f"PDF: {uploaded_file.name}", use_container_width=True)
                
                # Omzetten naar OpenCV formaat voor contour-detectie
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    img_array = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
                else:
                    img_array = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                img_array = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                st.image(uploaded_file, caption="Geüploade afbeelding", use_container_width=True)

            # Automatische contour (buitenlijn) detectie via OpenCV
            if img_array is not None:
                _, thresh = cv2.threshold(img_array, 200, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    # Pak de grootste contour (het product)
                    grootste_contour = max(contours, key=cv2.contourArea)
                    # Vereenvoudig de contour een beetje voor strakke 3D lijnen
                    epsilon = 0.015 * cv2.arcLength(grootste_contour, True)
                    approx = cv2.approxPolyDP(grootste_contour, epsilon, True)
                    if len(approx) >= 3:
                        contour_punten = approx.squeeze()

        except Exception as e:
            st.error(f"Fout bij verwerken tekening: {e}")

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

# --- 3D VISUALISATIE MET CONTOUR EXTRUSIE ---
st.subheader("🧊 3D Visualisatie: Product-contour in Bruto Blok")

c1, c2 = st.columns(2)
with c1:
    toon_bruto = st.checkbox("Toon Bruto Uitgangsmateriaal (Doorzichtig)", value=True)
with c2:
    toon_netto = st.checkbox("Toon Netto Product Contour (3D Gextrudeerd)", value=True)

fig = go.Figure()

# 1. Bruto blok (doorzichtig)
if toon_bruto:
    bx, by, bz = bruto_l, bruto_b, bruto_dopspan
    fig.add_trace(go.Mesh3d(
        x=[0, bx, bx, 0, 0, bx, bx, 0],
        y=[0, 0, by, by, 0, 0, by, by],
        z=[0, 0, 0, 0, bz, bz, bz, bz],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 2, 1, 5, 1, 5, 2, 7],
        color='lightblue',
        opacity=0.2,
        name='Bruto Uitgangsmateriaal'
    ))

# 2. Netto product (op basis van gedetecteerde contour of fallback rechthoek)
if toon_netto:
    if contour_punten is not None and len(contour_punten) > 2:
        # Normaliseer en schaal gedetecteerde contour naar de netto maten van de gebruiker
        pts = contour_punten.astype(float)
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        
        # Schaal naar mm binnen de netto afmetingen, gecentreerd met omtrek_xy
        range_x = max_x - min_x if max_x != min_x else 1.0
        range_y = max_y - min_y if max_y != min_y else 1.0
        
        scaled_x = omtrek_xy + (pts[:, 0] - min_x) / range_x * netto_l
        scaled_y = omtrek_xy + (pts[:, 1] - min_y) / range_y * netto_b
        
        n_pts = len(scaled_x)
        # Maak 3D extrusie mesh (onderkant op klem_z, bovenkant op klem_z + netto_d)
        x_mesh = np.concatenate([scaled_x, scaled_x])
        y_mesh = np.concatenate([scaled_y, scaled_y])
        z_mesh = np.concatenate([np.full(n_pts, klem_z), np.full(n_pts, klem_z + netto_d)])
        
        fig.add_trace(go.Mesh3d(
            x=x_mesh, y=y_mesh, z=z_mesh,
            alphahull=0,
            color='orange',
            opacity=0.85,
            name='Netto Product (Gedetecteerd Vorm)'
        ))
    else:
        # Fallback naar rechthoekig blok als er geen contour gevonden is
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
            opacity=0.85,
            name='Netto Product (Rechthoek)'
        ))

# Layout instellingen
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
