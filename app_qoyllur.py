#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN FOLIUM COMPLETA
✅ FOLIUM - PUNTOS DE COLORES CON POPUPS DEL TTL
✅ PERFIL DE ALTITUD CORREGIDO
✅ INFO DIRECTAMENTE DEL TTL (rdfs:comment)
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
# CARGAR LUGARES DEL TTL CON TODA LA INFO
# ============================================================================
@st.cache_resource
def cargar_lugares_desde_ttl():
    """Extrae TODOS los lugares con coordenadas y descripciones del TTL"""
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
        descripcion = ""
        comentario = ""
        
        # Buscar coordenadas
        for p, o in g.predicate_objects(s):
            p_str = str(p)
            if 'lat' in p_str.lower():
                try: lat = float(o)
                except: pass
            if 'long' in p_str.lower() or 'lon' in p_str.lower():
                try: lon = float(o)
                except: pass
        
        if lat and lon:
            # Buscar nombre (label)
            for o in g.objects(s, RDFS.label):
                if isinstance(o, Literal) and o.language == 'es':
                    nombre = str(o)
                    break
            if not nombre:
                nombre = str(s).split('#')[-1]
            
            # Buscar descripción (tieneDescripcion)
            for p, o in g.predicate_objects(s):
                if 'tieneDescripcion' in str(p):
                    if isinstance(o, Literal):
                        descripcion = str(o)
                        break
            
            # Buscar comentario (rdfs:comment)
            for o in g.objects(s, RDFS.comment):
                if isinstance(o, Literal) and o.language == 'es':
                    comentario = str(o)
                    break
            
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "nombre": nombre,
                "descripcion": descripcion,
                "comentario": comentario
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
# MAPA CON FOLIUM - PUNTOS DE COLORES Y POPUPS DEL TTL
# ============================================================================
def crear_mapa_folium():
    """Crea mapa con Folium - puntos de colores, popups con info del TTL"""
    
    mapa = folium.Map(
        location=[-13.55, -71.4],
        zoom_start=8,
        control_scale=True,
        tiles='OpenStreetMap'
    )
    
    for nombre, lugar in LUGARES_TTL.items():
        # Determinar color según el nombre
        color = 'blue'
        nombre_lower = nombre.lower()
        
        if 'santuario' in nombre_lower:
            color = 'red'
        elif 'colque' in nombre_lower or 'glaciar' in nombre_lower:
            color = 'lightblue'
        elif 'cruz' in nombre_lower:
            color = 'green'
        elif 'iglesia' in nombre_lower:
            color = 'orange'
        elif 'plaza' in nombre_lower:
            color = 'purple'
        elif 'cementerio' in nombre_lower:
            color = 'gray'
        elif 'yanaqocha' in nombre_lower or 'laguna' in nombre_lower:
            color = 'cadetblue'
        elif 'yanaqancha' in nombre_lower or 'descanso' in nombre_lower:
            color = 'darkpurple'
        elif 'mahuayani' in nombre_lower or 'inicio' in nombre_lower:
            color = 'darkgreen'
        elif 'capilla' in nombre_lower:
            color = 'orange'
        elif 'gruta' in nombre_lower:
            color = 'darkred'
        elif 'caicay' in nombre_lower or 'ccatcca' in nombre_lower or 'ocongate' in nombre_lower:
            color = 'cadetblue'
        
        # Usar la descripción del TTL
        info_texto = lugar['descripcion'] if lugar['descripcion'] else lugar['comentario']
        if not info_texto:
            info_texto = "Lugar sagrado de la peregrinación"
        
        # Popup con HTML bonito
        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; min-width: 250px; padding: 5px;">
            <h4 style="color: #1e3c72; margin: 0 0 5px 0; border-bottom: 2px solid #e67e22; padding-bottom: 5px;">
                {nombre}
            </h4>
            <p style="margin: 8px 0; color: #2c3e50; font-size: 13px;">
                {info_texto}
            </p>
            <p style="margin: 8px 0; color: #666; font-size: 12px; background: #f8f9fa; padding: 5px; border-radius: 4px;">
                📍 {lugar['lat']:.4f}, {lugar['lon']:.4f}
            </p>
        </div>
        """
        
        folium.Marker(
            location=[lugar["lat"], lugar["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=nombre,
            icon=folium.Icon(color=color, icon='info-sign', prefix='glyphicon')
        ).add_to(mapa)
    
    return mapa

# ============================================================================
# PERFIL DE ALTITUD - CORREGIDO
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
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["dist"],
        y=df["alt"],
        mode="lines+markers",
        line=dict(color="#1e3c72", width=4),
        marker=dict(size=12, color="#e67e22", symbol="circle"),
        text=df["lugar"],
        hovertemplate="<b>%{text}</b><br>📏 %{x:.0f} km<br>🏔️ %{y:.0f} msnm<extra></extra>"
    ))
    
    # Agregar zonas
    fig.add_vrect(x0=0, x1=85, fillcolor="rgba(46,204,113,0.1)", line_width=0, 
                  annotation_text="🚌 Zona vehicular", annotation_position="top left")
    fig.add_vrect(x0=85, x1=95, fillcolor="rgba(241,196,15,0.1)", line_width=0,
                  annotation_text="🚶 Ascenso", annotation_position="top left")
    fig.add_vrect(x0=95, x1=125, fillcolor="rgba(155,89,182,0.1)", line_width=0,
                  annotation_text="🏔️ Lomada (24h)", annotation_position="top left")
    
    fig.update_layout(
        title="⛰️ Perfil de Altitud de la Peregrinación",
        xaxis_title="Distancia (km)",
        yaxis_title="Altitud (msnm)",
        height=500,
        hovermode="x unified",
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_xaxes(gridcolor="#e9ecef", gridwidth=1)
    fig.update_yaxes(gridcolor="#e9ecef", gridwidth=1)
    
    return fig

# ============================================================================
# APP PRINCIPAL
# ============================================================================
def main():
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
        ### 🗺️ Sobre el mapa
        - **Click en los marcadores** para ver información del TTL
        - **Colores por tipo** de lugar sagrado
        - Descripciones directas del archivo TTL
        """)
    
    tab1, tab2, tab3 = st.tabs(["❓ Preguntas", "🗺️ Mapa TTL", "⛰️ Perfil"])
    
    # ===== TAB 1: PREGUNTAS =====
    with tab1:
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando conocimiento ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        st.markdown("### ❓ Pregunta tu propia consulta")
        
        # Espacio para escribir pregunta personalizada
        pregunta_personalizada = st.text_input(
            "✍️ Escribe tu pregunta sobre Qoyllur Rit'i:",
            placeholder="Ej: ¿Cuál es el significado de los ukukus?",
            key="pregunta_input"
        )
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("##### O selecciona una pregunta frecuente:")
        with col2:
            pregunta = st.selectbox(
                "Preguntas frecuentes:",
                options=[""] + TOP_10_PREGUNTAS,
                format_func=lambda x: "🎯 Elige una pregunta..." if x == "" else x,
                label_visibility="collapsed"
            )
        with col3:
            st.markdown("<div style='margin-top: 24px;'>", unsafe_allow_html=True)
            responder = st.button("✨ Consultar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Determinar qué pregunta usar
        pregunta_final = None
        if responder:
            if pregunta_personalizada.strip():
                pregunta_final = pregunta_personalizada
            elif pregunta:
                pregunta_final = pregunta
        
        if pregunta_final:
            with st.spinner("🔍 Buscando en la memoria andina..."):
                respuesta = st.session_state.rag.responder(pregunta_final)
                
            st.markdown(f"""
            <div class="respuesta-box">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <span style="font-size: 2rem; margin-right: 16px;">🏔️</span>
                    <div>
                        <span style="font-size: 0.8rem; color: #7f8c8d;">TU PREGUNTA</span>
                        <div style="font-size: 1.1rem; font-weight: 600; color: #1e3c72;">
                            {pregunta_final}
                        </div>
                    </div>
                </div>
                <div style="font-size: 1.1rem; line-height: 1.7; color: #2c3e50;">
                    {respuesta}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TAB 2: MAPA CON FOLIUM =====
    with tab2:
        st.markdown(f"### 🗺️ Mapa de lugares sagrados ({len(LUGARES_TTL)} puntos)")
        
        if len(LUGARES_TTL) == 0:
            st.error("❌ No se encontraron lugares con coordenadas en el TTL")
            st.stop()
        
        mapa = crear_mapa_folium()
        st_data = st_folium(mapa, width="100%", height=600)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Lugares TTL", len(LUGARES_TTL))
        with col2:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        with col3:
            st.metric("📝 Info del TTL", "Click en marcadores")
    
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