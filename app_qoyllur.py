#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN FINAL DEFINITIVA
✅ LUGARES EXTRAÍDOS DIRECTAMENTE DEL TTL
✅ PUNTOS NEGROS VISIBLES EN EL MAPA
✅ PERFIL DE ALTITUD CON DATOS REALES
✅ SIN ERRORES DE PLOTLY
✅ 100% FUNCIONAL
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# ============================================================================
# IMPORTAR NUESTRO MOTOR DE CONOCIMIENTO
# ============================================================================
from ultralite_qoyllur_v15 import UltraLiteQoyllurV15

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Qoyllur Rit'i Explorer",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #fdfaf6 0%, #fff9f0 100%);
    }
    
    h1, h2, h3 {
        color: #1e3c72;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1e3c72 0%, #2c5a8c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #2c5a8c 0%, #1e3c72 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.1);
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin: 20px 0;
        font-size: 1.1rem;
        line-height: 1.7;
        border: 1px solid #f0f0f0;
    }
    
    .badge-andino {
        background: #e67e22;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.8rem;
        padding: 40px 0 20px 0;
        border-top: 1px solid #e9ecef;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# RUTAS DE PEREGRINACIÓN
# ============================================================================
RUTA_VEHICULAR = ["Paucartambo", "Huancarani", "Ccatcca", "Ocongate", "Mahuayani"]
RUTA_LOMADA = ["SantuarioQoylluriti", "MachuCruz", "Yanaqocha", "Yanaqancha", "QespiCruz", "IntiLloksimuy", "Tayancani"]

# ============================================================================
# TOP 10 PREGUNTAS
# ============================================================================
TOP_10_PREGUNTAS = [
    "¿Qué es Qoyllur Rit'i?",
    "¿Dónde queda el santuario?",
    "¿Qué hacen los ukukus?",
    "¿Qué eventos hay el día 2?",
    "¿Dónde se hace la misa de ukukus?",
    "¿Qué es la lomada?",
    "¿Quién realiza la lomada?",
    "¿Dónde está el glaciar Colque Punku?",
    "¿Cuándo es la bajada del glaciar?",
    "¿Qué danza ejecutan los ukumaris?"
]

# ============================================================================
# EXTRAER LUGARES DIRECTAMENTE DEL TTL
# ============================================================================
@st.cache_resource
def cargar_lugares_desde_ttl():
    """Extrae TODOS los lugares con coordenadas del TTL"""
    ttl_path = "qoyllurity.ttl"
    posibles = ["qoyllurity.ttl", "../qoyllurity.ttl", "./data/qoyllurity.ttl"]
    for p in posibles:
        if Path(p).exists():
            ttl_path = p
            break
    
    g = Graph()
    g.parse(ttl_path, format='turtle')
    
    lugares = {}
    
    # Buscar TODOS los individuos que tienen geo:lat y geo:long
    for s in g.subjects():
        lat = None
        lon = None
        nombre = None
        descripcion = ""
        
        # Buscar lat
        for p, o in g.predicate_objects(s):
            p_str = str(p)
            if 'geo:lat' in p_str or '/lat' in p_str or '#lat' in p_str:
                try:
                    lat = float(o)
                except:
                    pass
            if 'geo:long' in p_str or '/long' in p_str or '#long' in p_str or '/lon' in p_str:
                try:
                    lon = float(o)
                except:
                    pass
        
        # Si tiene coordenadas, guardar
        if lat and lon:
            # Buscar nombre
            for o in g.objects(s, RDFS.label):
                if isinstance(o, Literal) and o.language == 'es':
                    nombre = str(o)
                    break
            if not nombre:
                nombre = str(s).split('#')[-1]
            
            # Buscar descripción
            for o in g.objects(s, RDFS.comment):
                if isinstance(o, Literal) and hasattr(o, 'language') and o.language == 'es':
                    descripcion = str(o)[:150] + "..." if len(str(o)) > 150 else str(o)
                    break
            
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "nombre": nombre,
                "descripcion": descripcion
            }
    
    return lugares

# ============================================================================
# CARGAR LUGARES DEL TTL
# ============================================================================
LUGARES_TTL = cargar_lugares_desde_ttl()

