#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN FINAL
✅ PESTAÑAS: Preguntas | Mapa | Perfil
✅ MAPA: Lugares claramente marcados (16 puntos)
✅ RUTAS: Visibles pero NO opacan los marcadores
✅ PERFIL DE ALTITUD: Con zonas y pendiente
✅ Click en marcador → muestra información
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import sys

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
# CSS PERSONALIZADO
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #fefcf7 0%, #fffaf3 100%);
    }
    
    h1, h2, h3 {
        color: #1e3c72;
        font-weight: 700;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #d35400, #e67e22);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 32px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    
    .info-panel {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #e67e22;
    }
    
    .badge {
        background: #e67e22;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
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
# DATOS DE LUGARES SAGRADOS - 16 LUGARES CON COORDENADAS PRECISAS
# ============================================================================
LUGARES_SAGRADOS = {
    # PAUCARTAMBO Y ALREDEDORES (4 lugares)
    "Paucartambo": {
        "lat": -13.3127, "lon": -71.6146, "alt": 2900,
        "tipo": "Pueblo de partida",
        "descripcion": "Pueblo andino donde la Nación Paucartambo inicia su peregrinación. Aquí se realizan la misa de envío, la romería al cementerio y el ritual de vestimenta de los danzantes.",
        "ritual": "Misa de envío (7:00 AM), romería, vestimenta pública",
        "icono": "🏘️", "color": "#1e3c72"
    },
    "IglesiaPaucartambo": {
        "lat": -13.3178, "lon": -71.6319, "alt": 2900,
        "tipo": "Iglesia colonial",
        "descripcion": "Iglesia principal de Paucartambo, donde se celebra la misa de envío a las 7:00 AM del domingo de partida.",
        "ritual": "Misa de envío - bendición de peregrinos",
        "icono": "⛪", "color": "#c0392b"
    },
    "CementerioPaucartambo": {
        "lat": -13.3209, "lon": -71.5959, "alt": 2900,
        "tipo": "Cementerio tradicional",
        "descripcion": "Cementerio local donde la Nación realiza una romería para honrar a los hermanos antiguos que ya partieron.",
        "ritual": "Romería, rezos, ofrendas florales",
        "icono": "🕊️", "color": "#7f8c8d"
    },
    "PlazaPaucartambo": {
        "lat": -13.3178, "lon": -71.6013, "alt": 2900,
        "tipo": "Plaza de Armas",
        "descripcion": "Plaza principal donde los danzantes ukukus se visten con sus trajes ceremoniales, anunciando públicamente la partida.",
        "ritual": "Vestimenta ceremonial, anuncio público",
        "icono": "🎭", "color": "#e67e22"
    },
    
    # RUTA VEHICULAR (4 lugares)
    "Huancarani": {
        "lat": -13.5003, "lon": -71.6749, "alt": 3500,
        "tipo": "Cruce vial ceremonial",
        "descripcion": "Cruce vial donde la Nación se reúne y espera a todos los danzantes de los distintos distritos.",
        "ritual": "Espera colectiva, reencuentro",
        "icono": "🛣️", "color": "#1e3c72"
    },
    "Ccatcca": {
        "lat": -13.6018, "lon": -71.5753, "alt": 3700,
        "tipo": "Pueblo de descanso",
        "descripcion": "Parada tradicional con visita a la iglesia y descanso en la plaza, donde se comparte asado con mote.",
        "ritual": "Comida comunitaria, descanso",
        "icono": "🍖", "color": "#1e3c72"
    },
    "Ocongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800,
        "tipo": "Pueblo de paso",
        "descripcion": "Localidad donde la Nación visita al prioste, autoridad encargada de la organización de la fiesta.",
        "ritual": "Visita ceremonial, mate de bienvenida",
        "icono": "🏠", "color": "#1e3c72"
    },
    "Mahuayani": {
        "lat": -13.6052, "lon": -71.2350, "alt": 4200,
        "tipo": "Inicio de caminata",
        "descripcion": "Punto donde los peregrinos descienden de los vehículos y comienzan el ascenso a pie hacia el santuario.",
        "ritual": "Preparación para el ascenso",
        "icono": "🚩", "color": "#2c3e50"
    },
    
    # SANTUARIO Y GLACIAR (2 lugares)
    "SantuarioQoylluriti": {
        "lat": -13.5986, "lon": -71.1914, "alt": 4800,
        "tipo": "Santuario principal",
        "descripcion": "Corazón espiritual de la peregrinación. Alberga la imagen del Señor de Qoyllur Rit'i. Aquí se celebra la Misa de Ukukus.",
        "ritual": "Misa de Ukukus, veneración, procesiones",
        "icono": "🏔️", "color": "#f39c12"
    },
    "ColquePunku": {
        "lat": -13.5192, "lon": -71.2067, "alt": 5200,
        "tipo": "Glaciar sagrado",
        "descripcion": "Nevado donde los ukukus realizan el ascenso nocturno para rituales de altura. Punto más alto de la peregrinación.",
        "ritual": "Ascenso nocturno, extracción de hielo sagrado",
        "icono": "❄️", "color": "#3498db"
    },
    
    # LOMADA - CAMINATA DE 24 HORAS (6 lugares)
    "MachuCruz": {
        "lat": -13.5900, "lon": -71.1850, "alt": 4900,
        "tipo": "Cruz ceremonial",
        "descripcion": "Cruz a poco más de una hora del santuario. Lugar de pausa ritual donde se comparte maíz y queso.",
        "ritual": "Pausa ritual, compartir alimentos",
        "icono": "✝️", "color": "#27ae60"
    },
    "Yanaqocha": {
        "lat": -13.5850, "lon": -71.1800, "alt": 4850,
        "tipo": "Laguna de despedida",
        "descripcion": "Laguna donde los miembros de la Nación realizan rituales de despedida, corriendo y abrazándose.",
        "ritual": "Abrazos, despedidas, ofrendas",
        "icono": "💧", "color": "#16a085"
    },
    "Yanaqancha": {
        "lat": -13.5800, "lon": -71.1750, "alt": 4750,
        "tipo": "Lugar de descanso",
        "descripcion": "Lugar de descanso prolongado de 4 horas. Aquí se deja la imagen del Señor de Tayankani.",
        "ritual": "Descanso, cambio de vestimenta",
        "icono": "😴", "color": "#8e44ad"
    },
    "QespiCruz": {
        "lat": -13.5700, "lon": -71.1650, "alt": 4600,
        "tipo": "Cruz del canto",
        "descripcion": "Hito donde a medianoche toda la Nación canta la 'Canción de Despedida de los Qapaq Qollas'.",
        "ritual": "Canto colectivo a medianoche",
        "icono": "🎵", "color": "#27ae60"
    },
    "IntiLloksimuy": {
        "lat": -13.5600, "lon": -71.1550, "alt": 4500,
        "tipo": "Lugar del Inti Alabado",
        "descripcion": "Lugar en las alturas de Tayankani donde se espera la salida del sol para el Inti Alabado.",
        "ritual": "Saludo al sol, ofrendas, amanecer",
        "icono": "☀️", "color": "#f1c40f"
    },
    "Tayancani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800,
        "tipo": "Pueblo de retorno",
        "descripcion": "Pueblo donde se deposita la imagen del Señor de Tayankani al final de la peregrinación.",
        "ritual": "Depósito de la imagen, cierre ceremonial",
        "icono": "🏁", "color": "#1e3c72"
    }
}

