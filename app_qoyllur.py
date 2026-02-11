#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN CON MAPA 100% FUNCIONAL
✅ Mapas gratuitos sin token
✅ Marcadores y rutas visibles
✅ Estilos Carto (siempre funcionan)
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ============================================================================
# IMPORTAR NUESTRO MOTOR DE CONOCIMIENTO
# ============================================================================
from ultralite_qoyllur_v15 import UltraLiteQoyllurV15

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Qoyllur Rit'i · Peregrinación Andina",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - ESTILO ELEGANTE Y CÁLIDO
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #fefcf7 0%, #fffaf3 100%);
    }
    
    h1, h2, h3 {
        color: #1e3c72;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem !important;
        background: linear-gradient(135deg, #1e3c72, #2c5a8c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #d35400, #e67e22);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 16px rgba(230,126,34,0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #e67e22, #f39c12);
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(230,126,34,0.3);
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.05);
        margin: 24px 0;
        font-size: 1.1rem;
        line-height: 1.8;
        border: 1px solid rgba(0,0,0,0.02);
    }
    
    .badge-andino {
        background: #e67e22;
        color: white;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(230,126,34,0.3);
    }
    
    .footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.9rem;
        padding: 48px 0 24px 0;
        border-top: 1px solid #f0e9e0;
        margin-top: 48px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATOS DE COORDENADAS - VERSIÓN SIMPLIFICADA Y FUNCIONAL
