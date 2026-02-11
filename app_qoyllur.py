#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN DEFINITIVA
✅ Preguntas a la izquierda
✅ Mapa con lugares clickeables
✅ Panel de información a la derecha
✅ 100% funcional, sin errores
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .info-panel {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #e67e22;
        height: fit-content;
    }
    
    .badge {
        background: #e67e22;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
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
# DATOS DE LUGARES SAGRADOS
# ============================================================================
LUGARES_SAGRADOS = {
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
    "¿Qué actividades hay cada día de la peregrinación?",
    "¿Dónde se realiza la misa especial de los ukukus?",
    "¿Qué es la Lomada o caminata de 24 horas?",
    "¿Quiénes participan en la peregrinación?",
    "¿Dónde está el glaciar Colque Punku?",
    "¿Cuándo suben al glaciar y por qué?",
    "¿Qué danzas y músicas acompañan la festividad?"
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
# MAPA SIMPLE - CLICKEABLE
# ============================================================================
def crear_mapa(tipo_ruta="todas"):
    """Mapa simple con marcadores clickeables"""
    
    fig = go.Figure()
    
    # 1. RUTAS (detrás)
    if tipo_ruta in ["vehicular", "todas"]:
        coords = [LUGARES_SAGRADOS[l] for l in RUTA_VEHICULAR if l in LUGARES_SAGRADOS]
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
        coords = [LUGARES_SAGRADOS[l] for l in RUTA_LOMADA if l in LUGARES_SAGRADOS]
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="Ruta Lomada",
                hoverinfo="skip"
            ))
    
    # 2. LUGARES (encima)
    for nombre, lugar in LUGARES_SAGRADOS.items():
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=dict(
                size=12,
                color=lugar["color"],
                symbol="marker"
            ),
            name=nombre,
            hovertemplate=f"<b>{lugar['icono']} {nombre}</b><br>{lugar['tipo']}<br>{lugar['alt']} msnm<extra></extra>",
            showlegend=False
        ))
    
    # 3. CONFIGURACIÓN
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.8
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        clickmode='event+select',
        showlegend=True,
        legend=dict(
            yanchor="top", y=0.99,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

# ============================================================================
# APP PRINCIPAL
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
        **👥 Participantes:** Ocho naciones  
        **⏳ Duración:** 5 días
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🗺️ Lugares en el mapa
        - **16 lugares sagrados**
        - 🚌 Ruta vehicular (naranja)
        - 🚶 Lomada (morada)
        - **🖱️ Click en cualquier marcador**
        """)
    
    # ===== LAYOUT PRINCIPAL: PREGUNTAS (IZQ) + MAPA (DER) =====
    col_preguntas, col_mapa = st.columns([1, 2])
    
    # ===== COLUMNA IZQUIERDA: PREGUNTAS =====
    with col_preguntas:
        st.markdown("### ❓ Preguntas frecuentes")
        
        # Cargar conocimiento
        if 'rag' not in st.session_state:
            with st.spinner("Cargando..."):
                st.session_state.rag = cargar_conocimiento()
        
        # Selector de preguntas
        pregunta = st.selectbox(
            "Selecciona una pregunta:",
            options=[""] + TOP_10_PREGUNTAS,
            format_func=lambda x: "Elige una pregunta..." if x == "" else x,
            key="pregunta_select"
        )
        
        # Botón consultar
        if st.button("🔍 Consultar", use_container_width=True):
            if pregunta:
                with st.spinner("Buscando..."):
                    respuesta = st.session_state.rag.responder(pregunta)
                    st.session_state.ultima_respuesta = respuesta
                    st.session_state.ultima_pregunta = pregunta
        
        # Mostrar respuesta si existe
        if 'ultima_respuesta' in st.session_state:
            st.markdown(f"""
            <div class="respuesta-box">
                <span style="font-size: 0.8rem; color: #e67e22;">RESPUESTA</span>
                <p style="font-size: 1rem; margin-top: 8px;">{st.session_state.ultima_respuesta}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Días de la festividad (info extra)
        with st.expander("📅 Ver días de la festividad"):
            st.markdown("""
            **Día 1 (Sábado):** Gelación y ensayos  
            **Día 2 (Domingo):** Misa, romería, viaje  
            **Día 3 (Lunes):** Ascenso, Misa Ukukus  
            **Noche Lunes:** Subida al glaciar  
            **Día 4 (Martes):** Bajada, inicio Lomada  
            **Noche Martes:** Canto en Q'espi Cruz  
            **Día 5 (Miércoles):** Inti Alabado, retorno
            """)
    
    # ===== COLUMNA DERECHA: MAPA + INFO =====
    with col_mapa:
        # Selector de rutas
        tipo_ruta = st.radio(
            "Mostrar rutas:",
            ["Todas", "Vehicular", "Lomada"],
            horizontal=True,
            key="ruta_radio"
        )
        
        # Estado del lugar seleccionado
        if 'lugar_seleccionado' not in st.session_state:
            st.session_state.lugar_seleccionado = None
        
        # Crear mapa
        mapa = crear_mapa(tipo_ruta.lower())
        
        # Capturar click
        evento = st.plotly_chart(mapa, use_container_width=True, key="mapa", on_select="rerun")
        
        # Procesar click
        if evento and "selection" in evento:
            puntos = evento["selection"].get("points", [])
            if puntos:
                nombre = puntos[0].get("name")
                if nombre and nombre not in ["Ruta vehicular", "Ruta Lomada"]:
                    st.session_state.lugar_seleccionado = nombre
                    st.rerun()
        
        # Panel de información del lugar
        st.markdown("---")
        
        if st.session_state.lugar_seleccionado and st.session_state.lugar_seleccionado in LUGARES_SAGRADOS:
            lugar = LUGARES_SAGRADOS[st.session_state.lugar_seleccionado]
            
            st.markdown(f"""
            <div class="info-panel" style="border-left-color: {lugar['color']};">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 2rem;">{lugar['icono']}</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {lugar['color']};">{st.session_state.lugar_seleccionado}</span>
                </div>
                <p style="color: #e67e22; font-weight: 600; margin-bottom: 12px;">{lugar['tipo']}</p>
                <p style="color: #2c3e50; line-height: 1.6;">{lugar['descripcion']}</p>
                <div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-top: 16px;">
                    <span style="font-weight: 600;">📏 Altitud:</span> {lugar['alt']:,} msnm<br>
                    <span style="font-weight: 600;">🕯️ Ritual:</span> {lugar['ritual']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: white; border-radius: 16px; padding: 32px; text-align: center; border: 2px dashed #e67e22;">
                <div style="font-size: 3rem; margin-bottom: 16px;">🗺️</div>
                <h4 style="color: #1e3c72; margin-bottom: 8px;">Haz click en cualquier lugar del mapa</h4>
                <p style="color: #666;">Selecciona un marcador para ver información detallada</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== FOOTER =====
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 32px; margin-bottom: 16px;">
            <span>🏔️ Qoyllur Rit'i Explorer</span>
            <span>•</span>
            <span>🗺️ 16 lugares sagrados</span>
            <span>•</span>
            <span>🖱️ Click en el mapa</span>
        </div>
        <div style="font-size: 0.75rem; color: #95a5a6;">
            Conocimiento ancestral · Nación Paucartambo · Sinakara, Cusco
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()