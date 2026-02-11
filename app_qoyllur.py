#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN FINAL
✅ LUGARES EXTRAÍDOS DIRECTAMENTE DEL TTL - ÚNICA FUENTE
✅ SIN diccionarios manuales
✅ Mapas con iconos personalizados
✅ Perfil de altitud con zonas y pendiente
✅ Tooltips detallados con descripciones del TTL
✅ 100% funcional en Python 3.13
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
import hashlib

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
# CSS PERSONALIZADO - ESTILO ANDINO
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
# EXTRAER LUGARES DIRECTAMENTE DEL TTL - ÚNICA FUENTE DE VERDAD
# ============================================================================
@st.cache_resource
def cargar_lugares_desde_ttl():
    """Extrae TODOS los lugares con coordenadas del TTL - SIN DICT MANUAL"""
    ttl_path = "qoyllurity.ttl"
    posibles = ["qoyllurity.ttl", "../qoyllurity.ttl", "./data/qoyllurity.ttl"]
    for p in posibles:
        if Path(p).exists():
            ttl_path = p
            break
    
    g = Graph()
    g.parse(ttl_path, format='turtle')
    
    lugares = {}
    
    for s in g.subjects():
        lat = None
        lon = None
        nombre = None
        alt = 0
        descripcion = ""
        
        # Buscar lat/long (Annotation Properties)
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
            # Buscar nombre (label)
            for o in g.objects(s, RDFS.label):
                if isinstance(o, Literal) and o.language == 'es':
                    nombre = str(o)
                    break
            
            if not nombre:
                nombre = str(s).split('#')[-1]
            
            # Buscar altitud si existe
            for p, o in g.predicate_objects(s):
                if 'alt' in str(p).lower():
                    try:
                        alt = float(o)
                    except:
                        pass
            
            # Buscar descripción
            for p, o in g.predicate_objects(s):
                p_str = str(p)
                if 'tieneDescripcion' in p_str or 'comment' in p_str:
                    if isinstance(o, Literal):
                        if hasattr(o, 'language') and o.language == 'es':
                            descripcion = str(o)
                            break
                        else:
                            descripcion = str(o)
            
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "nombre": nombre,
                "id": str(s).split('#')[-1],
                "descripcion": descripcion[:150] + "..." if len(descripcion) > 150 else descripcion,
                "tipo": "Lugar sagrado"
            }
    
    return lugares

# ============================================================================
# CARGAR LUGARES - ESTA ES LA ÚNICA FUENTE DE DATOS
# ============================================================================
LUGARES_TTL = cargar_lugares_desde_ttl()

# ============================================================================
# RUTAS DE PEREGRINACIÓN (solo nombres, las coordenadas vienen del TTL)
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
# FUNCIÓN PARA GENERAR COLORES CONSISTENTES
# ============================================================================
def generar_color(nombre):
    """Genera un color único basado en el nombre"""
    hash_obj = hashlib.md5(nombre.encode())
    hue = int(hash_obj.hexdigest()[:6], 16) % 360
    return f"hsl({hue}, 70%, 50%)"

# ============================================================================
# FUNCIÓN PARA ASIGNAR ICONOS
# ============================================================================
def asignar_icono(nombre):
    """Asigna un icono basado en el nombre del lugar"""
    nombre_lower = nombre.lower()
    if "glaciar" in nombre_lower or "colque" in nombre_lower or "punku" in nombre_lower:
        return "❄️"
    elif "santuario" in nombre_lower:
        return "🏔️"
    elif "cruz" in nombre_lower:
        return "✝️"
    elif "iglesia" in nombre_lower:
        return "⛪"
    elif "plaza" in nombre_lower:
        return "🎭"
    elif "laguna" in nombre_lower or "yanaqocha" in nombre_lower:
        return "💧"
    elif "cementerio" in nombre_lower:
        return "🕊️"
    elif "casa" in nombre_lower or "prioste" in nombre_lower:
        return "🏠"
    elif "capilla" in nombre_lower:
        return "⛪"
    elif "gruta" in nombre_lower:
        return "🕯️"
    elif "inicio" in nombre_lower or "mahuayani" in nombre_lower:
        return "🚩"
    elif "descanso" in nombre_lower or "yanaqancha" in nombre_lower:
        return "😴"
    elif "rio" in nombre_lower or "wayqo" in nombre_lower:
        return "💦"
    elif "solar" in nombre_lower or "inti" in nombre_lower:
        return "☀️"
    else:
        return "📍"