# ============================================================================
LUGARES_SAGRADOS = {
    # PAUCARTAMBO Y ALREDEDORES
    "Paucartambo": {"lat": -13.3127, "lon": -71.6146, "alt": 2900, "tipo": "Pueblo", "emoji": "🏘️", "descripcion": "Pueblo de partida de la Nación Paucartambo"},
    "IglesiaPaucartambo": {"lat": -13.3178, "lon": -71.6319, "alt": 2900, "tipo": "Iglesia", "emoji": "⛪", "descripcion": "Misa de envío"},
    "CementerioPaucartambo": {"lat": -13.3209, "lon": -71.5959, "alt": 2900, "tipo": "Cementerio", "emoji": "🕊️", "descripcion": "Romería a hermanos antiguos"},
    "PlazaPaucartambo": {"lat": -13.3178, "lon": -71.6013, "alt": 2900, "tipo": "Plaza", "emoji": "🎭", "descripcion": "Vestimenta de danzantes"},
    
    # RUTA VEHICULAR
    "Huancarani": {"lat": -13.5003, "lon": -71.6749, "alt": 3500, "tipo": "Cruce", "emoji": "🛣️", "descripcion": "Punto de encuentro"},
    "Ccatcca": {"lat": -13.6018, "lon": -71.5753, "alt": 3700, "tipo": "Pueblo", "emoji": "🍖", "descripcion": "Comida comunitaria"},
    "Ocongate": {"lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "Pueblo", "emoji": "🏠", "descripcion": "Visita al prioste"},
    
    # ASCENSO
    "Mahuayani": {"lat": -13.6052, "lon": -71.2350, "alt": 4200, "tipo": "Inicio", "emoji": "🚩", "descripcion": "Inicio de caminata"},
    "SantuarioQoylluriti": {"lat": -13.5986, "lon": -71.1914, "alt": 4800, "tipo": "Santuario", "emoji": "🏔️", "descripcion": "Misa de Ukukus"},
    
    # GLACIAR
    "ColquePunku": {"lat": -13.5192, "lon": -71.2067, "alt": 5200, "tipo": "Glaciar", "emoji": "❄️", "descripcion": "Ascenso nocturno ritual"},
    
    # LOMADA
    "MachuCruz": {"lat": -13.5900, "lon": -71.1850, "alt": 4900, "tipo": "Cruz", "emoji": "✝️", "descripcion": "Pausa para maíz y queso"},
    "Yanaqocha": {"lat": -13.5850, "lon": -71.1800, "alt": 4850, "tipo": "Laguna", "emoji": "💧", "descripcion": "Despedida"},
    "Yanaqancha": {"lat": -13.5800, "lon": -71.1750, "alt": 4750, "tipo": "Descanso", "emoji": "😴", "descripcion": "Descanso 4h"},
    "QespiCruz": {"lat": -13.5700, "lon": -71.1650, "alt": 4600, "tipo": "Cruz", "emoji": "🎵", "descripcion": "Canto a medianoche"},
    "IntiLloksimuy": {"lat": -13.5600, "lon": -71.1550, "alt": 4500, "tipo": "Solar", "emoji": "☀️", "descripcion": "Inti Alabado"},
    "Tayancani": {"lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "Pueblo", "emoji": "🏁", "descripcion": "Fin de la peregrinación"},
}

# ============================================================================
# RUTAS DE PEREGRINACIÓN
# ============================================================================
RUTA_VEHICULAR = ["Paucartambo", "Huancarani", "Ccatcca", "Ocongate", "Mahuayani"]
RUTA_LOMADA = ["SantuarioQoylluriti", "MachuCruz", "Yanaqocha", "Yanaqancha", "QespiCruz", "IntiLloksimuy", "Tayancani"]

# ============================================================================
# TOP 10 PREGUNTAS
# ============================================================================
TOP_10_PREGUNTAS = [
    "¿Qué es la fiesta del Señor de Qoyllur Rit'i?",
    "¿Dónde queda el santuario?",
    "¿Quiénes son los ukukus?",
    "¿Qué actividades hay cada día?",
    "¿Dónde se hace la misa de ukukus?",
    "¿Qué es la Lomada?",
    "¿Quiénes participan en la peregrinación?",
    "¿Dónde está el glaciar Colque Punku?",
    "¿Cuándo suben al glaciar?",
    "¿Qué danzas hay en la festividad?"
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
# MAPA 100% FUNCIONAL - SIN MAPBOX, SOLO PLOTLY GRATUITO
# ============================================================================
def crear_mapa_funcional(tipo_ruta="todas"):
    """Mapa que SIEMPRE funciona - usa estilos Carto gratuitos"""
    
    fig = go.Figure()
    
    # ===== DICCIONARIO DE COLORES =====
    colores = {
        "Pueblo": "#1e3c72",
        "Iglesia": "#c0392b",
        "Cementerio": "#7f8c8d",
        "Plaza": "#e67e22",
        "Cruce": "#f39c12",
        "Inicio": "#2c3e50",
        "Santuario": "#f39c12",
        "Glaciar": "#3498db",
        "Cruz": "#27ae60",
        "Laguna": "#16a085",
        "Descanso": "#8e44ad",
        "Solar": "#f1c40f",
    }
    
    # ===== AGREGAR MARCADORES =====
    for nombre, lugar in LUGARES_SAGRADOS.items():
        color = colores.get(lugar["tipo"], "#e67e22")
        
        hover_text = f"""
        <b>{lugar['emoji']} {nombre}</b><br>
        <span style='font-weight:500;'>{lugar['tipo']}</span><br>
        <br>
        {lugar['descripcion']}<br>
        <br>
        📏 Altitud: {lugar['alt']:,} msnm<br>
        🧭 Coordenadas: {lugar['lat']:.4f}, {lugar['lon']:.4f}
        """
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers+text",
            marker=dict(
                size=12,
                color=color,
                symbol="marker"
            ),
            text=nombre,
            textposition="top center",
            textfont=dict(size=9, color="#1e3c72"),
            hovertemplate=hover_text + "<extra></extra>",
            showlegend=False
        ))
    
    # ===== AGREGAR RUTA VEHICULAR =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords = []
        for lugar in RUTA_VEHICULAR:
            if lugar in LUGARES_SAGRADOS:
                coords.append(LUGARES_SAGRADOS[lugar])
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords],
            lon=[c["lon"] for c in coords],
            mode="lines+markers",
            line=dict(width=4, color="#e67e22"),
            marker=dict(size=6, color="#e67e22"),
            name="🚌 Ruta vehicular"
        ))
    
    # ===== AGREGAR RUTA LOMADA =====
    if tipo_ruta in ["lomada", "todas"]:
        coords = []
        for lugar in RUTA_LOMADA:
            if lugar in LUGARES_SAGRADOS:
                coords.append(LUGARES_SAGRADOS[lugar])
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords],
            lon=[c["lon"] for c in coords],
            mode="lines+markers",
            line=dict(width=4, color="#8e44ad"),
            marker=dict(size=6, color="#8e44ad"),
            name="🚶 Lomada (24h)"
        ))
    
    # ===== CONFIGURACIÓN MAPA - 100% GRATUITO =====
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # ✅ SIEMPRE FUNCIONA, sin token
            center=dict(lat=-13.5, lon=-71.4),
            zoom=8,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e9ecef",
            borderwidth=1
        )
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD SIMPLE
# ============================================================================
def crear_perfil_altitud():
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
        title="⛰️ Perfil de altitud de la peregrinación",
        xaxis_title="Distancia (km)",
        yaxis_title="Altitud (msnm)",
        height=400,
        hovermode="x unified",
        plot_bgcolor="white"
    )
    return fig

