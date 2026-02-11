#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN DEFINITIVA
✅ Mapas con marcadores y rutas
✅ Mapbox con estilos profesionales
✅ Texto inclusivo para todo público
✅ Interfaz simple y elegante
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
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        border: 1px solid #f0e9e0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.05);
        border-color: #e67e22;
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
    
    /* Tooltips elegantes */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #e67e22;
    }
    
    /* Selectores personalizados */
    .stSelectbox label, .stRadio label {
        color: #1e3c72 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Tarjetas de información */
    .info-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #f0e9e0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.02);
    }
    
    /* Expander personalizado */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #f0e9e0 !important;
        color: #1e3c72 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATOS DE COORDENADAS - TODOS LOS LUGARES SAGRADOS CON DESCRIPCIONES
# ============================================================================
LUGARES_SAGRADOS = {
    # PAUCARTAMBO Y ALREDEDORES
    "Paucartambo": {
        "lat": -13.3127, "lon": -71.6146, "alt": 2900,
        "tipo": "Pueblo de partida",
        "descripcion": "Pueblo andino donde la Nación Paucartambo inicia su peregrinación. Aquí se realizan la misa de envío, la romería al cementerio y el ritual de vestimenta de los danzantes.",
        "icono": "town-hall", "emoji": "🏘️",
        "recomendacion": "Visitar la plaza principal y la iglesia. Hay artesanía textil tradicional."
    },
    "IglesiaPaucartambo": {
        "lat": -13.3178, "lon": -71.6319, "alt": 2900,
        "tipo": "Iglesia colonial",
        "descripcion": "Iglesia principal de Paucartambo, donde se celebra la misa de envío a las 7:00 AM del domingo de partida.",
        "icono": "place-of-worship", "emoji": "⛪",
        "recomendacion": "Arquitectura colonial andina, retablos barrocos."
    },
    "CementerioPaucartambo": {
        "lat": -13.3209, "lon": -71.5959, "alt": 2900,
        "tipo": "Cementerio tradicional",
        "descripcion": "Cementerio local donde la Nación realiza una romería para honrar a los hermanos antiguos que ya partieron.",
        "icono": "cemetery", "emoji": "🕊️",
        "recomendacion": "Lugar de profundo respeto y memoria."
    },
    "PlazaPaucartambo": {
        "lat": -13.3178, "lon": -71.6013, "alt": 2900,
        "tipo": "Plaza de Armas",
        "descripcion": "Plaza principal donde los danzantes ukukus se visten con sus trajes ceremoniales, anunciando públicamente la partida de la Nación.",
        "icono": "square", "emoji": "🎭",
        "recomendacion": "Observar el ritual de vestimenta, lleno de color y tradición."
    },
    
    # RUTA VEHICULAR
    "Huancarani": {
        "lat": -13.5003, "lon": -71.6749, "alt": 3500,
        "tipo": "Cruce vial ceremonial",
        "descripcion": "Punto de encuentro crucial donde la Nación se reúne y espera a todos los danzantes de los distintos distritos que la conforman.",
        "icono": "road", "emoji": "🛣️",
        "recomendacion": "Momento de reencuentro y preparación colectiva."
    },
    "Ccatcca": {
        "lat": -13.6018, "lon": -71.5753, "alt": 3700,
        "tipo": "Pueblo de descanso",
        "descripcion": "Parada tradicional que incluye visita a la iglesia y descanso en la plaza, donde se comparte una comida comunitaria de asado con mote.",
        "icono": "village", "emoji": "🍖",
        "recomendacion": "Probar el asado con mote, tradición culinaria de la peregrinación."
    },
    "IglesiaCcatcca": {
        "lat": -13.6426, "lon": -72.0780, "alt": 3700,
        "tipo": "Iglesia de paso",
        "descripcion": "Templo visitado ritualmente, marcando el paso de la Nación por el pueblo.",
        "icono": "place-of-worship", "emoji": "⛪",
        "recomendacion": "Breve visita de recogimiento."
    },
    "PlazaCcatcca": {
        "lat": -13.6426, "lon": -72.0780, "alt": 3700,
        "tipo": "Plaza comunitaria",
        "descripcion": "Lugar de la comida comunitaria, donde los peregrinos reponen fuerzas.",
        "icono": "square", "emoji": "🏛️",
        "recomendacion": "Compartir alimentos con la comunidad."
    },
    "Ocongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800,
        "tipo": "Pueblo de paso",
        "descripcion": "Localidad donde la Nación visita al prioste, autoridad encargada de la organización de la fiesta.",
        "icono": "town-hall", "emoji": "🏘️",
        "recomendacion": "Conocer la casa del prioste y el mate caliente de bienvenida."
    },
    "CasaPriosteOcongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800,
        "tipo": "Casa del prioste",
        "descripcion": "Residencia de la autoridad festiva, donde la Nación es recibida con mate caliente.",
        "icono": "home", "emoji": "🏠",
        "recomendacion": "Tradición de hospitalidad andina."
    },
    "PlazaOcongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800,
        "tipo": "Plaza ceremonial final",
        "descripcion": "Plaza donde oficialmente termina la festividad para la Nación Paucartambo, con una procesión de entrada.",
        "icono": "square", "emoji": "🎉",
        "recomendacion": "Punto culminante del cierre ceremonial."
    },
    
    # ASCENSO AL SANTUARIO
    "Mahuayani": {
        "lat": -13.6052, "lon": -71.2350, "alt": 4200,
        "tipo": "Inicio de la caminata",
        "descripcion": "Punto donde los peregrinos descienden de los vehículos y comienzan el ascenso a pie hacia el santuario.",
        "icono": "flag", "emoji": "🚩",
        "recomendacion": "Prepararse para el ascenso, el aire se vuelve más fino."
    },
    "SantuarioQoylluriti": {
        "lat": -13.5986, "lon": -71.1914, "alt": 4800,
        "tipo": "Santuario principal",
        "descripcion": "Corazón espiritual de la peregrinación. Alberga la imagen del Señor de Qoyllur Rit'i y es el centro de las ceremonias principales.",
        "icono": "religious-christian", "emoji": "🏔️",
        "recomendacion": "Participar en la Misa de Ukukus, evento único y exclusivo."
    },
    "CeldaUkukusPaucartambo": {
        "lat": -13.5986, "lon": -71.1914, "alt": 4800,
        "tipo": "Alojamiento ritual",
        "descripcion": "Celda en el bofedal donde los ukukus de Paucartambo pasan la noche y organizan sus enseres.",
        "icono": "warehouse", "emoji": "🛏️",
        "recomendacion": "Espacio reservado para los danzantes."
    },
    "Mamachapata": {
        "lat": -13.5989, "lon": -71.1911, "alt": 4800,
        "tipo": "Área procesional",
        "descripcion": "Área dentro del santuario donde la Nación Paucartambo tiene el derecho histórico de ser los primeros en sacar en procesión la imagen del Señor de Tayankani.",
        "icono": "star", "emoji": "✨",
        "recomendacion": "Observar la procesión, privilegio de la Nación más antigua."
    },
    "Pachakunapata": {
        "lat": -13.5983, "lon": -71.1908, "alt": 4800,
        "tipo": "Entrada ceremonial",
        "descripcion": "Lugar de espera y entrada unificada de la Nación al santuario, cuando todos los danzantes están vestidos.",
        "icono": "gate", "emoji": "🚪",
        "recomendacion": "Momento de gran solemnidad y unidad."
    },
    
    # GLACIAR SAGRADO
    "ColquePunku": {
        "lat": -13.5192, "lon": -71.2067, "alt": 5200,
        "tipo": "Glaciar sagrado",
        "descripcion": "Nevado donde los ukukus realizan el ascenso nocturno para rituales de altura. Es el punto más alto de la peregrinación.",
        "icono": "snow", "emoji": "❄️",
        "recomendacion": "Ascenso nocturno con antorchas, experiencia espiritual única."
    },
    
    # LOMADA - CAMINATA DE 24 HORAS
    "MachuCruz": {
        "lat": -13.5900, "lon": -71.1850, "alt": 4900,
        "tipo": "Cruz ceremonial",
        "descripcion": "Punto con una cruz a poco más de una hora del santuario. Lugar de pausa ritual donde se comparte maíz y queso en señal de despedida.",
        "icono": "cross", "emoji": "✝️",
        "recomendacion": "Participar del compartir ritual, símbolo de hermandad."
    },
    "Yanaqocha": {
        "lat": -13.5850, "lon": -71.1800, "alt": 4850,
        "tipo": "Laguna de despedida",
        "descripcion": "Laguna donde los miembros de la Nación realizan rituales de despedida, corriendo y abrazándose.",
        "icono": "water", "emoji": "💧",
        "recomendacion": "Momento emotivo de abrazos y lágrimas."
    },
    "Yanaqancha": {
        "lat": -13.5800, "lon": -71.1750, "alt": 4750,
        "tipo": "Lugar de descanso",
        "descripcion": "Punto de descanso prolongado de 4 horas. Aquí se deja la imagen del Señor de Tayankani y la Nación se viste nuevamente.",
        "icono": "bench", "emoji": "😴",
        "recomendacion": "Descanso reparador antes de la noche de caminata."
    },
    "GrutaYanaqancha": {
        "lat": -13.5800, "lon": -71.1750, "alt": 4750,
        "tipo": "Gruta ceremonial",
        "descripcion": "Gruta donde la Nación desciende bailando después del descanso.",
        "icono": "cave", "emoji": "🕳️",
        "recomendacion": "Danza ceremonial de renovación."
    },
    "QquchiyocWayqo": {
        "lat": -13.5750, "lon": -71.1700, "alt": 4700,
        "tipo": "Riachuelo sagrado",
        "descripcion": "Lugar donde cruzan un riachuelo durante la noche, entre Yanaqancha y Q'espi Cruz.",
        "icono": "river", "emoji": "💦",
        "recomendacion": "Cruce nocturno, sonido del agua en la oscuridad."
    },
    "QespiCruz": {
        "lat": -13.5700, "lon": -71.1650, "alt": 4600,
        "tipo": "Cruz del canto",
        "descripcion": "Hito donde a medianoche toda la Nación canta la 'Canción de Despedida de los Qapaq Qollas'.",
        "icono": "cross", "emoji": "🎵",
        "recomendacion": "Escuchar el canto colectivo bajo las estrellas."
    },
    "IntiLloksimuy": {
        "lat": -13.5600, "lon": -71.1550, "alt": 4500,
        "tipo": "Lugar del Inti Alabado",
        "descripcion": "Punto en las alturas de Tayankani donde se espera la salida del sol. Según la tradición, aquí empieza el Inti Raymi.",
        "icono": "sun", "emoji": "☀️",
        "recomendacion": "Amanecer ceremonial, conexión con el sol ancestral."
    },
    "IntiAlabado_2025": {
        "lat": -13.5600, "lon": -71.1550, "alt": 4500,
        "tipo": "Ceremonia solar",
        "descripcion": "Ritual de saludo al sol al amanecer. Momento cumbre de la lomada.",
        "icono": "star", "emoji": "✨",
        "recomendacion": "Vivir el amanecer en los Andes, experiencia transformadora."
    },
    
    # TAYANKANI - RETORNO Y CIERRE
    "Tayancani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800,
        "tipo": "Pueblo de retorno",
        "descripcion": "Localidad donde se deposita la imagen del Señor de Tayankani al final de la peregrinación.",
        "icono": "village", "emoji": "🏘️",
        "recomendacion": "Cierre del ciclo ceremonial."
    },
    "CapillaTayankani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800,
        "tipo": "Capilla del Señor",
        "descripcion": "Capilla donde reside normalmente todo el año la imagen del Señor de Tayankani, y donde es depositada al final.",
        "icono": "chapel", "emoji": "⛪",
        "recomendacion": "Visitar la morada habitual de la imagen."
    },
    "GrutaTayankani": {
        "lat": -13.5550, "lon": -71.1500, "alt": 3900,
        "tipo": "Gruta ritual final",
        "descripcion": "Gruta en la parte alta del pueblo donde los Ukukus realizan sus últimos rituales antes del ingreso procesional.",
        "icono": "cave", "emoji": "🕯️",
        "recomendacion": "Últimos rituales de los ukukus, cierre de su rol ceremonial."
    },
    "Escalerachayoq": {
        "lat": -13.5650, "lon": -71.1600, "alt": 4700,
        "tipo": "Tramo ritual",
        "descripcion": "Bajada de piedras entre las 3 y 4 de la madrugada, antes de llegar al Inti Alabado.",
        "icono": "mountain", "emoji": "🪨",
        "recomendacion": "Tramo desafiante, preparación para el amanecer."
    },
    
    # DISTRITOS DE LA NACIÓN PAUCARTAMBO
    "Caicay": {
        "lat": -13.5969, "lon": -71.7021, "alt": 3200,
        "tipo": "Distrito integrante",
        "descripcion": "Distrito que conforma la Nación Paucartambo, con comunidades campesinas que participan en la peregrinación.",
        "icono": "town-hall", "emoji": "🏘️",
        "recomendacion": "Comunidad activa en la tradición."
    },
    "Challabamba": {
        "lat": -13.2116, "lon": -71.6544, "alt": 2800,
        "tipo": "Distrito integrante",
        "descripcion": "Distrito de Paucartambo que aporta danzantes a la peregrinación.",
        "icono": "town-hall", "emoji": "🏘️",
        "recomendacion": "Tradición textil y danzas."
    },
    "Colquepata": {
        "lat": -13.4247, "lon": -72.0058, "alt": 3100,
        "tipo": "Distrito integrante",
        "descripcion": "Distrito que forma parte de la Nación Paucartambo.",
        "icono": "town-hall", "emoji": "🏘️",
        "recomendacion": "Paisajes de altura."
    },
    "Ccapi": {
        "lat": -13.8550, "lon": -72.0903, "alt": 3300,
        "tipo": "Localidad invitada",
        "descripcion": "Localidad de Quispicanchis que peregrina tradicionalmente con Paucartambo por ser la nación más antigua.",
        "icono": "town-hall", "emoji": "🤝",
        "recomendacion": "Muestra de hermandad entre provincias."
    },
    "Ccarhuayo": {
        "lat": -13.6145, "lon": -71.4343, "alt": 3400,
        "tipo": "Localidad invitada",
        "descripcion": "Localidad de Quispicanchis que peregrina con la Nación Paucartambo.",
        "icono": "town-hall", "emoji": "🤝",
        "recomendacion": "Integración regional."
    },
    "Mollomarca": {
        "lat": -13.4343, "lon": -71.6374, "alt": 3500,
        "tipo": "Sector alto",
        "descripcion": "Comunidad campesina del sector alto de Paucartambo que participa activamente.",
        "icono": "town-hall", "emoji": "🏔️",
        "recomendacion": "Comunidad de altura."
    }
}

