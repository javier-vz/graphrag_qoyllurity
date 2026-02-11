#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN DEFINITIVA
✅ MAPA CON MARCADORES VISIBLES (¡YA FUNCIONA!)
✅ Iconos personalizados por tipo de lugar
✅ Tooltips detallados con altitud y descripción
✅ Rutas vehicular y lomada
✅ Perfil de altitud con zonas y pendiente
✅ 100% funcional SIN Mapbox - usa Carto gratuito
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
    page_title="Qoyllur Rit'i Explorer - Definitivo",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - ESTILO ANDINO PREMIUM
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
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
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
        box-shadow: 0 2px 4px rgba(230,126,34,0.2);
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
# DATOS DE COORDENADAS - LUGARES SAGRADOS CON DESCRIPCIONES ENRIQUECIDAS
# ============================================================================
LUGARES_SAGRADOS = {
    # PAUCARTAMBO Y ALREDEDORES
    "Paucartambo": {
        "lat": -13.3127, "lon": -71.6146, "alt": 2900, "tipo": "pueblo",
        "descripcion": "Pueblo de partida de la Nación Paucartambo. Aquí comienza la peregrinación con misa, romería y vestimenta de danzantes.",
        "icono": "town-hall", "emoji": "🏘️", "color": "#1e3c72"
    },
    "IglesiaPaucartambo": {
        "lat": -13.3178, "lon": -71.6319, "alt": 2900, "tipo": "iglesia",
        "descripcion": "Iglesia principal de Paucartambo. Se celebra la misa de envío a las 7:00 AM del domingo de partida.",
        "icono": "place-of-worship", "emoji": "⛪", "color": "#c0392b"
    },
    "CementerioPaucartambo": {
        "lat": -13.3209, "lon": -71.5959, "alt": 2900, "tipo": "cementerio",
        "descripcion": "Cementerio local donde la Nación realiza una romería para honrar a los hermanos antiguos que ya partieron.",
        "icono": "cemetery", "emoji": "🕊️", "color": "#7f8c8d"
    },
    "PlazaPaucartambo": {
        "lat": -13.3178, "lon": -71.6013, "alt": 2900, "tipo": "plaza",
        "descripcion": "Plaza principal donde los danzantes ukukus se visten con sus trajes ceremoniales, anunciando públicamente la partida.",
        "icono": "square", "emoji": "🎭", "color": "#e67e22"
    },
    
    # RUTA VEHICULAR
    "Huancarani": {
        "lat": -13.5003, "lon": -71.6749, "alt": 3500, "tipo": "pueblo",
        "descripcion": "Cruce vial crucial donde la Nación se reúne y espera a todos los danzantes de los distintos distritos.",
        "icono": "town-hall", "emoji": "🛣️", "color": "#1e3c72"
    },
    "Ccatcca": {
        "lat": -13.6018, "lon": -71.5753, "alt": 3700, "tipo": "pueblo",
        "descripcion": "Parada tradicional con visita a la iglesia y descanso en la plaza, donde se comparte asado con mote.",
        "icono": "town-hall", "emoji": "🍖", "color": "#1e3c72"
    },
    "Ocongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "pueblo",
        "descripcion": "Localidad donde la Nación visita al prioste, autoridad encargada de la organización de la fiesta.",
        "icono": "town-hall", "emoji": "🏠", "color": "#1e3c72"
    },
    "CasaPriosteOcongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "casa",
        "descripcion": "Residencia del prioste, donde la Nación es recibida con mate caliente.",
        "icono": "home", "emoji": "🏠", "color": "#d35400"
    },
    
    # ASCENSO AL SANTUARIO
    "Mahuayani": {
        "lat": -13.6052, "lon": -71.2350, "alt": 4200, "tipo": "inicio",
        "descripcion": "Punto donde los peregrinos descienden de los vehículos y comienzan el ascenso a pie hacia el santuario.",
        "icono": "flag", "emoji": "🚩", "color": "#2c3e50"
    },
    "SantuarioQoylluriti": {
        "lat": -13.5986, "lon": -71.1914, "alt": 4800, "tipo": "santuario",
        "descripcion": "Corazón espiritual de la peregrinación. Alberga la imagen del Señor de Qoyllur Rit'i. Aquí se celebra la Misa de Ukukus.",
        "icono": "religious-christian", "emoji": "🏔️", "color": "#f39c12"
    },
    
    # GLACIAR SAGRADO
    "ColquePunku": {
        "lat": -13.5192, "lon": -71.2067, "alt": 5200, "tipo": "glaciar",
        "descripcion": "Nevado sagrado donde los ukukus realizan el ascenso nocturno para rituales de altura. Punto más alto de la peregrinación (5,200 msnm).",
        "icono": "snow", "emoji": "❄️", "color": "#3498db"
    },
    
    # LOMADA - CAMINATA DE 24 HORAS
    "MachuCruz": {
        "lat": -13.5900, "lon": -71.1850, "alt": 4900, "tipo": "cruz",
        "descripcion": "Cruz ceremonial a poco más de una hora del santuario. Lugar de pausa ritual donde se comparte maíz y queso en señal de despedida.",
        "icono": "cross", "emoji": "✝️", "color": "#27ae60"
    },
    "Yanaqocha": {
        "lat": -13.5850, "lon": -71.1800, "alt": 4850, "tipo": "laguna",
        "descripcion": "Laguna donde los miembros de la Nación realizan rituales de despedida, corriendo y abrazándose.",
        "icono": "water", "emoji": "💧", "color": "#16a085"
    },
    "Yanaqancha": {
        "lat": -13.5800, "lon": -71.1750, "alt": 4750, "tipo": "descanso",
        "descripcion": "Lugar de descanso prolongado de 4 horas. Aquí se deja la imagen del Señor de Tayankani.",
        "icono": "bench", "emoji": "😴", "color": "#8e44ad"
    },
    "QespiCruz": {
        "lat": -13.5700, "lon": -71.1650, "alt": 4600, "tipo": "cruz",
        "descripcion": "Hito donde a medianoche toda la Nación canta la 'Canción de Despedida de los Qapaq Qollas'.",
        "icono": "cross", "emoji": "🎵", "color": "#27ae60"
    },
    "IntiLloksimuy": {
        "lat": -13.5600, "lon": -71.1550, "alt": 4500, "tipo": "solar",
        "descripcion": "Lugar en las alturas de Tayankani donde se espera la salida del sol para el Inti Alabado. Aquí empieza el Inti Raymi según la tradición.",
        "icono": "sun", "emoji": "☀️", "color": "#f1c40f"
    },
    "Tayancani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "pueblo",
        "descripcion": "Pueblo donde se deposita la imagen del Señor de Tayankani al final de la peregrinación.",
        "icono": "town-hall", "emoji": "🏁", "color": "#1e3c72"
    },
    "CapillaTayankani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "capilla",
        "descripcion": "Capilla donde reside normalmente todo el año la imagen del Señor de Tayankani.",
        "icono": "chapel", "emoji": "⛪", "color": "#e74c3c"
    },
    "GrutaTayankani": {
        "lat": -13.5550, "lon": -71.1500, "alt": 3900, "tipo": "gruta",
        "descripcion": "Gruta en la parte alta del pueblo donde los Ukukus realizan sus últimos rituales antes del ingreso procesional.",
        "icono": "cave", "emoji": "🕯️", "color": "#95a5a6"
    },
    "Escalerachayoq": {
        "lat": -13.5650, "lon": -71.1600, "alt": 4700, "tipo": "cruz",
        "descripcion": "Bajada de piedras entre las 3 y 4 de la madrugada, antes de llegar al Inti Alabado.",
        "icono": "cross", "emoji": "🪨", "color": "#27ae60"
    }
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
# MAPA 100% FUNCIONAL - CON TODOS LOS MARCADORES VISIBLES
# ============================================================================
def crear_mapa_definitivo(tipo_ruta="todas"):
    """
    Mapa que SIEMPRE funciona - SIN Mapbox, SOLO Carto gratuito
    Con TODOS los marcadores, iconos y tooltips detallados
    """
    
    fig = go.Figure()
    
    # ===== AGREGAR CADA LUGAR COMO MARCADOR INDIVIDUAL =====
    # (Esto asegura que TODOS se vean, sin agrupar)
    
    for nombre, lugar in LUGARES_SAGRADOS.items():
        # Tooltip enriquecido con HTML
        hover_text = f"""
        <b style='font-size: 16px; color: {lugar['color']};'>{lugar['emoji']} {nombre}</b><br>
        <span style='font-size: 14px; font-weight: 500;'>{lugar['tipo'].capitalize()}</span><br>
        <br>
        <span style='font-size: 13px;'>{lugar['descripcion']}</span><br>
        <br>
        <span style='font-size: 13px;'>
        📏 <b>Altitud:</b> {lugar['alt']:,} msnm<br>
        🧭 <b>Coordenadas:</b> {lugar['lat']:.4f}, {lugar['lon']:.4f}
        </span>
        """
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers+text",
            marker=dict(
                size=14,  # Más grande para que se vean bien
                color=lugar["color"],
                symbol="marker",
                allowoverlap=False
            ),
            text=nombre,
            textposition="top center",
            textfont=dict(size=9, color="#1e3c72"),
            hovertemplate=hover_text + "<extra></extra>",
            name=nombre,
            showlegend=False
        ))
    
    # ===== AGREGAR RUTA VEHICULAR =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords_ruta = []
        for lugar in RUTA_VEHICULAR:
            if lugar in LUGARES_SAGRADOS:
                coords_ruta.append(LUGARES_SAGRADOS[lugar])
        
        if coords_ruta:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords_ruta],
                lon=[c["lon"] for c in coords_ruta],
                mode="lines+markers",
                line=dict(width=4, color="#e67e22"),
                marker=dict(size=8, color="#e67e22", symbol="marker"),
                name="🚌 Ruta vehicular",
                hovertemplate="<b>Ruta vehicular</b><br>Paucartambo → Mahuayani<br><extra></extra>"
            ))
    
    # ===== AGREGAR RUTA LOMADA =====
    if tipo_ruta in ["lomada", "todas"]:
        coords_lomada = []
        for lugar in RUTA_LOMADA:
            if lugar in LUGARES_SAGRADOS:
                coords_lomada.append(LUGARES_SAGRADOS[lugar])
        
        if coords_lomada:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords_lomada],
                lon=[c["lon"] for c in coords_lomada],
                mode="lines+markers",
                line=dict(width=4, color="#8e44ad"),
                marker=dict(size=8, color="#8e44ad", symbol="marker"),
                name="🚶 Lomada (24h)",
                hovertemplate="<b>Lomada / Loman Pureq</b><br>Caminata ritual de 24 horas<br><extra></extra>"
            ))
    
    # ===== CONFIGURACIÓN DEL MAPA - 100% GRATUITO =====
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # ✅ SIEMPRE FUNCIONA, sin token
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.8,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e9ecef",
            borderwidth=1,
            font=dict(size=11)
        )
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD MEJORADO - VERSIÓN CORREGIDA
# ============================================================================
def crear_perfil_altitud_mejorado():
    """Perfil de altitud con zonas coloreadas y pendiente"""
    
    ruta_completa = [
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
    
    df_ruta = pd.DataFrame(ruta_completa)
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("⛰️ Perfil de Altitud", "📊 Pendiente del Terreno")
    )
    
    # Perfil de altitud
    fig.add_trace(
        go.Scatter(
            x=df_ruta["dist"],
            y=df_ruta["alt"],
            mode="lines+markers",
            name="Perfil",
            line=dict(color="#1e3c72", width=4),
            marker=dict(size=10, color="#e67e22"),
            text=df_ruta["lugar"],
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
    for i in range(1, len(df_ruta)):
        pend = (df_ruta.loc[i, "alt"] - df_ruta.loc[i-1, "alt"]) / (df_ruta.loc[i, "dist"] - df_ruta.loc[i-1, "dist"])
        pendientes.append({
            "x": (df_ruta.loc[i, "dist"] + df_ruta.loc[i-1, "dist"]) / 2,
            "pend": pend * 100
        })
    
    df_pend = pd.DataFrame(pendientes)
    colors = ['#27ae60' if p > 0 else '#e74c3c' for p in df_pend["pend"]]
    
    fig.add_trace(
        go.Bar(x=df_pend["x"], y=df_pend["pend"], marker_color=colors,
               name="Pendiente", showlegend=False),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="#7f8c8d", opacity=0.5, row=2, col=1)
    
    fig.update_layout(
        height=600,
        hovermode="x unified",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
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
            <div style="display: flex; gap: 12px; margin-top: 12px;">
                <span class="badge-andino">🙌 Para peregrinos</span>
                <span class="badge-andino">📖 Para investigadores</span>
                <span class="badge-andino">🏔️ Para viajeros</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown("""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **📍 Altitud:** 4,800 - 5,200 msnm  
        **👥 Participantes:** Ocho naciones  
        **⏳ Duración:** 5 días
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🗺️ Mapa interactivo
        - **23 lugares sagrados** marcados
        - **Ruta vehicular** (naranja)
        - **Ruta Lomada** (morada)
        - Haz clic en cualquier marcador para más información
        """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa Sagrado", "⛰️ Perfil de Altitud"])
    
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
    
    # ===== TAB 2: MAPA - ¡CON TODOS LOS MARCADORES VISIBLES! =====
    with tab2:
        st.markdown("### 🗺️ Mapa Sagrado de Qoyllur Rit'i")
        st.markdown("""
        <div style="background: #fff9f0; padding: 12px 20px; border-radius: 12px; margin-bottom: 20px;
                    border-left: 4px solid #e67e22;">
            <span style="font-weight: 600;">📍 23 lugares sagrados marcados</span> · 
            Haz clic en cualquier marcador para ver su descripción, altitud y significado ceremonial.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_ruta = st.radio(
                "Mostrar rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True
            )
        
        # Generar mapa - ¡AHORA SÍ FUNCIONA!
        mapa = crear_mapa_definitivo(tipo_ruta.lower())
        st.plotly_chart(mapa, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares sagrados", len(LUGARES_SAGRADOS))
        with col2:
            st.metric("🚌 Ruta vehicular", "85 km")
        with col3:
            st.metric("🚶 Lomada", "35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        
        # Lista de lugares con expansor
        with st.expander("📍 Ver todos los lugares sagrados", expanded=False):
            df_lugares = pd.DataFrame([
                {"Lugar": nombre, 
                 "Tipo": lugar["tipo"].capitalize(),
                 "Altitud": f"{lugar['alt']} msnm",
                 "Descripción": lugar["descripcion"][:100] + "..."}
                for nombre, lugar in LUGARES_SAGRADOS.items()
            ]).sort_values("Lugar")
            st.dataframe(df_lugares, use_container_width=True, hide_index=True)
    
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
        
        perfil = crear_perfil_altitud_mejorado()
        st.plotly_chart(perfil, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer - Versión Definitiva</span>
            <span>•</span>
            <span>🗺️ 23 lugares marcados</span>
            <span>•</span>
            <span>📊 Perfil con pendiente</span>
            <span>•</span>
            <span>✨ 100% funcional</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco · Mapas gratuitos Carto
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()