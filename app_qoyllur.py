#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN DEFINITIVA
✅ LUGARES EXTRAÍDOS DIRECTAMENTE DEL TTL
✅ SIN diccionarios manuales
✅ SIN leyendas infinitas
✅ SOLO el mapa con los lugares del TTL
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
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1e3c72 0%, #2c5a8c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin: 20px 0;
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
    ns = "http://example.org/festividades#"
    
    for s in g.subjects(RDF.type, URIRef(ns + "Lugar")):
        nombre = str(s).split('#')[-1]
        
        lat = None
        lon = None
        alt = 0
        tipo = "Lugar sagrado"
        
        for p, o in g.predicate_objects(s):
            if str(p).endswith('lat'):
                lat = float(o)
            if str(p).endswith('long'):
                lon = float(o)
            if str(p).endswith('comment'):
                desc = str(o)
        
        if lat and lon:
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "tipo": tipo,
                "nombre": nombre
            }
    
    return lugares

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
# MAPA CON LUGARES DEL TTL
# ============================================================================
def crear_mapa_ttl(tipo_ruta="todas", estilo_mapa="calle"):
    """Mapa con lugares EXTRAÍDOS DIRECTAMENTE DEL TTL"""
    
    LUGARES = cargar_lugares_desde_ttl()
    
    # Colores por lugar (para que se vean bonitos)
    COLORES = {
        "Paucartambo": "#1e3c72",
        "Huancarani": "#1e3c72",
        "Ccatcca": "#1e3c72",
        "Ocongate": "#1e3c72",
        "Tayancani": "#1e3c72",
        "SantuarioQoylluriti": "#f39c12",
        "ColquePunku": "#3498db",
        "MachuCruz": "#27ae60",
        "Yanaqocha": "#16a085",
        "Yanaqancha": "#8e44ad",
        "QespiCruz": "#27ae60",
        "IntiLloksimuy": "#f1c40f",
        "Caicay": "#1e3c72",
        "Challabamba": "#1e3c72",
        "Colquepata": "#1e3c72",
        "Ccapi": "#1e3c72",
        "Ccarhuayo": "#1e3c72",
        "Mollomarca": "#1e3c72",
        "Mahuayani": "#2c3e50",
    }
    
    # Iconos por lugar
    ICONOS = {
        "Paucartambo": "🏘️",
        "Huancarani": "🛣️",
        "Ccatcca": "🍖",
        "Ocongate": "🏠",
        "Tayancani": "🏁",
        "SantuarioQoylluriti": "🏔️",
        "ColquePunku": "❄️",
        "MachuCruz": "✝️",
        "Yanaqocha": "💧",
        "Yanaqancha": "😴",
        "QespiCruz": "🎵",
        "IntiLloksimuy": "☀️",
        "Caicay": "🏘️",
        "Challabamba": "🏘️",
        "Colquepata": "🏘️",
        "Ccapi": "🏘️",
        "Ccarhuayo": "🏘️",
        "Mollomarca": "🏘️",
        "Mahuayani": "🚩",
    }
    
    ESTILOS_MAPA = {
        "calle": "carto-positron",
        "outdoor": "open-street-map",
        "oscuro": "carto-darkmatter"
    }
    
    fig = go.Figure()
    
    # ===== AGREGAR RUTAS =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords = []
        for l in RUTA_VEHICULAR:
            if l in LUGARES:
                coords.append(LUGARES[l])
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
            if l in LUGARES:
                coords.append(LUGARES[l])
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="Ruta Lomada",
                hoverinfo="skip"
            ))
    
    # ===== AGREGAR LUGARES DIRECTAMENTE DEL TTL =====
    for nombre, lugar in LUGARES.items():
        color = COLORES.get(nombre, "#e67e22")
        icono = ICONOS.get(nombre, "📍")
        
        hover_text = f"""
        <b style='font-size: 16px; color: {color};'>{icono} {nombre}</b><br>
        <span style='font-size: 13px;'>
        📏 {lugar['lat']:.4f}, {lugar['lon']:.4f}
        </span>
        """
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=dict(
                size=12,
                color=color,
                symbol="marker"
            ),
            name=nombre,
            hovertemplate=hover_text + "<extra></extra>",
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=color,
                font=dict(size=12, color="#1e3c72")
            ),
            showlegend=False
        ))
    
    # ===== CONFIGURAR MAPA =====
    estilo = ESTILOS_MAPA.get(estilo_mapa, "carto-positron")
    
    fig.update_layout(
        mapbox=dict(
            style=estilo,
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.5
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        clickmode='event+select'
    )
    
    return fig, len(LUGARES)

# ============================================================================
# PERFIL DE ALTITUD
# ============================================================================
def crear_perfil_altitud():
    """Perfil de altitud simple"""
    
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
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["dist"], y=df["alt"],
        mode="lines+markers",
        line=dict(color="#1e3c72", width=4),
        marker=dict(size=10, color="#e67e22"),
        text=df["lugar"],
        hovertemplate="<b>%{text}</b><br>📏 %{x:.0f} km<br>🏔️ %{y:.0f} msnm<extra></extra>"
    ))
    
    fig.update_layout(
        height=400,
        hovermode="x unified",
        plot_bgcolor="white",
        xaxis_title="Distancia (km)",
        yaxis_title="Altitud (msnm)"
    )
    
    return fig

# ============================================================================
# APP PRINCIPAL
# ============================================================================
def main():
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
        <div style="font-size: 4rem;">🏔️</div>
        <div>
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; color: #1e3c72;">
                Qoyllur Rit'i Explorer
            </h1>
            <p style="margin: 0; color: #7f8c8d; font-size: 1.2rem;">
                Peregrinación al Señor de Qoyllur Rit'i · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🏔️ La peregrinación")
        st.markdown("""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **📍 Altitud:** 4,800 - 5,200 msnm  
        **👥 Participantes:** Ocho naciones  
        **⏳ Duración:** 5 días
        """)
    
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa", "⛰️ Perfil"])
    
    # ===== TAB 1: PREGUNTAS =====
    with tab1:
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando conocimiento ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pregunta = st.selectbox(
                "Selecciona una pregunta:",
                options=[""] + TOP_10_PREGUNTAS,
                format_func=lambda x: "Elige una pregunta..." if x == "" else x
            )
        with col2:
            st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
            responder = st.button("✨ Consultar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        if responder and pregunta:
            with st.spinner("🔍 Buscando..."):
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
    
    # ===== TAB 2: MAPA - SOLO LUGARES DEL TTL =====
    with tab2:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("### 🗺️ Lugares sagrados del TTL")
        with col2:
            tipo_ruta = st.radio(
                "Rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True
            )
        with col3:
            estilo_mapa = st.selectbox(
                "Estilo:",
                ["Calle", "Outdoor", "Oscuro"],
                index=0
            )
        
        mapa, num_lugares = crear_mapa_ttl(
            tipo_ruta.lower(),
            estilo_mapa.lower()
        )
        
        st.plotly_chart(mapa, use_container_width=True)
        
        # SOLO métricas, SIN leyendas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares del TTL", num_lugares)
        with col2:
            st.metric("🚌 Ruta vehicular", "85 km")
        with col3:
            st.metric("🚶 Lomada", "35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
    
    # ===== TAB 3: PERFIL =====
    with tab3:
        st.markdown("### ⛰️ Perfil de altitud")
        
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
    
    # ===== FOOTER =====
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer</span>
            <span>•</span>
            <span>🗺️ Lugares del TTL</span>
            <span>•</span>
            <span>📊 Perfil de altitud</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Nación Paucartambo · Sinakara, Cusco
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()