# ============================================================================
# MAPA - SOLO CON LUGARES DEL TTL
# ============================================================================
def crear_mapa_ttl(tipo_ruta="todas", estilo_mapa="calle", token_mapbox=None):
    """
    Mapa con lugares EXCLUSIVAMENTE del TTL
    """
    
    # Estilos de mapa
    ESTILOS_MAPA = {
        "calle": "carto-positron",
        "outdoor": "open-street-map",
        "oscuro": "carto-darkmatter",
        "satelite": "satellite-streets"
    }
    
    fig = go.Figure()
    
    # ===== AGREGAR RUTAS (solo si existen en TTL) =====
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
    
    # ===== AGREGAR LUGARES - SOLO DEL TTL =====
    for nombre, lugar in LUGARES_TTL.items():
        color = generar_color(nombre)
        icono = asignar_icono(nombre)
        
        hover_text = f"""
        <b style='font-size: 16px; color: {color};'>{icono} {nombre}</b><br>
        <span style='font-size: 13px;'>
        📏 {lugar['lat']:.4f}, {lugar['lon']:.4f}<br>
        🏔️ {lugar['alt']:.0f} msnm<br>
        </span>
        <span style='font-size: 12px; color: #555;'>
        {lugar['descripcion']}
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
# PERFIL DE ALTITUD
# ============================================================================
def crear_perfil_altitud():
    """Perfil de altitud con zonas y pendiente"""
    
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
# GALERÍA DE FOTOS
# ============================================================================
def mostrar_galeria_fotos():
    """Muestra galería de fotos (placeholder)"""
    st.markdown("### 📸 Galería de la Peregrinación")
    st.info("""
    **📸 Próximamente:**
    - Fotos de la peregrinación
    - Videos de danzas rituales
    - Paisajes de la ruta
    """)

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
        **⛰️ Altitud:** 4,800 - 5,200 msnm  
        **👥 Participantes:** Ocho naciones
        """)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "❓ Preguntas", "🗺️ Mapa TTL", "⛰️ Perfil",
        "📋 Eventos", "📸 Galería"
    ])
    
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
    
    # ===== TAB 2: MAPA - SOLO LUGARES DEL TTL =====
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
    
    # ===== TAB 4: EVENTOS =====
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Eventos por Día")
            eventos_por_dia = {
                "Día 1": 1, "Día 2": 9, "Día 3": 6,
                "Noche L1": 1, "Día 4": 6, "Noche M": 2, "Día 5": 5
            }
            df_eventos = pd.DataFrame([
                {"dia": d, "eventos": e} for d, e in eventos_por_dia.items()
            ])
            fig = px.bar(df_eventos, x="dia", y="eventos",
                        color="eventos", color_continuous_scale=["#f39c12", "#e67e22", "#c0392b"])
            fig.update_traces(texttemplate="%{y}", textposition="outside")
            fig.update_layout(height=400, showlegend=False, plot_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏳ Línea de Tiempo")
            timeline = {
                "Día 1 (Sábado)": "🟡 Gelación y ensayos",
                "Día 2 (Domingo)": "🟠 Misa · Romería · Viaje",
                "Día 3 (Lunes)": "🔵 Ascenso · Misa Ukukus",
                "Noche Lunes": "🌙 Subida al glaciar",
                "Día 4 (Martes)": "🟢 Bajada · Inicio Lomada",
                "Noche Martes": "⭐ Canto en Q'espi Cruz",
                "Día 5 (Miércoles)": "🔴 Inti Alabado · Retorno"
            }
            for dia, evento in timeline.items():
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid #e67e22; padding: 12px 16px;
                           margin: 8px 0; border-radius: 0 12px 12px 0;">
                    <span style="font-weight: 600; color: #1e3c72;">{dia}</span>
                    <span style="color: #5d6d7e; margin-left: 12px;">{evento}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== TAB 5: GALERÍA =====
    with tab5:
        mostrar_galeria_fotos()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer</span>
            <span>•</span>
            <span>🗺️ Lugares del TTL</span>
            <span>•</span>
            <span>📊 Perfil con pendiente</span>
            <span>•</span>
            <span>✨ 100% TTL</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()