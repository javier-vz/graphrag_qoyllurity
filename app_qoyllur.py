#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN COMPLETA CORREGIDA
Fase 1.5: UltraLite + UI Elegante + Mapas + Gráficos + Galería
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
    page_title="Qoyllur Rit'i Explorer - Completo",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - ESTILO ANDINO PREMIUM
# ============================================================================
st.markdown("""
<style>
    /* Colores de la tierra andina */
    :root {
        --andean-sky: #1e3c72;
        --andean-sunset: #e67e22;
        --andean-stone: #7f8c8d;
        --andean-textile: #c0392b;
        --andean-leaf: #27ae60;
        --andean-snow: #ecf0f1;
        --andean-gold: #f39c12;
        --andean-purple: #8e44ad;
    }
    
    .main {
        background: linear-gradient(135deg, #fdfaf6 0%, #fff9f0 100%);
    }
    
    h1, h2, h3 {
        color: #1e3c72;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1e3c72 0%, #2c5a8c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #2c5a8c 0%, #1e3c72 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        margin: 20px 0;
        font-size: 1.1rem;
        line-height: 1.7;
        border: 1px solid #f0f0f0;
    }
    
    .sugerencia-card {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
        cursor: pointer;
        border-bottom: 3px solid #e67e22;
    }
    
    .sugerencia-card:hover {
        transform: translateX(6px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        background: white;
    }
    
    .photo-card {
        background: white;
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .photo-card:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }
    
    .badge-andino {
        background: #e67e22;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 8px;
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
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
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
    },
    {
        "id": "IMG_007",
        "titulo": "Machu Cruz",
        "lugar": "MachuCruz",
        "evento": "RitualMachuCruz_2025",
        "descripcion": "Pausa ritual para comer maíz y queso",
        "url": "https://via.placeholder.com/400x300/f39c12/ffffff?text=✝️+Machu+Cruz",
        "fecha": "2025-06-17"
    },
    {
        "id": "IMG_008",
        "titulo": "Despedida en Yanaqocha",
        "lugar": "Yanaqocha",
        "evento": "RitualDespedida_Yanaqocha_2025",
        "descripcion": "Abrazos y despedidas en la laguna",
        "url": "https://via.placeholder.com/400x300/16a085/ffffff?text=💧+Laguna+Yanaqocha",
        "fecha": "2025-06-17"
    },
    {
        "id": "IMG_009",
        "titulo": "Inti Alabado",
        "lugar": "IntiLloksimuy",
        "evento": "IntiAlabado_2025",
        "descripcion": "Saludo al sol al amanecer en Tayankani",
        "url": "https://via.placeholder.com/400x300/f1c40f/ffffff?text=☀️+Inti+Alabado",
        "fecha": "2025-06-18"
    },
    {
        "id": "IMG_010",
        "titulo": "Procesión final",
        "lugar": "PlazaOcongate",
        "evento": "ProcesionEntradaOcongate_2025",
        "descripcion": "Entrada procesional a Ocongate, fin de la peregrinación",
        "url": "https://via.placeholder.com/400x300/2980b9/ffffff?text=🎉+Ocongate",
        "fecha": "2025-06-18"
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
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def crear_mapa_interactivo(tipo_ruta="todas"):
    """Crea mapa interactivo con Plotly - VERSIÓN CORREGIDA"""
    fig = go.Figure()
    
    # Convertir datos a DataFrame
    df_lugares = []
    for nombre, coords in LUGARES_COORDENADAS.items():
        df_lugares.append({
            "nombre": nombre,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "alt": coords["alt"],
            "tipo": coords["tipo"]
        })
    df = pd.DataFrame(df_lugares)
    
    # Colores por tipo
    colores = {
        "pueblo": "#1e3c72",
        "iglesia": "#c0392b",
        "cementerio": "#7f8c8d",
        "plaza": "#e67e22",
        "santuario": "#f39c12",
        "glaciar": "#3498db",
        "cruz": "#27ae60",
        "laguna": "#16a085",
        "descanso": "#8e44ad",
        "rio": "#2980b9",
        "solar": "#f1c40f",
        "capilla": "#e74c3c",
        "gruta": "#95a5a6",
        "inicio": "#2c3e50",
        "casa": "#d35400"
    }
    
    # Agregar puntos
    for tipo in df["tipo"].unique():
        df_tipo = df[df["tipo"] == tipo]
        fig.add_trace(go.Scattermapbox(
            lat=df_tipo["lat"],
            lon=df_tipo["lon"],
            mode="markers+text",
            marker=dict(
                size=10,
                color=colores.get(tipo, "#000000"),
                symbol="marker"
            ),
            text=df_tipo["nombre"],
            textposition="top center",
            name=tipo.capitalize(),
            hovertemplate="<b>%{text}</b><br>" +
                         f"Tipo: {tipo}<br>" +
                         "Altitud: %{customdata} msnm<br>" +
                         "<extra></extra>",
            customdata=df_tipo["alt"]
        ))
    
    # Agregar rutas - CORREGIDO: QUITAR dash
    if tipo_ruta in ["vehicular", "todas"]:
        coords_ruta = []
        for lugar in RUTA_VEHICULAR:
            if lugar in LUGARES_COORDENADAS:
                coords_ruta.append(LUGARES_COORDENADAS[lugar])
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_ruta],
            lon=[c["lon"] for c in coords_ruta],
            mode="lines+markers",
            line=dict(width=3, color="#e67e22"),
            marker=dict(size=6, color="#e67e22"),
            name="Ruta vehicular",
            hovertemplate="Ruta vehicular<br>" +
                         f"Paucartambo → Mahuayani<br>" +
                         "<extra></extra>"
        ))
    
    if tipo_ruta in ["lomada", "todas"]:
        coords_lomada = []
        for lugar in RUTA_LOMADA:
            if lugar in LUGARES_COORDENADAS:
                coords_lomada.append(LUGARES_COORDENADAS[lugar])
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_lomada],
            lon=[c["lon"] for c in coords_lomada],
            mode="lines+markers",
            line=dict(width=3, color="#8e44ad"),
            marker=dict(size=6, color="#8e44ad"),
            name="Ruta Lomada",
            hovertemplate="Lomada (caminata 24h)<br>" +
                         "Santuario → Tayankani<br>" +
                         "<extra></extra>"
        ))
    
    # Configurar mapa
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=-13.5, lon=-71.4),
            zoom=8
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#e9ecef",
            borderwidth=1
        ),
        title=dict(
            text="🗺️ Mapa Sagrado de Qoyllur Rit'i",
            font=dict(size=20, color="#1e3c72"),
            x=0.5
        )
    )
    
    return fig

def crear_grafico_altitud():
    """Crea gráfico de perfil de altitud"""
    # Ruta completa: Paucartambo → Santuario → Tayankani
    ruta_completa = [
        "Paucartambo",
        "Huancarani",
        "Ccatcca",
        "Ocongate",
        "Mahuayani",
        "SantuarioQoylluriti",
        "MachuCruz",
        "Yanaqocha",
        "Yanaqancha",
        "QquchiyocWayqo",
        "QespiCruz",
        "IntiLloksimuy",
        "Tayancani"
    ]
    
    datos_ruta = []
    distancia = 0
    distancias = [0]
    
    for i, lugar in enumerate(ruta_completa):
        if lugar in LUGARES_COORDENADAS:
            datos_ruta.append({
                "lugar": lugar,
                "altitud": LUGARES_COORDENADAS[lugar]["alt"],
                "distancia": distancia,
                "tipo": LUGARES_COORDENADAS[lugar]["tipo"]
            })
        
        # Calcular distancia aproximada (simplificado)
        if i < len(ruta_completa) - 1:
            distancia += random.randint(8, 15)  # Simulado
    
    df_ruta = pd.DataFrame(datos_ruta)
    
    fig = go.Figure()
    
    # Área bajo la curva
    fig.add_trace(go.Scatter(
        x=df_ruta["distancia"],
        y=df_ruta["altitud"],
        mode="lines+markers",
        name="Perfil de altitud",
        line=dict(color="#1e3c72", width=4),
        marker=dict(
            size=10,
            color=df_ruta["altitud"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="msnm", x=1.05)
        ),
        text=df_ruta["lugar"],
        hovertemplate="<b>%{text}</b><br>" +
                     "Distancia: %{x:.0f} km<br>" +
                     "Altitud: %{y:.0f} msnm<br>" +
                     "<extra></extra>"
    ))
    
    # Destacar puntos clave
    puntos_clave = ["Paucartambo", "SantuarioQoylluriti", "Tayancani"]
    df_clave = df_ruta[df_ruta["lugar"].isin(puntos_clave)]
    
    fig.add_trace(go.Scatter(
        x=df_clave["distancia"],
        y=df_clave["altitud"],
        mode="markers+text",
        marker=dict(size=15, color="#e67e22", symbol="star"),
        text=df_clave["lugar"],
        textposition="top center",
        name="Puntos clave",
        showlegend=True
    ))
    
    fig.update_layout(
        title="⛰️ Perfil de Altitud de la Peregrinación",
        xaxis_title="Distancia aproximada (km)",
        yaxis_title="Altitud (msnm)",
        height=500,
        hovermode="x unified",
        font=dict(family="Inter", size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#e9ecef"),
        xaxis=dict(gridcolor="#e9ecef")
    )
    
    return fig

def crear_grafico_eventos():
    """Crea gráfico de eventos por día"""
    eventos_por_dia = {
        "Día 1 (Sábado)": 1,
        "Día 2 (Domingo)": 9,
        "Día 3 (Lunes)": 6,
        "Noche Lunes-Martes": 1,
        "Día 4 (Martes)": 6,
        "Noche Martes-Miércoles": 2,
        "Día 5 (Miércoles)": 5
    }
    
    df_eventos = pd.DataFrame([
        {"dia": d, "eventos": e} for d, e in eventos_por_dia.items()
    ])
    
    fig = px.bar(
        df_eventos,
        x="dia",
        y="eventos",
        color="eventos",
        color_continuous_scale=["#f39c12", "#e67e22", "#c0392b"],
        title="📋 Eventos Rituales por Día",
        labels={"dia": "Día de la festividad", "eventos": "Número de eventos"}
    )
    
    fig.update_traces(
        texttemplate="%{y}",
        textposition="outside",
        marker_line_color="#1e3c72",
        marker_line_width=1.5
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12),
        xaxis_tickangle=-45
    )
    
    return fig

def mostrar_galeria_fotos(fotos=GALERIA_FOTOS):
    """Muestra galería de fotos en grid"""
    st.markdown("### 📸 Galería de la Peregrinación")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        dias = ["Todos"] + sorted(list(set([f["fecha"] for f in fotos])))
        filtro_dia = st.selectbox("Filtrar por día", dias, key="filtro_dia")
    with col2:
        lugares = ["Todos"] + sorted(list(set([f["lugar"] for f in fotos])))
        filtro_lugar = st.selectbox("Filtrar por lugar", lugares, key="filtro_lugar")
    with col3:
        eventos = ["Todos"] + sorted(list(set([f["evento"] for f in fotos])))
        filtro_evento = st.selectbox("Filtrar por evento", eventos, key="filtro_evento")
    
    # Aplicar filtros
    fotos_filtradas = fotos.copy()
    if filtro_dia != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["fecha"] == filtro_dia]
    if filtro_lugar != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["lugar"] == filtro_lugar]
    if filtro_evento != "Todos":
        fotos_filtradas = [f for f in fotos_filtradas if f["evento"] == filtro_evento]
    
    # Mostrar en grid de 3 columnas
    cols = st.columns(3)
    for i, foto in enumerate(fotos_filtradas[:9]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="photo-card">
                <img src="{foto['url']}" style="width:100%; border-radius:12px; margin-bottom:8px;">
                <div style="padding: 8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:#1e3c72;">{foto['titulo']}</span>
                        <span class="badge-andino">{foto['fecha']}</span>
                    </div>
                    <p style="color:#5d6d7e; font-size:0.9rem; margin-top:6px;">
                        {foto['descripcion']}
                    </p>
                    <div style="display:flex; gap:8px; margin-top:8px;">
                        <span class="chip">📍 {foto['lugar']}</span>
                        <span class="chip">🏷️ {foto['evento'][:20]}...</span>
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
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 40px;">
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
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "❓ Preguntas", 
        "🗺️ Mapa Sagrado", 
        "⛰️ Perfil de Altitud",
        "📋 Eventos",
        "📸 Galería"
    ])
    
    # ========================================================================
    # TAB 1: PREGUNTAS
    # ========================================================================
    with tab1:
        # Inicializar motor
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando conocimiento ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pregunta = st.selectbox(
                "🔍 Selecciona una pregunta:",
                options=[""] + TOP_10_PREGUNTAS,
                format_func=lambda x: "🎯 Elige una pregunta..." if x == "" else x,
                key="selector_preguntas"
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
    # TAB 2: MAPA INTERACTIVO
    # ========================================================================
    with tab2:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 🗺️ Mapa Interactivo de Lugares Sagrados")
        with col2:
            tipo_ruta = st.radio(
                "Mostrar rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True,
                key="selector_ruta"
            )
        
        mapa = crear_mapa_interactivo(tipo_ruta.lower())
        st.plotly_chart(mapa, use_container_width=True)
        
        # Leyenda de lugares
        with st.expander("📍 Ver todos los lugares sagrados"):
            df_lugares = pd.DataFrame([
                {"Lugar": n, "Tipo": d["tipo"], "Altitud": f"{d['alt']} msnm"}
                for n, d in LUGARES_COORDENADAS.items()
            ]).sort_values("Lugar")
            st.dataframe(df_lugares, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 3: PERFIL DE ALTITUD
    # ========================================================================
    with tab3:
        st.markdown("### ⛰️ Perfil de Altitud de la Peregrinación")
        st.markdown("""
        <div style="background: #fff9f0; padding: 16px; border-radius: 12px; margin-bottom: 20px;">
            <span style="font-weight: 600;">📊 DATOS DE ALTITUD:</span><br>
            • Salida: Paucartambo (2,900 msnm)<br>
            • Punto más alto: Glaciar Colque Punku (5,200 msnm)<br>
            • Desnivel acumulado: +2,300 metros<br>
            • Llegada: Tayankani (3,800 msnm)
        </div>
        """, unsafe_allow_html=True)
        
        grafico_altitud = crear_grafico_altitud()
        st.plotly_chart(grafico_altitud, use_container_width=True)
    
    # ========================================================================
    # TAB 4: EVENTOS
    # ========================================================================
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Eventos por Día")
            grafico_eventos = crear_grafico_eventos()
            st.plotly_chart(grafico_eventos, use_container_width=True)
        
        with col2:
            st.markdown("### ⏳ Línea de Tiempo")
            
            timeline_data = {
                "Día 1 (Sábado)": "🟡 Gelación y ensayos",
                "Día 2 (Domingo)": "🟠 Misa · Romería · Viaje",
                "Día 3 (Lunes)": "🔵 Ascenso · Misa Ukukus",
                "Noche Lunes": "🌙 Subida al glaciar",
                "Día 4 (Martes)": "🟢 Bajada · Inicio Lomada",
                "Noche Martes": "⭐ Canto en Q'espi Cruz",
                "Día 5 (Miércoles)": "🔴 Inti Alabado · Retorno"
            }
            
            for dia, evento in timeline_data.items():
                st.markdown(f"""
                <div style="
                    background: white;
                    border-left: 4px solid #e67e22;
                    padding: 12px 16px;
                    margin: 8px 0;
                    border-radius: 0 12px 12px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                ">
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
        <div style="background: #e9ecef; padding: 20px; border-radius: 16px; margin-top: 20px;">
            <span style="font-weight: 600; color: #1e3c72;">📸 ¿Tienes fotos de Qoyllur Rit'i?</span><br>
            <span style="color: #5d6d7e;">
                Puedes agregar tus propias imágenes a la galería. 
                Sube las fotos a GitHub y agrega las URLs en el archivo GALERIA_FOTOS.
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer - Versión Completa</span>
            <span>•</span>
            <span>🗺️ Mapas Interactivos</span>
            <span>•</span>
            <span>📸 Galería Visual</span>
            <span>•</span>
            <span>📊 Gráficos de Altitud</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco · 100% local · Raspberry Pi 5
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()