# ============================================================================
# RUTAS DE PEREGRINACIÓN - ACTUALIZADAS
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
# TOP 10 PREGUNTAS - LENGUAJE INCLUSIVO
# ============================================================================
TOP_10_PREGUNTAS = [
    "¿Qué es la fiesta del Señor de Qoyllur Rit'i?",
    "¿Dónde queda el santuario y cómo llegar?",
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
# MAPA PREMIUM CON MAPBOX - MARCADORES Y RUTAS
# ============================================================================
def crear_mapa_qoyllur(tipo_ruta="todas", estilo="outdoor", token_mapbox=None):
    """
    Crea mapa interactivo con marcadores detallados y rutas
    - Outdoor: ideal para montaña (default)
    - Satélite: vista real de los Andes
    - Calle: referencia urbana
    - Oscuro: modo noche
    """
    
    # Configuración de estilos Mapbox
    ESTILOS_MAPBOX = {
        "outdoor": "outdoors-v12",          # Mejor para trekking/montaña
        "satelite": "satellite-streets-v12", # Imagen real con calles
        "calle": "streets-v12",             # Mapa urbano
        "oscuro": "dark-v11"               # Modo noche
    }
    
    # Token por defecto público de Mapbox (limitado, funciona para pruebas)
    DEFAULT_TOKEN = "pk.eyJ1Ijoic3RyZWFtbGl0LWdvb2dsZSIsImEiOiJjbG9uaWJub2EwNnBrMnFvYzNpdjQ5bWNvIn0.7VZJmTOWYQl2g6yVQc9iDw"
    
    fig = go.Figure()
    
    # Usar token proporcionado o el default
    token = token_mapbox if token_mapbox else DEFAULT_TOKEN
    
    # ===== AGREGAR MARCADORES =====
    for lugar_id, lugar in LUGARES_SAGRADOS.items():
        # Definir color según tipo de lugar
        if "glaciar" in lugar["tipo"].lower():
            color = "#3498db"  # Azul hielo
        elif "santuario" in lugar["tipo"].lower() or "capilla" in lugar["tipo"].lower() or "iglesia" in lugar["tipo"].lower():
            color = "#f39c12"  # Dorado
        elif "cruz" in lugar["tipo"].lower():
            color = "#27ae60"  # Verde
        elif "laguna" in lugar["tipo"].lower() or "rio" in lugar["tipo"].lower():
            color = "#16a085"  # Turquesa
        elif "descanso" in lugar["tipo"].lower():
            color = "#8e44ad"  # Púrpura
        elif "pueblo" in lugar["tipo"].lower() or "distrito" in lugar["tipo"].lower():
            color = "#1e3c72"  # Azul andino
        elif "plaza" in lugar["tipo"].lower():
            color = "#e67e22"  # Naranja
        elif "cementerio" in lugar["tipo"].lower():
            color = "#7f8c8d"  # Gris
        elif "inicio" in lugar["tipo"].lower():
            color = "#2c3e50"  # Azul oscuro
        else:
            color = "#e67e22"  # Naranja por defecto
        
        # Tooltip enriquecido
        hover_text = f"""
        <b style='font-size: 16px; color: {color};'>{lugar['emoji']} {lugar_id}</b><br>
        <span style='font-size: 14px; font-weight: 500;'>{lugar['tipo']}</span><br>
        <br>
        <span style='font-size: 13px;'>{lugar['descripcion']}</span><br>
        <br>
        <span style='font-size: 12px;'>
        📏 <b>Altitud:</b> {lugar['alt']:,} msnm<br>
        🧭 <b>Coordenadas:</b> {lugar['lat']:.4f}, {lugar['lon']:.4f}<br>
        💡 <b>Recomendación:</b> {lugar['recomendacion']}
        </span>
        """
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=dict(
                size=12,
                color=color,
                symbol="marker",
                allowoverlap=False
            ),
            name=lugar_id,
            text=lugar_id,
            hovertemplate=hover_text + "<extra></extra>",
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=color,
                font=dict(size=12, color="#1e3c72")
            ),
            showlegend=False
        ))
    
    # ===== AGREGAR RUTA VEHICULAR =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords_ruta = [LUGARES_SAGRADOS[l] for l in RUTA_VEHICULAR if l in LUGARES_SAGRADOS]
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_ruta],
            lon=[c["lon"] for c in coords_ruta],
            mode="lines+markers",
            line=dict(width=4, color="#e67e22"),
            marker=dict(size=8, color="#e67e22", symbol="marker"),
            name="🚌 Ruta vehicular",
            hovertemplate="<b>Ruta vehicular</b><br>Paucartambo → Mahuayani<br>Distancia: ~85 km<br><extra></extra>"
        ))
    
    # ===== AGREGAR RUTA LOMADA =====
    if tipo_ruta in ["lomada", "todas"]:
        coords_lomada = [LUGARES_SAGRADOS[l] for l in RUTA_LOMADA if l in LUGARES_SAGRADOS]
        
        fig.add_trace(go.Scattermapbox(
            lat=[c["lat"] for c in coords_lomada],
            lon=[c["lon"] for c in coords_lomada],
            mode="lines+markers",
            line=dict(width=4, color="#8e44ad"),
            marker=dict(size=8, color="#8e44ad", symbol="marker"),
            name="🚶 Lomada (24h)",
            hovertemplate="<b>Lomada / Loman Pureq</b><br>Caminata ritual de 24 horas<br>Santuario → Tayankani<br>Distancia: ~35 km<br><extra></extra>"
        ))
    
    # ===== CONFIGURAR MAPA =====
    estilo_seleccionado = ESTILOS_MAPBOX.get(estilo, "outdoors-v12")
    
    fig.update_layout(
        mapbox=dict(
            style=estilo_seleccionado,
            center=dict(lat=-13.5, lon=-71.4),
            zoom=8.2,
            accesstoken=token
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
            borderwidth=1,
            font=dict(size=11)
        )
    )
    
    return fig