# ============================================================================
# APP PRINCIPAL
# ============================================================================
def main():
    
    # ===== HEADER =====
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 32px;">
        <div style="font-size: 4.5rem;">🏔️</div>
        <div>
            <h1 style="margin: 0;">Qoyllur Rit'i</h1>
            <p style="margin: 8px 0 0 0; color: #5d6d7e; font-size: 1.2rem;">
                Peregrinación al Señor de Qoyllur Rit'i · Sinakara, Cusco
            </p>
            <div style="display: flex; gap: 12px; margin-top: 12px;">
                <span class="badge-andino">🙌 Para peregrinos</span>
                <span class="badge-andino">📖 Para investigadores</span>
                <span class="badge-andino">🏔️ Para viajeros</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("""
        ### 📿 Sobre la festividad
        
        **Qoyllur Rit'i** (quechua: *Nieve brillante*) es una de las peregrinaciones andinas más grandes de los Andes.
        
        **🗓️ Cuándo:** 58 días después del Miércoles de Ceniza  
        **⛰️ Dónde:** Santuario de Sinakara, Cusco (4,800 - 5,200 msnm)  
        **👥 Quiénes:** Ocho naciones, lideradas por la Nación Paucartambo
        """)
        
        st.markdown("---")
        st.info("""
        **🗺️ Mapa gratuito**  
        El mapa usa estilos Carto, 100% funcional sin necesidad de token.
        """)
    
    # ===== TABS =====
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa", "⛰️ Perfil"])
    
    # ===== TAB 1: PREGUNTAS =====
    with tab1:
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando sabiduría ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pregunta = st.selectbox(
                "Preguntas frecuentes:",
                options=[""] + TOP_10_PREGUNTAS,
                format_func=lambda x: "🎯 Elige una pregunta..." if x == "" else x
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
                <div style="font-size: 1.3rem; font-weight: 600; color: #1e3c72; margin-bottom: 16px;">
                    {pregunta}
                </div>
                <div style="font-size: 1.1rem; line-height: 1.8;">
                    {respuesta}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TAB 2: MAPA 100% FUNCIONAL =====
    with tab2:
        st.markdown("### 🗺️ Lugares sagrados de la peregrinación")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_ruta = st.radio(
                "Mostrar rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True
            )
        
        # Generar mapa - ¡SIEMPRE FUNCIONA!
        mapa = crear_mapa_funcional(tipo_ruta.lower())
        st.plotly_chart(mapa, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares", len(LUGARES_SAGRADOS))
        with col2:
            st.metric("🚌 Ruta vehicular", "85 km")
        with col3:
            st.metric("🚶 Lomada", "35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        
        # Lista de lugares
        with st.expander("📍 Ver lista de lugares sagrados"):
            df = pd.DataFrame([
                {"Lugar": nombre, 
                 "Tipo": d["tipo"], 
                 "Altitud": f"{d['alt']} msnm",
                 "Descripción": d["descripcion"]}
                for nombre, d in LUGARES_SAGRADOS.items()
            ]).sort_values("Lugar")
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # ===== TAB 3: PERFIL =====
    with tab3:
        st.markdown("### ⛰️ Perfil de altitud")
        perfil = crear_perfil_altitud()
        st.plotly_chart(perfil, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Salida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📈 Desnivel", "+2,300 m")
        with col4:
            st.metric("🎯 Llegada", "Tayancani", "3,800 msnm")
    
    # ===== FOOTER =====
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 48px; margin-bottom: 24px;">
            <span style="color: #1e3c72;">🙌 Para todos los públicos</span>
            <span style="color: #7f8c8d;">•</span>
            <span style="color: #1e3c72;">📚 Conocimiento libre</span>
            <span style="color: #7f8c8d;">•</span>
            <span style="color: #1e3c72;">🏔️ Cultura viva</span>
        </div>
        <div style="font-size: 0.85rem; color: #95a5a6;">
            Qoyllur Rit'i Explorer · Código abierto · 100% local · Raspberry Pi 5
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()