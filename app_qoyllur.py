#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN 2.0 PREMIUM
✅ Mapas con iconos personalizados
✅ Perfil de altitud con zonas y pendiente
✅ Tooltips detallados
✅ Estilos de mapa (Satélite, Calle, Outdoor, Oscuro)
✅ Listo para Mapbox (solo agregar token)
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import random
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
    
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        border: 1px solid #f0f0f0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        border-color: #e67e22;
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
    
    /* Tooltips personalizados */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        background-color: #1e3c72;
        color: white;
        text-align: center;
        padding: 6px 12px;
        border-radius: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.8rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
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
    "IglesiaCcatcca": {"lat": -13.6426, "lon": -72.0780, "alt": 3700, "tipo": "iglesia"},
    "PlazaCcatcca": {"lat": -13.6426, "lon": -72.0780, "alt": 3700, "tipo": "plaza"},
    "Ocongate": {"lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "pueblo"},
    "CasaPriosteOcongate": {"lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "casa"},
    "PlazaOcongate": {"lat": -13.6394, "lon": -71.3878, "alt": 3800, "tipo": "plaza"},
    "Mahuayani": {"lat": -13.6052, "lon": -71.2350, "alt": 4200, "tipo": "inicio"},
    "SantuarioQoylluriti": {"lat": -13.5986, "lon": -71.1914, "alt": 4800, "tipo": "santuario"},
    "ColquePunku": {"lat": -13.5192, "lon": -71.2067, "alt": 5200, "tipo": "glaciar"},
    "MachuCruz": {"lat": -13.5900, "lon": -71.1850, "alt": 4900, "tipo": "cruz"},
    "Yanaqocha": {"lat": -13.5850, "lon": -71.1800, "alt": 4850, "tipo": "laguna"},
    "Yanaqancha": {"lat": -13.5800, "lon": -71.1750, "alt": 4750, "tipo": "descanso"},
    "QespiCruz": {"lat": -13.5700, "lon": -71.1650, "alt": 4600, "tipo": "cruz"},
    "QquchiyocWayqo": {"lat": -13.5750, "lon": -71.1700, "alt": 4700, "tipo": "rio"},
    "IntiLloksimuy": {"lat": -13.5600, "lon": -71.1550, "alt": 4500, "tipo": "solar"},
    "Tayancani": {"lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "pueblo"},
    "CapillaTayankani": {"lat": -13.5547, "lon": -71.1503, "alt": 3800, "tipo": "capilla"},
    "GrutaTayankani": {"lat": -13.5550, "lon": -71.1500, "alt": 3900, "tipo": "gruta"},
}

# ============================================================================
# RUTAS DE PEREGRINACIÓN
# ============================================================================
RUTA_VEHICULAR = [
    "Paucartambo",
    "Huancarani",
    "Ccatcca",
    "Ocongate",
    "Mahuayani"
]

RUTA_LOMADA = [
    "SantuarioQoylluriti",
    "MachuCruz",
    "Yanaqocha",
    "Yanaqancha",
    "QquchiyocWayqo",
    "QespiCruz",
    "IntiLloksimuy",
    "Tayancani"
]

# ============================================================================
# GALERÍA DE FOTOS (SIMULADA - REEMPLAZAR CON URLs REALES)
# ============================================================================
GALERIA_FOTOS = [
    {
        "id": "IMG_001",
        "titulo": "Ukumaris en misa de envío",
        "lugar": "IglesiaPaucartambo",
        "evento": "MisaInicial_Paucartambo_2025",
        "descripcion": "Ukumaris arrodillados durante la misa de envío en Paucartambo",
        "url": "https://via.placeholder.com/400x300/1e3c72/ffffff?text=🏔️+Misa+de+Envío",
        "fecha": "2025-06-15"
    },
    {
        "id": "IMG_002",
        "titulo": "Vestimenta ceremonial",
        "lugar": "PlazaPaucartambo",
        "evento": "RitualVestimentaDanzantes_2025",
        "descripcion": "Ukumari ayudando a otro a ponerse la máscara ceremonial",
        "url": "https://via.placeholder.com/400x300/e67e22/ffffff?text=🎭+Vestimenta+Ukumari",
        "fecha": "2025-06-15"
    },
    {
        "id": "IMG_003",
        "titulo": "Parada en Huancarani",
        "lugar": "Huancarani",
        "evento": "ParadaHuancarani_2025",
        "descripcion": "La Nación Paucartambo reunida en el cruce vial",
        "url": "https://via.placeholder.com/400x300/27ae60/ffffff?text=🚌+Huancarani",
        "fecha": "2025-06-15"
    },
    {
        "id": "IMG_004",
        "titulo": "Comida comunitaria",
        "lugar": "PlazaCcatcca",
        "evento": "ComidaCcatcca_2025",
        "descripcion": "Compartiendo asado con mote en la plaza de Ccatcca",
        "url": "https://via.placeholder.com/400x300/c0392b/ffffff?text=🍖+Comida+en+Ccatcca",
        "fecha": "2025-06-15"
    },
    {
        "id": "IMG_005",
        "titulo": "Misa de Ukukus",
        "lugar": "SantuarioQoylluriti",
        "evento": "MisaUkukus_2025",
        "descripcion": "Ukumaris en misa especial con el glaciar al fondo",
        "url": "https://via.placeholder.com/400x300/8e44ad/ffffff?text=⛪+Misa+de+Ukukus",
        "fecha": "2025-06-16"
    },
    {
        "id": "IMG_006",
        "titulo": "Ascenso al glaciar",
        "lugar": "ColquePunku",
        "evento": "SubidaColquePunku_2025",
        "descripcion": "Ukumaris ascendiendo al glaciar con antorchas",
        "url": "https://via.placeholder.com/400x300/34495e/ffffff?text=❄️+Glaciar+Colque+Punku",
        "fecha": "2025-06-16"
    }
]

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
# MAPA MEJORADO - CON ICONOS PERSONALIZADOS Y TOOLTIPS
# ============================================================================
def crear_mapa_mejorado(tipo_ruta="todas", estilo_mapa="satelite", token_mapbox=None):
    """
    Crea mapa interactivo con iconos personalizados y tooltips detallados
    """
    
    # Diccionario de iconos Maki (compatibles con Mapbox)
    ICONOS = {
        "pueblo": "town-hall",
        "iglesia": "place-of-worship",
        "cementerio": "cemetery",
        "plaza": "square",
        "santuario": "religious-christian",
        "glaciar": "snow",
        "cruz": "cross",
        "laguna": "water",
        "descanso": "bench",
        "rio": "river",
        "solar": "sun",
        "capilla": "chapel",
        "gruta": "cave",
        "inicio": "flag",
        "casa": "home"
    }
    
    # Tamaños de iconos
    TAMAÑOS = {
        "pueblo": 12, "iglesia": 14, "cementerio": 11, "plaza": 11,
        "santuario": 16, "glaciar": 15, "cruz": 13, "laguna": 12,
        "descanso": 10, "rio": 10, "solar": 14, "capilla": 12,
        "gruta": 11, "inicio": 14, "casa": 11
    }
    
    # Colores por tipo
    COLORES = {
        "pueblo": "#1e3c72", "iglesia": "#c0392b", "cementerio": "#7f8c8d",
        "plaza": "#e67e22", "santuario": "#f39c12", "glaciar": "#3498db",
        "cruz": "#27ae60", "laguna": "#16a085", "descanso": "#8e44ad",
        "rio": "#2980b9", "solar": "#f1c40f", "capilla": "#e74c3c",
        "gruta": "#95a5a6", "inicio": "#2c3e50", "casa": "#d35400"
    }
    
    # Descripciones detalladas para tooltips
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
        "CapillaTayankani": "Capilla donde reside la imagen todo el año",
        "GrutaTayankani": "Gruta de rituales finales de los Ukukus",
        "Ocongate": "Pueblo donde termina oficialmente la festividad",
        "Mahuayani": "Punto de inicio de la caminata al santuario",
        "Huancarani": "Cruce vial - Punto de encuentro de danzantes",
        "Ccatcca": "Pueblo de descanso y comida comunitaria",
        "CasaPriosteOcongate": "Casa del prioste - Autoridad de la fiesta"
    }
    
    # Estilos de mapa disponibles
    ESTILOS_MAPA = {
        "satelite": "satellite-streets",
        "calle": "carto-positron",
        "outdoor": "outdoors",
        "oscuro": "carto-darkmatter"
    }
    
    fig = go.Figure()
    
    # Preparar datos
    df_lugares = []
    for nombre, coords in LUGARES_COORDENADAS.items():
        df_lugares.append({
            "nombre": nombre,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "alt": coords["alt"],
            "tipo": coords["tipo"],
            "descripcion": DESCRIPCIONES.get(nombre, f"Lugar sagrado: {nombre}"),
            "icono": ICONOS.get(coords["tipo"], "marker"),
            "tamano": TAMAÑOS.get(coords["tipo"], 10)
        })
    
    df = pd.DataFrame(df_lugares)
    
    # Agregar puntos al mapa
    for tipo in df["tipo"].unique():
        df_tipo = df[df["tipo"] == tipo]
        
        hover_text = []
        for _, row in df_tipo.iterrows():
            texto = f"""
            <b style='font-size: 16px; color: {COLORES.get(tipo, "#000000")};'>{row['nombre']}</b><br>
            <span style='font-size: 14px;'>{row['descripcion']}</span><br>
            <br>
            <span style='font-size: 13px;'>
            🏔️ <b>Tipo:</b> {tipo.capitalize()}<br>
            📏 <b>Altitud:</b> {row['alt']:,} msnm<br>
            🗺️ <b>Coordenadas:</b> {row['lat']:.4f}, {row['lon']:.4f}
            </span>
            """
            hover_text.append(texto)
        
        fig.add_trace(go.Scattermapbox(
            lat=df_tipo["lat"],
            lon=df_tipo["lon"],
            mode="markers+text",
            marker=dict(
                    size=df_tipo["tamano"].iloc[0] if len(df_tipo) > 0 else 10,
                    color=COLORES.get(tipo, "#000000"),
                    symbol=ICONOS.get(tipo, "marker"),  # ✅ USAR EL DICCIONARIO DIRECTO
                    allowoverlap=False
            ),
            text=df_tipo["nombre"],
            textposition="top center",
            textfont=dict(size=10, color="#1e3c72"),
            name=tipo.capitalize(),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_text,
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=COLORES.get(tipo, "#000000"),
                font=dict(size=12, color="#1e3c72")
            )
        ))
    
    # Agregar rutas
    if tipo_ruta in ["vehicular", "todas"]:
        coords_ruta = [LUGARES_COORDENADAS[l] for l in RUTA_VEHICULAR if l in LUGARES_COORDENADAS]
        nombres_ruta = [l for l in RUTA_VEHICULAR if l in LUGARES_COORDENADAS]
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_ruta],
            lon=[c["lon"] for c in coords_ruta],
            mode="lines+markers",
            line=dict(width=4, color="#e67e22"),
            marker=dict(size=8, color="#e67e22", symbol="marker"),
            name="🚌 Ruta vehicular",
            hovertemplate="<b>Ruta vehicular</b><br>Paucartambo → Mahuayani<br>Paradas: " + 
                         ", ".join(nombres_ruta[1:-1]) + "<br><extra></extra>"
        ))
    
    if tipo_ruta in ["lomada", "todas"]:
        coords_lomada = [LUGARES_COORDENADAS[l] for l in RUTA_LOMADA if l in LUGARES_COORDENADAS]
        nombres_lomada = [l for l in RUTA_LOMADA if l in LUGARES_COORDENADAS]
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_lomada],
            lon=[c["lon"] for c in coords_lomada],
            mode="lines+markers",
            line=dict(width=4, color="#8e44ad"),
            marker=dict(size=8, color="#8e44ad", symbol="marker"),
            name="🚶 Ruta Lomada (24h)",
            hovertemplate="<b>Lomada / Loman Pureq</b><br>Caminata ritual de 24 horas<br>" +
                         "Hitos: " + ", ".join(nombres_lomada[1:-1]) + "<br><extra></extra>"
        ))
    
    # Configurar mapa
    mapbox_config = {
        "style": ESTILOS_MAPA.get(estilo_mapa, "carto-positron"),
        "center": dict(lat=-13.5, lon=-71.4),
        "zoom": 8.2
    }
    
    if token_mapbox:
        mapbox_config["accesstoken"] = token_mapbox
    
    fig.update_layout(
        mapbox=mapbox_config,
        margin=dict(l=0, r=0, t=40, b=0),
        height=650,
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#e9ecef", borderwidth=1
        ),
        title=dict(
            text="🗺️ Mapa Sagrado de Qoyllur Rit'i",
            font=dict(size=22, color="#1e3c72"),
            x=0.5
        )
    )
    
    return fig, df