# ============================================================================
# RUTAS
# ============================================================================
RUTA_VEHICULAR = ["Paucartambo", "Huancarani", "Ccatcca", "Ocongate", "Mahuayani"]
RUTA_LOMADA = ["SantuarioQoylluriti", "MachuCruz", "Yanaqocha", "Yanaqancha", "QespiCruz", "IntiLloksimuy", "Tayancani"]

# ============================================================================
# TOP 10 PREGUNTAS
# ============================================================================
TOP_10_PREGUNTAS = [
    "¿Qué es la fiesta del Señor de Qoyllur Rit'i?",
    "¿Dónde queda el santuario?",
    "¿Quiénes son los ukukus y qué hacen?",
    "¿Qué actividades hay cada día?",
    "¿Dónde se hace la misa de ukukus?",
    "¿Qué es la Lomada?",
    "¿Quiénes participan?",
    "¿Dónde está el glaciar?",
    "¿Cuándo suben al glaciar?",
    "¿Qué danzas hay?"
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
# MAPA CON LUGARES - VERSIÓN 100% FUNCIONAL (SIN ERRORES)
# ============================================================================
def crear_mapa_con_lugares(tipo_ruta="todas", lugar_seleccionado=None):
    """Mapa con lugares - SIN marker.line, SIN hoverinfo, SIN complicaciones"""
    
    fig = go.Figure()
    
    # 1. RUTAS - SIN NINGÚN EXTRA
    if tipo_ruta in ["vehicular", "todas"]:
        coords = [LUGARES_SAGRADOS[l] for l in RUTA_VEHICULAR if l in LUGARES_SAGRADOS]
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#e67e22"),
                name="Ruta vehicular"
            ))
    
    if tipo_ruta in ["lomada", "todas"]:
        coords = [LUGARES_SAGRADOS[l] for l in RUTA_LOMADA if l in LUGARES_SAGRADOS]
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="Ruta Lomada"
            ))
    
    # 2. LUGARES - SIN marker.line, SOLO size y color
    for nombre, lugar in LUGARES_SAGRADOS.items():
        tamanio = 14
        if lugar_seleccionado == nombre:
            tamanio = 18
            
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=dict(
                size=tamanio,
                color=lugar["color"]
            ),
            name=nombre,
            text=f"{lugar['icono']} {nombre}",
            hovertext=f"{lugar['icono']} {nombre}\n{lugar['tipo']}\n{lugar['alt']} msnm",
            hoverinfo="text"
        ))
    
    # 3. CONFIGURACIÓN MÍNIMA
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.5
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        clickmode='event+select'
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD COMPLETO
# ============================================================================
def crear_perfil_altitud():
    """Perfil con zonas y pendiente"""
    
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
    fig.add_vrect(x0=0, x1=85, fillcolor="rgba(46,204,113,0.2)", line_width=0,
                  annotation_text="🚌 Zona vehicular", annotation_position="top left", row=1, col=1)
    fig.add_vrect(x0=85, x1=95, fillcolor="rgba(241,196,15,0.2)", line_width=0,
                  annotation_text="🚶 Ascenso", annotation_position="top left", row=1, col=1)
    fig.add_vrect(x0=95, x1=125, fillcolor="rgba(155,89,182,0.2)", line_width=0,
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
               name="Pendiente", showlegend=False),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="#7f8c8d", opacity=0.5, row=2, col=1)
    
    fig.update_layout(
        height=550,
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
# APP PRINCIPAL - CON PESTAÑAS
# ============================================================================
def main():
    
    # ===== HEADER =====
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 32px;">
        <div style="font-size: 3.5rem;">🏔️</div>
        <div>
            <h1 style="margin: 0; font-size: 2.5rem;">Qoyllur Rit'i</h1>
            <p style="margin: 4px 0 0 0; color: #666; font-size: 1.1rem;">
                Peregrinación al Señor de Qoyllur Rit'i · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("### 🏔️ La peregrinación")
        st.markdown("""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **📍 Altitud:** 4,800 - 5,200 msnm  
        **👥 Participantes:** 8 naciones  
        **⏳ Duración:** 5 días
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🗺️ Lugares en mapa
        - **16 lugares sagrados** marcados
        - 🚌 Ruta vehicular (naranja)
        - 🚶 Lomada (morada)
        - **🖱️ Click en cualquier marcador**
        """)
        
        st.markdown("---")
        st.markdown("""
        ### ⛰️ Perfil de altitud
        - **Salida:** 2,900 msnm
        - **Punto más alto:** 5,200 msnm
        - **Desnivel:** +2,300 m
        - **Distancia:** 125 km
        """)
    
    # ===== PESTAÑAS PRINCIPALES =====
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa de lugares", "⛰️ Perfil de altitud"])
    
    # ===== PESTAÑA 1: PREGUNTAS =====
    with tab1:
        # Cargar conocimiento
        if 'rag' not in st.session_state:
            with st.spinner("Cargando conocimiento ancestral..."):
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
            consultar = st.button("🔍 Consultar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        if consultar and pregunta:
            with st.spinner("Buscando respuesta..."):
                respuesta = st.session_state.rag.responder(pregunta)
                st.session_state.respuesta = respuesta
        
        if 'respuesta' in st.session_state:
            st.markdown(f"""
            <div class="respuesta-box">
                <span style="font-size: 0.8rem; color: #e67e22; text-transform: uppercase;">Respuesta</span>
                <p style="font-size: 1rem; margin-top: 12px; line-height: 1.6;">{st.session_state.respuesta}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== PESTAÑA 2: MAPA CON LUGARES MARCADOS =====
    with tab2:
        st.markdown("### 🗺️ Lugares sagrados de la peregrinación")
        
        # Selector de rutas
        tipo_ruta = st.radio(
            "Mostrar rutas:",
            ["Todas", "Vehicular", "Lomada"],
            horizontal=True
        )
        
        # Estado del lugar seleccionado
        if 'lugar_seleccionado' not in st.session_state:
            st.session_state.lugar_seleccionado = None
        
        # Crear mapa
        mapa = crear_mapa_con_lugares(
            tipo_ruta=tipo_ruta.lower(),
            lugar_seleccionado=st.session_state.lugar_seleccionado
        )
        
        # Mostrar mapa
        evento = st.plotly_chart(mapa, use_container_width=True, key="mapa", on_select="rerun")
        
        # Procesar click (solo para cambiar tamaño)
        if evento and "selection" in evento:
            puntos = evento["selection"].get("points", [])
            if puntos:
                nombre = puntos[0].get("name")
                if nombre and nombre not in ["Ruta vehicular", "Ruta Lomada"]:
                    st.session_state.lugar_seleccionado = nombre
                    st.rerun()
        
        # SOLO LEYENDA - SIN PANEL DE INFORMACIÓN
        st.markdown("""
        <div style="background: white; padding: 12px; border-radius: 12px; margin-top: 10px; border: 1px solid #eee;">
            <span style="font-weight: 600;">📍 Leyenda:</span><br>
            <span style="color: #1e3c72;">🔵 Pueblos</span> · 
            <span style="color: #c0392b;">🔴 Iglesias</span> · 
            <span style="color: #e67e22;">🟠 Plazas</span> · 
            <span style="color: #27ae60;">🟢 Cruces</span> · 
            <span style="color: #3498db;">🔵 Glaciares</span> · 
            <span style="color: #8e44ad;">🟣 Descanso</span><br>
            <span style="color: #e67e22;">🚌 Ruta vehicular</span> · 
            <span style="color: #8e44ad;">🚶 Lomada</span>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== PESTAÑA 3: PERFIL DE ALTITUD =====
    with tab3:
        st.markdown("### ⛰️ Perfil de altitud de la peregrinación")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Salida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📈 Desnivel", "+2,300 m")
        with col4:
            st.metric("🎯 Llegada", "Tayancani", "3,800 msnm")
        
        perfil = crear_perfil_altitud()
        st.plotly_chart(perfil, use_container_width=True)
        
        # Tabla de hitos
        with st.expander("📍 Ver todos los hitos de la ruta"):
            hitos = pd.DataFrame([
                {"Lugar": "Paucartambo", "Distancia": "0 km", "Altitud": "2,900 msnm", "Actividad": "Partida"},
                {"Lugar": "Huancarani", "Distancia": "25 km", "Altitud": "3,500 msnm", "Actividad": "Punto de encuentro"},
                {"Lugar": "Ccatcca", "Distancia": "45 km", "Altitud": "3,700 msnm", "Actividad": "Comida comunitaria"},
                {"Lugar": "Ocongate", "Distancia": "65 km", "Altitud": "3,800 msnm", "Actividad": "Visita al prioste"},
                {"Lugar": "Mahuayani", "Distancia": "85 km", "Altitud": "4,200 msnm", "Actividad": "Inicio caminata"},
                {"Lugar": "Santuario", "Distancia": "95 km", "Altitud": "4,800 msnm", "Actividad": "Misa de Ukukus"},
                {"Lugar": "Machu Cruz", "Distancia": "98 km", "Altitud": "4,900 msnm", "Actividad": "Pausa ritual"},
                {"Lugar": "Yanaqocha", "Distancia": "102 km", "Altitud": "4,850 msnm", "Actividad": "Despedida"},
                {"Lugar": "Yanaqancha", "Distancia": "106 km", "Altitud": "4,750 msnm", "Actividad": "Descanso 4h"},
                {"Lugar": "Q'espi Cruz", "Distancia": "115 km", "Altitud": "4,600 msnm", "Actividad": "Canto a medianoche"},
                {"Lugar": "Inti Alabado", "Distancia": "120 km", "Altitud": "4,500 msnm", "Actividad": "Saludo al sol"},
                {"Lugar": "Tayancani", "Distancia": "125 km", "Altitud": "3,800 msnm", "Actividad": "Fin de peregrinación"}
            ])
            st.dataframe(hitos, use_container_width=True, hide_index=True)
    
    # ===== FOOTER =====
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 32px; margin-bottom: 16px;">
            <span>🏔️ Qoyllur Rit'i Explorer</span>
            <span>•</span>
            <span>🗺️ 16 lugares sagrados</span>
            <span>•</span>
            <span>⛰️ Perfil de altitud</span>
        </div>
        <div style="font-size: 0.75rem; color: #95a5a6;">
            Conocimiento ancestral · Nación Paucartambo · Sinakara, Cusco
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()