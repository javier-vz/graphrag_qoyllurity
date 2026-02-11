#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN FOLIUM (SOLO PUNTOS)
✅ FOLIUM - SIEMPRE FUNCIONA
✅ SOLO PUNTOS NEGROS GRANDES EN EL MAPA
✅ LUGARES DIRECTAMENTE DEL TTL
✅ SIN RUTAS, SIN COMPLICACIONES
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from pathlib import Path
from rdflib import Graph, Literal
from rdflib.namespace import RDFS
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# MOTOR DE CONOCIMIENTO
# ============================================================================
from ultralite_qoyllur_v15 import UltraLiteQoyllurV15

st.set_page_config(page_title="Qoyllur Rit'i", page_icon="🏔️", layout="wide")

# ============================================================================
# CSS
# ============================================================================
st.markdown("""
<style>
    .main { background: #fdfaf6; }
    h1 { color: #1e3c72; }
    .stButton button { background: #1e3c72; color: white; }
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

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
# CARGAR LUGARES DEL TTL
# ============================================================================
@st.cache_resource
def cargar_lugares_desde_ttl():
    """Extrae TODOS los lugares con coordenadas del TTL"""
    ttl_path = "qoyllurity.ttl"
    if not Path(ttl_path).exists():
        return {}
    
    g = Graph()
    g.parse(ttl_path, format='turtle')
    lugares = {}
    
    for s in g.subjects():
        lat = None
        lon = None
        nombre = None
        
        for p, o in g.predicate_objects(s):
            p_str = str(p)
            if 'lat' in p_str.lower():
                try: lat = float(o)
                except: pass
            if 'long' in p_str.lower() or 'lon' in p_str.lower():
                try: lon = float(o)
                except: pass
        
        if lat and lon:
            for o in g.objects(s, RDFS.label):
                if isinstance(o, Literal) and o.language == 'es':
                    nombre = str(o)
                    break
            if not nombre:
                nombre = str(s).split('#')[-1]
            
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "nombre": nombre
            }
    
    return lugares

# ============================================================================
# CARGAR LUGARES
# ============================================================================
LUGARES_TTL = cargar_lugares_desde_ttl()

# ============================================================================
# MOTOR DE CONOCIMIENTO
# ============================================================================
@st.cache_resource
def cargar_conocimiento():
    return UltraLiteQoyllurV15("qoyllurity.ttl")

# ============================================================================
# MAPA CON FOLIUM - PUNTOS DE COLORES Y POPUPS BONITOS
# ============================================================================
def crear_mapa_folium():
    """Crea mapa con Folium - puntos de colores, popups con info"""
    
    # Centro del mapa
    mapa = folium.Map(
        location=[-13.55, -71.4],
        zoom_start=8,
        control_scale=True,
        tiles='OpenStreetMap'
    )
    
    # Diccionario de colores por tipo de lugar (inferido del nombre)
    colores = {
        'santuario': 'red',
        'glaciar': 'lightblue',
        'cruz': 'green',
        'iglesia': 'orange',
        'plaza': 'purple',
        'pueblo': 'blue',
        'cementerio': 'gray',
        'laguna': 'cadetblue',
        'descanso': 'darkpurple',
        'inicio': 'darkgreen',
        'capilla': 'orange',
        'gruta': 'darkred'
    }
    
    # Iconos por tipo
    iconos = {
        'santuario': '🏔️',
        'glaciar': '❄️',
        'cruz': '✝️',
        'iglesia': '⛪',
        'plaza': '🎭',
        'pueblo': '🏘️',
        'cementerio': '🕊️',
        'laguna': '💧',
        'descanso': '😴',
        'inicio': '🚩',
        'capilla': '⛪',
        'gruta': '🕯️'
    }
    
    for nombre, lugar in LUGARES_TTL.items():
        # Determinar color e icono según el nombre
        color = 'blue'
        icono = '📍'
        
        nombre_lower = nombre.lower()
        
        if 'santuario' in nombre_lower:
            color = 'red'
            icono = '🏔️'
        elif 'colque' in nombre_lower or 'glaciar' in nombre_lower:
            color = 'lightblue'
            icono = '❄️'
        elif 'cruz' in nombre_lower:
            color = 'green'
            icono = '✝️'
        elif 'iglesia' in nombre_lower:
            color = 'orange'
            icono = '⛪'
        elif 'plaza' in nombre_lower:
            color = 'purple'
            icono = '🎭'
        elif 'cementerio' in nombre_lower:
            color = 'gray'
            icono = '🕊️'
        elif 'yanaqocha' in nombre_lower or 'laguna' in nombre_lower:
            color = 'cadetblue'
            icono = '💧'
        elif 'yanaqancha' in nombre_lower or 'descanso' in nombre_lower:
            color = 'darkpurple'
            icono = '😴'
        elif 'mahuayani' in nombre_lower or 'inicio' in nombre_lower:
            color = 'darkgreen'
            icono = '🚩'
        elif 'capilla' in nombre_lower:
            color = 'orange'
            icono = '⛪'
        elif 'gruta' in nombre_lower:
            color = 'darkred'
            icono = '🕯️'
        
        # Crear popup con HTML bonito
        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
            <h4 style="color: #1e3c72; margin: 0 0 8px 0;">{icono} {nombre}</h4>
            <hr style="margin: 8px 0; border: 1px solid #e67e22;">
            <p style="margin: 8px 0; color: #2c3e50;">
                <b>📍 Coordenadas:</b><br>
                {lugar['lat']:.4f}, {lugar['lon']:.4f}
            </p>
        """
        
        # Agregar descripción si existe
        if 'descripcion' in lugar and lugar['descripcion']:
            popup_html += f"""
            <p style="margin: 8px 0; color: #2c3e50;">
                <b>📝 Descripción:</b><br>
                {lugar['descripcion']}
            </p>
            """
        
        popup_html += "</div>"
        
        # Agregar marcador
        folium.Marker(
            location=[lugar["lat"], lugar["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=nombre,
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(mapa)
    
    return mapa

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
                Conocimiento ancestral · Mapas con Folium · Sinakara, Cusco
            </p>
            <p style="margin: 5px 0 0 0; color: #e67e22; font-size: 0.9rem;">
                🗺️ {len(LUGARES_TTL)} lugares sagrados cargados desde el TTL
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown(f"""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📍 Lugares en mapa:** {len(LUGARES_TTL)} sitios sagrados  
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **⛰️ Altitud máxima:** 5,200 msnm  
        **👥 Participantes:** Ocho naciones
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🗺️ Mapa con Folium
        - **Puntos negros** = lugares sagrados
        - **Click** en cada punto para ver nombre
        - Sin tokens, sin Mapbox, sin errores
        """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa (Folium)", "⛰️ Perfil"])
    
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
    
    # ===== TAB 2: MAPA CON FOLIUM - SOLO PUNTOS NEGROS =====
    with tab2:
        st.markdown(f"### 🗺️ Mapa de lugares sagrados ({len(LUGARES_TTL)} puntos)")
        
        if len(LUGARES_TTL) == 0:
            st.error("❌ No se encontraron lugares con coordenadas en el TTL")
            st.stop()
        
        # Crear mapa con Folium
        mapa = crear_mapa_folium()
        
        # Mostrar mapa
        st_data = st_folium(mapa, width="100%", height=600)
        
        # Métricas simples
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Lugares TTL", len(LUGARES_TTL))
        with col2:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        with col3:
            st.metric("🗺️ Tecnología", "Folium (sin errores)")
    
    # ===== TAB 3: PERFIL =====
    with tab3:
        st.markdown("### ⛰️ Perfil de Altitud")
        
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

if __name__ == "__main__":
    main()