# ============================================================================
# PERFIL DE ALTITUD - VERSIÓN CORREGIDA
# ============================================================================
def crear_perfil_altitud():
    """Perfil de altitud simple y funcional"""
    
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
        plot_bgcolor="white",
        font=dict(family="Inter", size=12)
    )
    
    return fig

# ============================================================================
# APP PRINCIPAL - VERSIÓN DEFINITIVA
# ============================================================================
def main():
    
    # ===== HEADER REDISEÑADO - INCLUSIVO Y ELEGANTE =====
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 32px;">
        <div style="font-size: 4.5rem; background: linear-gradient(135deg, #1e3c72, #2c5a8c); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🏔️
        </div>
        <div>
            <h1 style="margin: 0; font-size: 3.2rem;">Qoyllur Rit'i</h1>
            <p style="margin: 8px 0 0 0; color: #5d6d7e; font-size: 1.2rem; font-weight: 400;">
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
    
    # ===== SIDEBAR - CONFIGURACIÓN MAPBOX =====
    with st.sidebar:
        st.markdown("### 🗺️ Mejora tu experiencia")
        
        token_mapbox = st.text_input(
            "🔑 Token de Mapbox (opcional)",
            type="password",
            placeholder="pk.eyJ1...",
            help="Obtén tu token gratis en mapbox.com. Sin token, usamos un mapa base gratuito."
        )
        
        if token_mapbox:
            st.success("✅ Token configurado - Mapas de alta calidad")
            st.info("🌍 Disfruta de imágenes satelitales y estilos profesionales")
        else:
            st.info("""
            **✨ Sin token también funciona**
            
            Usamos un token público de prueba con límite gratuito.
            Para uso profesional, obtén tu token en [mapbox.com](https://mapbox.com)
            """)
        
        st.markdown("---")
        
        # ===== INFORMACIÓN CONTEXTUAL =====
        st.markdown("""
        ### 📿 Sobre la festividad
        
        **Qoyllur Rit'i** (quechua: *Nieve brillante*) es una de las peregrinaciones andinas más grandes de los Andes.
        
        **🗓️ Cuándo:**  
        58 días después del Miércoles de Ceniza
        
        **⛰️ Dónde:**  
        Santuario de Sinakara, Cusco (4,800 - 5,200 msnm)
        
        **👥 Quiénes:**  
        Ocho naciones, lideradas por la Nación Paucartambo
        
        **✨ Por qué es especial:**  
        Fusión única de tradición católica y cosmovisión andina. Patrimonio Cultural de la Nación.
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff9f0, #fff); padding: 20px; border-radius: 16px; border: 1px solid #ffe0b2;">
            <span style="font-weight: 700; color: #e67e22;">📌 DATO CURIOSO</span><br>
            <span style="color: #5d6d7e; font-size: 0.95rem;">
            Los ukukus o ukumaris representan al oso andino y son los únicos que pueden subir al glaciar. Actúan como protectores y justicieros.
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== TABS PRINCIPALES =====
    tab1, tab2, tab3, tab4 = st.tabs([
        "❓ Preguntas frecuentes", 
        "🗺️ Mapa interactivo", 
        "⛰️ Perfil de ruta",
        "📋 Guía de la festividad"
    ])
    
    # ===== TAB 1: PREGUNTAS FRECUENTES =====
    with tab1:
        if 'rag' not in st.session_state:
            with st.spinner("🏔️ Cargando sabiduría ancestral..."):
                st.session_state.rag = cargar_conocimiento()
        
        st.markdown("""
        ### ❓ Resuelve tus dudas sobre Qoyllur Rit'i
        
        Selecciona una pregunta frecuente o escribe la tuya propia. Nuestro sistema busca en el conocimiento recopilado por investigadores.
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pregunta = st.selectbox(
                "🔍 Preguntas frecuentes:",
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
                        <span style="font-size: 0.8rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px;">
                            Respuesta
                        </span>
                        <div style="font-size: 1.3rem; font-weight: 600; color: #1e3c72;">
                            {pregunta}
                        </div>
                    </div>
                </div>
                <div style="font-size: 1.1rem; line-height: 1.8; color: #2c3e50;">
                    {respuesta}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TAB 2: MAPA INTERACTIVO - VERSIÓN MEJORADA =====
    with tab2:
        st.markdown("""
        ### 🗺️ Explora los lugares sagrados
        
        Cada punto en el mapa representa un lugar con historia y significado. 
        Haz clic en los marcadores para conocer su importancia en la peregrinación.
        """)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("#### 🎯 Mostrar en el mapa:")
        with col2:
            tipo_ruta = st.radio(
                "Rutas:",
                ["Todas", "Vehicular", "Lomada"],
                horizontal=True,
                label_visibility="collapsed"
            )
        with col3:
            estilo = st.selectbox(
                "Estilo:",
                ["outdoor", "satelite", "calle", "oscuro"],
                format_func=lambda x: {
                    "outdoor": "🏞️ Outdoor (trekking)",
                    "satelite": "🛰️ Satélite",
                    "calle": "🏙️ Calle",
                    "oscuro": "🌙 Oscuro"
                }[x],
                label_visibility="collapsed"
            )
        
        # Generar mapa
        mapa = crear_mapa_qoyllur(
            tipo_ruta=tipo_ruta.lower(),
            estilo=estilo,
            token_mapbox=token_mapbox if token_mapbox else None
        )
        
        st.plotly_chart(mapa, use_container_width=True)
        
        # Estadísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares sagrados", len(LUGARES_SAGRADOS))
        with col2:
            st.metric("🚌 Ruta vehicular", "85 km")
        with col3:
            st.metric("🚶 Lomada", "35 km · 24h")
        with col4:
            st.metric("🏔️ Altitud máxima", "5,200 msnm")
        
        # Buscador de lugares
        with st.expander("🔍 Buscar lugar específico", expanded=False):
            lugar_buscar = st.selectbox(
                "Selecciona un lugar para ver más detalles:",
                options=[""] + sorted(LUGARES_SAGRADOS.keys()),
                format_func=lambda x: "Elige un lugar..." if x == "" else f"{LUGARES_SAGRADOS[x]['emoji']} {x}"
            )
            
            if lugar_buscar and lugar_buscar in LUGARES_SAGRADOS:
                lugar = LUGARES_SAGRADOS[lugar_buscar]
                st.markdown(f"""
                <div style="background: white; padding: 24px; border-radius: 16px; border-left: 6px solid #e67e22;">
                    <h4 style="margin: 0 0 8px 0; color: #1e3c72;">{lugar['emoji']} {lugar_buscar}</h4>
                    <p style="color: #e67e22; font-weight: 600; margin: 0 0 12px 0;">{lugar['tipo']}</p>
                    <p style="color: #2c3e50; line-height: 1.6;">{lugar['descripcion']}</p>
                    <p style="color: #27ae60; font-style: italic; margin-top: 12px;">💡 {lugar['recomendacion']}</p>
                    <div style="display: flex; gap: 16px; margin-top: 16px;">
                        <span style="background: #e9ecef; padding: 6px 16px; border-radius: 30px; font-size: 0.9rem;">
                            📏 {lugar['alt']:,} msnm
                        </span>
                        <span style="background: #e9ecef; padding: 6px 16px; border-radius: 30px; font-size: 0.9rem;">
                            🧭 {lugar['lat']:.4f}, {lugar['lon']:.4f}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== TAB 3: PERFIL DE RUTA =====
    with tab3:
        st.markdown("""
        ### ⛰️ La ruta paso a paso
        
        Conoce el perfil de altitud de la peregrinación. 
        Desde Paucartambo (2,900 msnm) hasta el glaciar Colque Punku (5,200 msnm).
        """)
        
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
    
    # ===== TAB 4: GUÍA DE LA FESTIVIDAD =====
    with tab4:
        st.markdown("""
        ### 📋 Todo lo que necesitas saber
        
        Una guía completa de la peregrinación, día por día.
        """)
        
        # Días en columnas
        dias = {
            "Día 1 - Sábado": {
                "emoji": "🟡",
                "evento": "Preparación",
                "detalle": "Gelación y ensayos en Paucartambo",
                "hora": "Todo el día",
                "lugar": "Paucartambo"
            },
            "Día 2 - Domingo": {
                "emoji": "🟠",
                "evento": "Partida",
                "detalle": "Misa, romería, vestimenta y viaje a Mahuayani",
                "hora": "07:00 - 20:00",
                "lugar": "Paucartambo → Mahuayani"
            },
            "Día 3 - Lunes": {
                "emoji": "🔵",
                "evento": "Ascenso",
                "detalle": "Caminata al santuario y Misa de Ukukus",
                "hora": "05:00 - 18:00",
                "lugar": "Mahuayani → Santuario"
            },
            "Noche Lunes": {
                "emoji": "🌙",
                "evento": "Glaciar",
                "detalle": "Ascenso nocturno al Colque Punku",
                "hora": "23:00 - 05:00",
                "lugar": "Colque Punku"
            },
            "Día 4 - Martes": {
                "emoji": "🟢",
                "evento": "Lomada",
                "detalle": "Descenso del glaciar e inicio de caminata de 24h",
                "hora": "09:00 - 21:00",
                "lugar": "Santuario → Yanaqancha"
            },
            "Noche Martes": {
                "emoji": "⭐",
                "evento": "Canto",
                "detalle": "Canto de despedida en Q'espi Cruz",
                "hora": "00:00",
                "lugar": "Q'espi Cruz"
            },
            "Día 5 - Miércoles": {
                "emoji": "🔴",
                "evento": "Retorno",
                "detalle": "Inti Alabado y procesión final en Ocongate",
                "hora": "04:00 - 13:00",
                "lugar": "Tayankani → Ocongate"
            }
        }
        
        cols = st.columns(4)
        for i, (dia, info) in enumerate(dias.items()):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 16px; 
                            border-left: 4px solid #e67e22; margin-bottom: 20px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 1.5rem;">{info['emoji']}</span>
                        <span style="font-weight: 700; color: #1e3c72;">{dia}</span>
                    </div>
                    <p style="font-weight: 600; color: #e67e22; margin: 4px 0;">{info['evento']}</p>
                    <p style="color: #5d6d7e; font-size: 0.9rem; margin: 8px 0;">{info['detalle']}</p>
                    <div style="display: flex; justify-content: space-between; margin-top: 12px;">
                        <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                            🕐 {info['hora']}
                        </span>
                        <span style="background: #e9ecef; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                            📍 {info['lugar']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== FOOTER =====
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 48px; margin-bottom: 24px;">
            <span style="color: #1e3c72; font-weight: 600;">🙌 Para todos los públicos</span>
            <span style="color: #7f8c8d;">•</span>
            <span style="color: #1e3c72; font-weight: 600;">📚 Conocimiento libre</span>
            <span style="color: #7f8c8d;">•</span>
            <span style="color: #1e3c72; font-weight: 600;">🏔️ Cultura viva</span>
        </div>
        <div style="font-size: 0.85rem; color: #95a5a6; max-width: 800px; margin: 0 auto;">
            Qoyllur Rit'i Explorer es una herramienta educativa y de difusión cultural.
            Basado en ontología RDF y trabajo de campo etnográfico.
            Código abierto · 100% local · Listo para Raspberry Pi
        </div>
        <div style="margin-top: 24px; font-size: 0.8rem; color: #bdc3c7;">
            Con gratitud a la Nación Paucartambo y a todos los peregrinos que mantienen viva esta tradición.
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()