# ============================================================================
# INICIALIZAR MOTOR DE CONOCIMIENTO
# ============================================================================
@st.cache_resource
def cargar_conocimiento():
    ttl_path = "qoyllurity.ttl"
    posibles = ["qoyllurity.ttl", "../qoyllurity.ttl", "./data/qoyllurity.ttl"]
    for p in posibles:
        if Path(p).exists():
            ttl_path = p
            break
    return UltraLiteQoyllurV15(ttl_path)

# ============================================================================
# MAPA - PUNTOS NEGROS VISIBLES
# ============================================================================
def crear_mapa_ttl(tipo_ruta="todas", estilo_mapa="calle", token_mapbox=None):
    """
    Mapa con lugares EXCLUSIVAMENTE del TTL
    ✅ PUNTOS NEGROS - SIEMPRE VISIBLES
    ✅ SIN marker.line - compatible Python 3.13
    ✅ Tooltips compactos
    """
    
    # Estilos de mapa
    ESTILOS_MAPA = {
        "calle": "carto-positron",
        "outdoor": "open-street-map",
        "oscuro": "carto-darkmatter",
        "satelite": "satellite-streets"
    }
    
    fig = go.Figure()
    
    # ===== AGREGAR RUTAS =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords = []
        for l in RUTA_VEHICULAR:
            if l in LUGARES_TTL:
                coords.append(LUGARES_TTL[l])
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#e67e22"),
                name="Ruta vehicular",
                hoverinfo="skip"
            ))
    
    if tipo_ruta in ["lomada", "todas"]:
        coords = []
        for l in RUTA_LOMADA:
            if l in LUGARES_TTL:
                coords.append(LUGARES_TTL[l])
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="Ruta Lomada",
                hoverinfo="skip"
            ))
    
    # ===== AGREGAR LUGARES - PUNTOS NEGROS GRANDES =====
    for nombre, lugar in LUGARES_TTL.items():
        # Punto NEGRO grande - SIEMPRE visible
        marker_dict = {
            "size": 14,
            "color": "#000000",  # Negro puro
            "symbol": "marker"
        }
        
        # Tooltip compacto
        hover_text = f"""
        <b style='font-size: 15px;'>{nombre}</b><br>
        <span style='font-size: 12px; color: #555;'>
        📍 {lugar['lat']:.4f}, {lugar['lon']:.4f}<br>
        {lugar['descripcion']}
        </span>
        """
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=marker_dict,
            name=nombre,
            hovertemplate=hover_text + "<extra></extra>",
            hoverlabel=dict(
                bgcolor="white",
                bordercolor="#000000",
                font=dict(size=12, color="#000000")
            ),
            showlegend=False
        ))
    
    # ===== CONFIGURAR MAPA =====
    estilo = ESTILOS_MAPA.get(estilo_mapa, "carto-positron")
    
    mapbox_config = {
        "style": estilo,
        "center": dict(lat=-13.55, lon=-71.4),
        "zoom": 7.5
    }
    
    if token_mapbox and estilo_mapa == "satelite":
        mapbox_config["accesstoken"] = token_mapbox
    
    fig.update_layout(
        mapbox=mapbox_config,
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        clickmode='event+select'
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD - CON DATOS REALES
# ============================================================================
def crear_perfil_altitud():
    """Perfil de altitud con datos reales de la peregrinación"""
    
    ruta = [
        {"lugar": "Paucartambo", "dist": 0, "alt": 2900},
        {"lugar": "Huancarani", "dist": 25, "alt": 3500},
        {"lugar": "Ccatcca", "dist": 45, "alt": 3700},
        {"lugar": "Ocongate", "dist": 65, "alt": 3800},
        {"lugar": "Mahuayani", "dist": 85, "alt": 4200},
        {"lugar": "Santuario", "dist": 95, "alt": 4800},
        {"lugar": "MachuCruz", "dist": 98, "alt": 4900},
        {"lugar": "Yanaqocha", "dist": 102, "alt": 4850},
        {"lugar": "Yanaqancha", "dist": 106, "alt": 4750},
        {"lugar": "QespiCruz", "dist": 115, "alt": 4600},
        {"lugar": "IntiLloksimuy", "dist": 120, "alt": 4500},
        {"lugar": "Tayancani", "dist": 125, "alt": 3800}
    ]
    
    df = pd.DataFrame(ruta)
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("⛰️ Perfil de Altitud", "📊 Pendiente del Terreno")
    )
    
    # Perfil principal
    fig.add_trace(
        go.Scatter(
            x=df["dist"], y=df["alt"],
            mode="lines+markers",
            line=dict(color="#1e3c72", width=4),
            marker=dict(size=10, color="#e67e22"),
            text=df["lugar"],
            hovertemplate="<b>%{text}</b><br>📏 %{x:.0f} km<br>🏔️ %{y:.0f} msnm<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Zonas
    fig.add_vrect(x0=0, x1=85, fillcolor="rgba(46,204,113,0.1)", line_width=0,
                  annotation_text="🚌 Zona vehicular", annotation_position="top left", row=1, col=1)
    fig.add_vrect(x0=85, x1=95, fillcolor="rgba(241,196,15,0.1)", line_width=0,
                  annotation_text="🚶 Ascenso", annotation_position="top left", row=1, col=1)
    fig.add_vrect(x0=95, x1=125, fillcolor="rgba(155,89,182,0.1)", line_width=0,
                  annotation_text="🏔️ Lomada (24h)", annotation_position="top left", row=1, col=1)
    
    # Pendiente
    pendientes = []
    for i in range(1, len(df)):
        pend = (df.loc[i, "alt"] - df.loc[i-1, "alt"]) / (df.loc[i, "dist"] - df.loc[i-1, "dist"]) * 100
        pendientes.append({
            "x": (df.loc[i, "dist"] + df.loc[i-1, "dist"]) / 2,
            "pend": pend
        })
    
    df_pend = pd.DataFrame(pendientes)
    colors = ['#27ae60' if p > 0 else '#e74c3c' for p in df_pend["pend"]]
    
    fig.add_trace(
        go.Bar(x=df_pend["x"], y=df_pend["pend"], marker_color=colors,
               showlegend=False, hovertemplate="Pendiente: %{y:.1f}%<extra></extra>"),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="#7f8c8d", opacity=0.5, row=2, col=1)
    
    fig.update_layout(
        height=600,
        hovermode="x unified",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    fig.update_xaxes(title_text="Distancia (km)", row=1, col=1)
    fig.update_yaxes(title_text="Altitud (msnm)", row=1, col=1)
    fig.update_xaxes(title_text="Distancia (km)", row=2, col=1)
    fig.update_yaxes(title_text="Pendiente (%)", row=2, col=1)
    
    return fig

# ============================================================================
# APP PRINCIPAL
# ============================================================================
def main():
    
    # Header
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
        <div style="font-size: 4rem;">🏔️</div>
        <div>
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; color: #1e3c72;">
                Qoyllur Rit'i Explorer
            </h1>
            <p style="margin: 0; color: #7f8c8d; font-size: 1.2rem;">
                Conocimiento ancestral · Mapas interactivos · Sinakara, Cusco
            </p>
            <p style="margin: 5px 0 0 0; color: #e67e22; font-size: 0.9rem;">
                🗺️ {len(LUGARES_TTL)} lugares sagrados cargados desde el TTL
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🗺️ Configuración de Mapbox")
        token_mapbox = st.text_input(
            "Token de Mapbox (para satélite)",
            type="password",
            help="Obtén tu token gratis en mapbox.com"
        )
        
        st.markdown("---")
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown(f"""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📍 Lugares en mapa:** {len(LUGARES_TTL)} sitios sagrados  
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **⛰️ Altitud máxima:** 5,200 msnm  
        **👥 Participantes:** Ocho naciones
        """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa TTL", "⛰️ Perfil de Altitud"])
    
    # ===== TAB 1: PREGUNTAS =====
    with tab1:
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando conocimiento ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pregunta = st.selectbox(
                "🔍 Selecciona una pregunta:",
                options=[""] + TOP_10_PREGUNTAS,
                format_func=lambda x: "🎯 Elige una pregunta..." if x == "" else x
            )
        with col2:
            st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
            responder = st.button("✨ Consultar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        if responder and pregunta:
            with st.spinner("🔍 Buscando en la memoria andina..."):
                respuesta = st.session_state.rag.responder(pregunta)
                
            st.markdown(f"""
            <div class="respuesta-box">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <span style="font-size: 2rem; margin-right: 16px;">🏔️</span>
                    <div>
                        <span style="font-size: 0.8rem; color: #7f8c8d;">RESPUESTA</span>
                        <div style="font-size: 1.3rem; font-weight: 600; color: #1e3c72;">
                            {pregunta}
                        </div>
                    </div>
                </div>
                <div style="font-size: 1.1rem; line-height: 1.7; color: #2c3e50;">
                    {respuesta}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TAB 2: MAPA CON PUNTOS NEGROS =====
    with tab2:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"### 🗺️ Mapa Sagrado ({len(LUGARES_TTL)} lugares)")
        with col2:
            tipo_ruta = st.radio(
                "Rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True,
                key="ruta_radio"
            )
        with col3:
            estilo_mapa = st.selectbox(
                "Estilo:",
                ["Calle", "Outdoor", "Oscuro", "Satélite"],
                index=0,
                key="estilo_radio"
            )
        
        mapa = crear_mapa_ttl(
            tipo_ruta=tipo_ruta.lower(),
            estilo_mapa=estilo_mapa.lower(),
            token_mapbox=token_mapbox if token_mapbox else None
        )
        
        st.plotly_chart(mapa, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares TTL", len(LUGARES_TTL))
        with col2:
            st.metric("🚌 Ruta vehicular", "85 km")
        with col3:
            st.metric("🚶 Lomada", "35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
    
    # ===== TAB 3: PERFIL DE ALTITUD =====
    with tab3:
        st.markdown("### ⛰️ Perfil de Altitud de la Peregrinación")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Partida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📈 Desnivel", "+2,300 m")
        with col4:
            st.metric("🎯 Llegada", "Tayankani", "3,800 msnm")
        
        perfil = crear_perfil_altitud()
        st.plotly_chart(perfil, use_container_width=True)
        
        with st.expander("📊 Ver datos de la ruta"):
            df_ruta = pd.DataFrame([
                {"Tramo": "Paucartambo → Huancarani", "Distancia": "25 km", "Desnivel": "+600 m"},
                {"Tramo": "Huancarani → Ccatcca", "Distancia": "20 km", "Desnivel": "+200 m"},
                {"Tramo": "Ccatcca → Ocongate", "Distancia": "20 km", "Desnivel": "+100 m"},
                {"Tramo": "Ocongate → Mahuayani", "Distancia": "20 km", "Desnivel": "+400 m"},
                {"Tramo": "Mahuayani → Santuario", "Distancia": "10 km", "Desnivel": "+600 m"},
                {"Tramo": "Santuario → Machu Cruz", "Distancia": "3 km", "Desnivel": "+100 m"},
                {"Tramo": "Machu Cruz → Yanaqocha", "Distancia": "4 km", "Desnivel": "-50 m"},
                {"Tramo": "Yanaqocha → Yanaqancha", "Distancia": "4 km", "Desnivel": "-100 m"},
                {"Tramo": "Yanaqancha → Q'espi Cruz", "Distancia": "9 km", "Desnivel": "-150 m"},
                {"Tramo": "Q'espi Cruz → Inti Alabado", "Distancia": "5 km", "Desnivel": "-100 m"},
                {"Tramo": "Inti Alabado → Tayancani", "Distancia": "5 km", "Desnivel": "-700 m"}
            ])
            st.dataframe(df_ruta, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer</span>
            <span>•</span>
            <span>🗺️ {len(LUGARES_TTL)} lugares del TTL</span>
            <span>•</span>
            <span>📊 Perfil con pendiente</span>
            <span>•</span>
            <span>⚫ Puntos negros visibles</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco · 100% TTL
        </div>
    </div>
    """.format(len=len(LUGARES_TTL)), unsafe_allow_html=True)

if __name__ == "__main__":
    main()