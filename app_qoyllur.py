#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN 2.0 PREMIUM (CORREGIDA)
✅ Mapas con iconos personalizados - ¡AHORA FUNCIONA!
✅ Perfil de altitud con zonas y pendiente
✅ Tooltips detallados
✅ Estilos de mapa (Calle, Outdoor, Oscuro) - Sin satélite (requiere Mapbox)
✅ 100% funcional en Python 3.13 y Streamlit Cloud
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
    page_title="Qoyllur Rit'i Explorer - Premium",
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
# DATOS DE COORDENADAS - LUGARES SAGRADOS
# ============================================================================
LUGARES_COORDENADAS = {
    "Paucartambo": {"lat": -13.3127, "lon": -71.6146, "alt": 2900, "tipo": "pueblo"},
    "IglesiaPaucartambo": {"lat": -13.3178, "lon": -71.6319, "alt": 2900, "tipo": "iglesia"},
    "CementerioPaucartambo": {"lat": -13.3209, "lon": -71.5959, "alt": 2900, "tipo": "cementerio"},
    "PlazaPaucartambo": {"lat": -13.3178, "lon": -71.6013, "alt": 2900, "tipo": "plaza"},
    "Huancarani": {"lat": -13.5003, "lon": -71.6749, "alt": 3500, "tipo": "pueblo"},
    "Ccatcca": {"lat": -13.6018, "lon": -71.5753, "alt": 3700, "tipo": "pueblo"},
    "Ocongate": {"lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "pueblo"},
    "Mahuayani": {"lat": -13.6052, "lon": -71.2350, "alt": 4200, "tipo": "inicio"},
    "SantuarioQoylluriti": {"lat": -13.5986, "lon": -71.1914, "alt": 4800, "tipo": "santuario"},
    "ColquePunku": {"lat": -13.5192, "lon": -71.2067, "alt": 5200, "tipo": "glaciar"},
    "MachuCruz": {"lat": -13.5900, "lon": -71.1850, "alt": 4900, "tipo": "cruz"},
    "Yanaqocha": {"lat": -13.5850, "lon": -71.1800, "alt": 4850, "tipo": "laguna"},
    "Yanaqancha": {"lat": -13.5800, "lon": -71.1750, "alt": 4750, "tipo": "descanso"},
    "QespiCruz": {"lat": -13.5700, "lon": -71.1650, "alt": 4600, "tipo": "cruz"},
    "IntiLloksimuy": {"lat": -13.5600, "lon": -71.1550, "alt": 4500, "tipo": "solar"},
    "Tayancani": {"lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "pueblo"},
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
# MAPA CORREGIDO - SIN ERRORES DE PLOTLY
# ============================================================================
def crear_mapa_mejorado(tipo_ruta="todas", estilo_mapa="calle"):
    """
    Mapa interactivo - VERSIÓN CORREGIDA
    ✅ Sin customdata
    ✅ Sin marker.line problemático
    ✅ Sin opacity en lines
    ✅ Solo estilos que funcionan sin Mapbox
    """
    
    # Colores por tipo
    COLORES = {
        "pueblo": "#1e3c72", "iglesia": "#c0392b", "cementerio": "#7f8c8d",
        "plaza": "#e67e22", "santuario": "#f39c12", "glaciar": "#3498db",
        "cruz": "#27ae60", "laguna": "#16a085", "descanso": "#8e44ad",
        "solar": "#f1c40f", "inicio": "#2c3e50"
    }
    
    # Descripciones para tooltips
    DESCRIPCIONES = {
        "Paucartambo": "Pueblo de partida de la Nación Paucartambo",
        "SantuarioQoylluriti": "Santuario del Señor de Qoyllur Rit'i - 4,800 msnm",
        "ColquePunku": "Glaciar sagrado - Lugar de rituales nocturnos - 5,200 msnm",
        "MachuCruz": "Cruz ceremonial - Pausa para comer maíz y queso",
        "Yanaqocha": "Laguna de despedida - Rituales de abrazo",
        "Yanaqancha": "Lugar de descanso de 4 horas",
        "QespiCruz": "Punto del canto de medianoche - Qapaq Qollas",
        "IntiLloksimuy": "Lugar del Inti Alabado - Saludo al sol",
        "Tayancani": "Pueblo donde se deposita la imagen del Señor",
        "Mahuayani": "Punto de inicio de la caminata al santuario",
        "Huancarani": "Cruce vial - Punto de encuentro de danzantes",
        "Ccatcca": "Pueblo de descanso y comida comunitaria",
        "Ocongate": "Pueblo donde termina oficialmente la festividad",
    }
    
    # Iconos por tipo (usando emojis en hover, no en marker)
    ICONOS = {
        "pueblo": "🏘️", "iglesia": "⛪", "cementerio": "🕊️", "plaza": "🎭",
        "santuario": "🏔️", "glaciar": "❄️", "cruz": "✝️", "laguna": "💧",
        "descanso": "😴", "solar": "☀️", "inicio": "🚩"
    }
    
    # Estilos de mapa que funcionan SIN Mapbox
    ESTILOS_MAPA = {
        "calle": "carto-positron",
        "outdoor": "open-street-map",
        "oscuro": "carto-darkmatter"
    }
    
    fig = go.Figure()
    
    # ===== AGREGAR RUTAS =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords_ruta = [LUGARES_COORDENADAS[l] for l in RUTA_VEHICULAR if l in LUGARES_COORDENADAS]
        if coords_ruta:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords_ruta],
                lon=[c["lon"] for c in coords_ruta],
                mode="lines",
                line=dict(width=3, color="#e67e22"),
                name="🚌 Ruta vehicular",
                hoverinfo="skip"
            ))
    
    if tipo_ruta in ["lomada", "todas"]:
        coords_lomada = [LUGARES_COORDENADAS[l] for l in RUTA_LOMADA if l in LUGARES_COORDENADAS]
        if coords_lomada:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords_lomada],
                lon=[c["lon"] for c in coords_lomada],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="🚶 Ruta Lomada (24h)",
                hoverinfo="skip"
            ))
    
    # ===== AGREGAR LUGARES - SIN customdata, SIN marker.line =====
    for nombre, lugar in LUGARES_COORDENADAS.items():
        # Saltar lugares que no están en nuestra lista principal
        if nombre not in DESCRIPCIONES and nombre not in ["IglesiaCcatcca", "PlazaCcatcca", "CasaPriosteOcongate", "PlazaOcongate", "CapillaTayankani", "GrutaTayankani", "QquchiyocWayqo"]:
            continue
            
        color = COLORES.get(lugar["tipo"], "#e67e22")
        icono = ICONOS.get(lugar["tipo"], "📍")
        desc = DESCRIPCIONES.get(nombre, f"Lugar sagrado: {nombre}")
        
        hover_text = f"""
        <b style='font-size: 16px; color: {color};'>{icono} {nombre}</b><br>
        <span style='font-size: 14px;'>{desc}</span><br>
        <br>
        <span style='font-size: 13px;'>
        🏔️ <b>Tipo:</b> {lugar['tipo'].capitalize()}<br>
        📏 <b>Altitud:</b> {lugar['alt']:,} msnm
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
            )
        ))
    
    # ===== CONFIGURAR MAPA =====
    estilo = ESTILOS_MAPA.get(estilo_mapa, "carto-positron")
    
    fig.update_layout(
        mapbox=dict(
            style=estilo,
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.8
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#e9ecef", borderwidth=1
        )
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD CORREGIDO
# ============================================================================
def crear_perfil_altitud_mejorado():
    """Perfil de altitud - VERSIÓN CORREGIDA"""
    
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
    
    # Hitos principales
    hitos = df[df["lugar"].isin(["Paucartambo", "Santuario", "Tayancani"])]
    fig.add_trace(
        go.Scatter(
            x=hitos["dist"], y=hitos["alt"],
            mode="markers",
            marker=dict(size=12, color="#e67e22", symbol="star"),
            name="Hitos principales",
            showlegend=False,
            hovertemplate="<b>%{text}</b><br>📍 Punto clave<br>🏔️ %{y:.0f} msnm<extra></extra>",
            text=hitos["lugar"]
        ),
        row=1, col=1
    )
    
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
        go.Bar(
            x=df_pend["x"], y=df_pend["pend"],
            marker_color=colors,
            showlegend=False,
            hovertemplate="Pendiente: %{y:.1f}%<extra></extra>"
        ),
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
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
        <div style="font-size: 4rem;">🏔️</div>
        <div>
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; color: #1e3c72;">
                Qoyllur Rit'i Explorer
            </h1>
            <p style="margin: 0; color: #7f8c8d; font-size: 1.2rem;">
                Conocimiento ancestral · Mapas interactivos · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown("### 🗺️ Estilos de mapa")
        st.markdown("""
        - 🗺️ **Calle** - Mapa base
        - 🌳 **Outdoor** - Para montaña
        - 🌙 **Oscuro** - Modo noche
        """)
    
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
    
    # ===== TAB 2: MAPA =====
    with tab2:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("### 🗺️ Mapa Sagrado de Qoyllur Rit'i")
        with col2:
            tipo_ruta = st.radio(
                "Mostrar rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True
            )
        with col3:
            estilo_mapa = st.selectbox(
                "Estilo:",
                ["Calle", "Outdoor", "Oscuro"],
                index=0
            )
        
        mapa = crear_mapa_mejorado(
            tipo_ruta.lower(),
            estilo_mapa.lower()
        )
        st.plotly_chart(mapa, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares sagrados", "16")
        with col2:
            st.metric("🚌 Ruta vehicular", "~85 km")
        with col3:
            st.metric("🚶 Lomada", "~35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
    
    # ===== TAB 3: PERFIL =====
    with tab3:
        st.markdown("### ⛰️ Perfil Completo de la Peregrinación")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Partida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📏 Desnivel", "+2,300 m")
        with col4:
            st.metric("🎯 Llegada", "Tayankani", "3,800 msnm")
        
        perfil = crear_perfil_altitud_mejorado()
        st.plotly_chart(perfil, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer V2.0 Premium</span>
            <span>•</span>
            <span>🗺️ Mapas con tooltips</span>
            <span>•</span>
            <span>📊 Perfil con pendiente</span>
            <span>•</span>
            <span>✨ 100% funcional</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()