# ============================================================================
# PERFIL DE ALTITUD MEJORADO - CON ZONAS Y PENDIENTE
# ============================================================================
# ============================================================================
# PERFIL DE ALTITUD MEJORADO - VERSIÓN CORREGIDA PARA PYTHON 3.13
# ============================================================================
def crear_perfil_altitud_mejorado():
    """
    Crea perfil de altitud con zonas coloreadas y gráfico de pendiente
    VERSIÓN CORREGIDA - compatible con Python 3.13 y Plotly actual
    """
    
    ruta_completa = [
        {"lugar": "Paucartambo", "dist": 0, "alt": 2900, "tipo": "pueblo", "icono": "🚌"},
        {"lugar": "Huancarani", "dist": 25, "alt": 3500, "tipo": "pueblo", "icono": "🤝"},
        {"lugar": "Ccatcca", "dist": 45, "alt": 3700, "tipo": "pueblo", "icono": "🍖"},
        {"lugar": "Ocongate", "dist": 65, "alt": 3800, "tipo": "pueblo", "icono": "🏠"},
        {"lugar": "Mahuayani", "dist": 85, "alt": 4200, "tipo": "inicio", "icono": "🚶"},
        {"lugar": "Santuario", "dist": 95, "alt": 4800, "tipo": "santuario", "icono": "⛪"},
        {"lugar": "MachuCruz", "dist": 98, "alt": 4900, "tipo": "cruz", "icono": "✝️"},
        {"lugar": "Yanaqocha", "dist": 102, "alt": 4850, "tipo": "laguna", "icono": "💧"},
        {"lugar": "Yanaqancha", "dist": 106, "alt": 4750, "tipo": "descanso", "icono": "😴"},
        {"lugar": "QquchiyocWayqo", "dist": 110, "alt": 4700, "tipo": "rio", "icono": "💦"},
        {"lugar": "QespiCruz", "dist": 115, "alt": 4600, "tipo": "cruz", "icono": "🎵"},
        {"lugar": "IntiLloksimuy", "dist": 120, "alt": 4500, "tipo": "solar", "icono": "☀️"},
        {"lugar": "Tayancani", "dist": 125, "alt": 3800, "tipo": "pueblo", "icono": "🏁"}
    ]
    
    df_ruta = pd.DataFrame(ruta_completa)
    
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("⛰️ Perfil de Altitud", "📊 Pendiente del Terreno")
    )
    
    # ===== GRÁFICO PRINCIPAL: PERFIL DE ALTITUD =====
    # Versión simplificada sin fillcolor problemático
    fig.add_trace(
        go.Scatter(
            x=df_ruta["dist"],
            y=df_ruta["alt"],
            mode="lines+markers",
            name="Perfil de altitud",
            line=dict(color="#1e3c72", width=4),
            marker=dict(
                size=10,
                color=df_ruta["alt"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="msnm", x=1.05, len=0.5)
            ),
            text=df_ruta["lugar"],
            hovertemplate="<b>%{text}</b><br>" +
                         "📏 Distancia: %{x:.0f} km<br>" +
                         "🏔️ Altitud: %{y:.0f} msnm<br>" +
                         "<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Zonas coloreadas usando add_vrect (más estable)
    fig.add_vrect(
        x0=0, x1=85,
        fillcolor="rgba(46, 204, 113, 0.1)",
        line_width=0,
        annotation_text="🚌 Zona vehicular",
        annotation_position="top left",
        row=1, col=1
    )
    
    fig.add_vrect(
        x0=85, x1=95,
        fillcolor="rgba(241, 196, 15, 0.1)",
        line_width=0,
        annotation_text="🚶 Ascenso",
        annotation_position="top left",
        row=1, col=1
    )
    
    fig.add_vrect(
        x0=95, x1=125,
        fillcolor="rgba(155, 89, 182, 0.1)",
        line_width=0,
        annotation_text="🏔️ Lomada (24h)",
        annotation_position="top left",
        row=1, col=1
    )
    
    # Hitos principales
    hitos = ["Paucartambo", "Mahuayani", "Santuario", "Tayancani"]
    df_hitos = df_ruta[df_ruta["lugar"].isin(hitos)]
    
    fig.add_trace(
        go.Scatter(
            x=df_hitos["dist"],
            y=df_hitos["alt"],
            mode="markers+text",
            marker=dict(
                size=14,
                color="#e67e22",
                symbol="star",
                line=dict(color="white", width=2)
            ),
            text=df_hitos["lugar"],
            textposition="top center",
            textfont=dict(size=11, color="#1e3c72"),
            name="Hitos principales",
            hovertemplate="<b>%{text}</b><br>📍 Punto clave<br>🏔️ %{y:.0f} msnm<extra></extra>"
        ),
        row=1, col=1
    )
    
    # ===== GRÁFICO SECUNDARIO: PENDIENTE =====
    # Calcular pendientes
    pendientes = []
    for i in range(1, len(df_ruta)):
        delta_dist = df_ruta.loc[i, "dist"] - df_ruta.loc[i-1, "dist"]
        delta_alt = df_ruta.loc[i, "alt"] - df_ruta.loc[i-1, "alt"]
        pendiente = (delta_alt / delta_dist) * 100 if delta_dist > 0 else 0
        
        pendientes.append({
            "x": (df_ruta.loc[i, "dist"] + df_ruta.loc[i-1, "dist"]) / 2,
            "pendiente": pendiente,
            "inicio": df_ruta.loc[i-1, "lugar"],
            "fin": df_ruta.loc[i, "lugar"]
        })
    
    df_pend = pd.DataFrame(pendientes)
    
    # Colores según pendiente
    colors = ['#27ae60' if p >= 0 else '#e74c3c' for p in df_pend["pendiente"]]
    
    fig.add_trace(
        go.Bar(
            x=df_pend["x"],
            y=df_pend["pendiente"],
            marker_color=colors,
            name="Pendiente",
            hovertemplate="<b>%{customdata[0]} → %{customdata[1]}</b><br>" +
                         "📊 Pendiente: %{y:.1f}%<br>" +
                         "<extra></extra>",
            customdata=df_pend[["inicio", "fin"]].values,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Línea de referencia en 0%
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#7f8c8d",
        opacity=0.5,
        row=2, col=1
    )
    
    # ===== CONFIGURACIÓN DEL LAYOUT =====
    fig.update_layout(
        height=700,
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#e9ecef",
            borderwidth=1
        ),
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    # Configuración de ejes
    fig.update_xaxes(
        title_text="Distancia (km)",
        gridcolor="#e9ecef",
        showgrid=True,
        gridwidth=1,
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="Altitud (msnm)",
        gridcolor="#e9ecef",
        showgrid=True,
        gridwidth=1,
        row=1, col=1
    )
    
    fig.update_xaxes(
        title_text="Distancia (km)",
        gridcolor="#e9ecef",
        showgrid=True,
        gridwidth=1,
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="Pendiente (%)",
        gridcolor="#e9ecef",
        showgrid=True,
        gridwidth=1,
        row=2, col=1
    )
    
    return fig

# ============================================================================
# GALERÍA DE FOTOS MEJORADA
# ============================================================================
def mostrar_galeria_fotos(fotos=GALERIA_FOTOS):
    """Muestra galería de fotos en grid responsive"""
    
    st.markdown("### 📸 Galería de la Peregrinación")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        dias = ["Todos"] + sorted(list(set([f["fecha"] for f in fotos])))
        filtro_dia = st.selectbox("📅 Filtrar por día", dias, key="filtro_dia")
    with col2:
        lugares = ["Todos"] + sorted(list(set([f["lugar"] for f in fotos])))
        filtro_lugar = st.selectbox("📍 Filtrar por lugar", lugares, key="filtro_lugar")
    with col3:
        eventos = ["Todos"] + sorted(list(set([f["evento"] for f in fotos])))
        filtro_evento = st.selectbox("🏷️ Filtrar por evento", eventos, key="filtro_evento")
    
    fotos_filtradas = fotos.copy()
    if filtro_dia != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["fecha"] == filtro_dia]
    if filtro_lugar != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["lugar"] == filtro_lugar]
    if filtro_evento != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["evento"] == filtro_evento]
    
    cols = st.columns(3)
    for i, foto in enumerate(fotos_filtradas[:9]):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: white; border-radius: 16px; padding: 12px; margin-bottom: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
                        transition: all 0.3s ease;">
                <img src="{foto['url']}" style="width:100%; border-radius:12px; margin-bottom:12px;">
                <div style="padding: 4px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:#1e3c72;">{foto['titulo']}</span>
                        <span class="badge-andino">{foto['fecha']}</span>
                    </div>
                    <p style="color:#5d6d7e; font-size:0.9rem; margin-top:8px;">
                        {foto['descripcion']}
                    </p>
                    <div style="display:flex; gap:8px; margin-top:8px;">
                        <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px;
                                   font-size:0.75rem; color:#495057;">
                            📍 {foto['lugar']}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if len(fotos_filtradas) > 9:
        st.info(f"📸 Mostrando 9 de {len(fotos_filtradas)} fotos")

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
                Conocimiento ancestral · Mapas interactivos · Galería visual · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Token de Mapbox en sidebar (para probar después)
    with st.sidebar:
        st.markdown("### 🗺️ Configuración de Mapbox")
        token_mapbox = st.text_input(
            "Token de Mapbox (opcional)",
            type="password",
            help="Obtén tu token gratis en mapbox.com para imágenes satelitales"
        )
        
        if token_mapbox:
            st.success("✅ Token configurado - Imágenes satelitales activadas")
        else:
            st.info("ℹ️ Sin token: usando mapas base gratuitos")
        
        st.markdown("---")
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown("""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **📍 Altitud:** 4,800 - 5,200 msnm  
        **👥 Participantes:** Ocho naciones  
        **⏳ Duración:** 5 días
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "❓ Preguntas", "🗺️ Mapa Sagrado", "⛰️ Perfil de Altitud",
        "📋 Eventos", "📸 Galería"
    ])
    
    # ========================================================================
    # TAB 1: PREGUNTAS
    # ========================================================================
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
    
    # ========================================================================
    # TAB 2: MAPA SAGRADO MEJORADO
    # ========================================================================
    with tab2:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("### 🗺️ Mapa Sagrado Interactivo")
        with col2:
            tipo_ruta = st.radio(
                "Mostrar rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True
            )
        with col3:
            estilo_mapa = st.selectbox(
                "Estilo de mapa:",
                ["Satélite", "Calle", "Outdoor", "Oscuro"],
                index=0
            )
        
        mapa, df_lugares = crear_mapa_mejorado(
            tipo_ruta.lower(),
            estilo_mapa.lower(),
            token_mapbox if token_mapbox else None
        )
        st.plotly_chart(mapa, use_container_width=True)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares sagrados", len(LUGARES_COORDENADAS))
        with col2:
            st.metric("🚌 Ruta vehicular", "~120 km")
        with col3:
            st.metric("🚶 Lomada", "~35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        
        # Leyenda
        with st.expander("📍 Leyenda de lugares por tipo", expanded=False):
            tipos_unicos = df_lugares["tipo"].unique()
            cols = st.columns(3)
            for i, tipo in enumerate(tipos_unicos[:12]):
                with cols[i % 3]:
                    st.markdown(f"• **{tipo.capitalize()}**")
    
    # ========================================================================
    # TAB 3: PERFIL DE ALTITUD MEJORADO
    # ========================================================================
    with tab3:
        st.markdown("### ⛰️ Perfil Completo de la Peregrinación")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Partida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📏 Desnivel", "+2,300 m", "⬆️ Ascenso")
        with col4:
            st.metric("🎯 Llegada", "Tayankani", "3,800 msnm")
        
        perfil = crear_perfil_altitud_mejorado()
        st.plotly_chart(perfil, use_container_width=True)
    
    # ========================================================================
    # TAB 4: EVENTOS
    # ========================================================================
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Eventos por Día")
            eventos_por_dia = {
                "Día 1": 1, "Día 2": 9, "Día 3": 6,
                "Noche L1-M": 1, "Día 4": 6, "Noche M-M": 2, "Día 5": 5
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
                "Día 1 (Sábado)": "🟡 Gelación",
                "Día 2 (Domingo)": "🟠 Misa · Romería · Viaje",
                "Día 3 (Lunes)": "🔵 Ascenso · Misa Ukukus",
                "Noche Lunes": "🌙 Subida glaciar",
                "Día 4 (Martes)": "🟢 Bajada · Inicio Lomada",
                "Noche Martes": "⭐ Canto Q'espi Cruz",
                "Día 5 (Miércoles)": "🔴 Inti Alabado"
            }
            for dia, evento in timeline.items():
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid #e67e22; padding: 12px 16px;
                           margin: 8px 0; border-radius: 0 12px 12px 0;">
                    <span style="font-weight: 600; color: #1e3c72;">{dia}</span>
                    <span style="color: #5d6d7e; margin-left: 12px;">{evento}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 5: GALERÍA
    # ========================================================================
    with tab5:
        mostrar_galeria_fotos()
        
        st.markdown("---")
        st.markdown("""
        <div style="background: #fff9f0; padding: 24px; border-radius: 16px; margin-top: 20px;
                    border: 1px solid #ffe0b2;">
            <span style="font-weight: 600; color: #1e3c72; font-size: 1.1rem;">📸 ¿Tienes fotos de Qoyllur Rit'i?</span><br>
            <span style="color: #5d6d7e;">
                Puedes agregar tus propias imágenes a la galería. 
                Sube las fotos a GitHub y agrega las URLs en el archivo GALERIA_FOTOS.
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer V2.0 Premium</span>
            <span>•</span>
            <span>🗺️ Mapas con iconos</span>
            <span>•</span>
            <span>📊 Perfil con pendiente</span>
            <span>•</span>
            <span>🛰️ Listo para Mapbox</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco · 100% local
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()