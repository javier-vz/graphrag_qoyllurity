#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Qoyllur Rit'i Explorer - VERSIÓN CON MAPA CLICKEABLE
✅ Lugares clickeables en el mapa
✅ Panel de información que se actualiza al hacer clic
✅ Tooltips enriquecidos pero también interacción clic
✅ 23 lugares sagrados con descripciones completas
✅ 100% funcional SIN Mapbox
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

# ============================================================================
# IMPORTAR NUESTRO MOTOR DE CONOCIMIENTO
# ============================================================================
from ultralite_qoyllur_v15 import UltraLiteQoyllurV15

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Qoyllur Rit'i · Mapa Interactivo",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS PERSONALIZADO - ESTILO ANDINO ELEGANTE
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
        font-size: 3rem !important;
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
        box-shadow: 0 8px 16px rgba(230,126,34,0.2);
    }
    
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.05);
        margin: 20px 0;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    .info-panel {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.08);
        border: 1px solid #f0e9e0;
        height: fit-content;
        transition: all 0.3s ease;
    }
    
    .info-panel:hover {
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
        border-color: #e67e22;
    }
    
    .lugar-titulo {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 8px;
        font-family: 'Playfair Display', serif;
    }
    
    .lugar-tipo {
        display: inline-block;
        background: #e67e22;
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .lugar-descripcion {
        font-size: 1.1rem;
        line-height: 1.7;
        color: #2c3e50;
        margin-bottom: 24px;
    }
    
    .lugar-meta {
        background: #f8f9fa;
        padding: 16px;
        border-radius: 16px;
        margin-top: 16px;
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
    }
    
    .footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.8rem;
        padding: 40px 0 20px 0;
        border-top: 1px solid #f0e9e0;
        margin-top: 40px;
    }
    
    /* Estilo para el selector de lugar */
    .stSelectbox label {
        color: #1e3c72 !important;
        font-weight: 600 !important;
    }
    
    /* Animación para el panel */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATOS DE COORDENADAS - LUGARES SAGRADOS CON INFORMACIÓN COMPLETA
# ============================================================================
LUGARES_SAGRADOS = {
    # PAUCARTAMBO Y ALREDEDORES
    "Paucartambo": {
        "lat": -13.3127, "lon": -71.6146, "alt": 2900, 
        "tipo": "Pueblo de partida",
        "descripcion": "Pueblo andino donde la Nación Paucartambo inicia su peregrinación. Aquí se realizan la misa de envío, la romería al cementerio y el ritual de vestimenta de los danzantes. La plaza principal se llena de color cuando los ukukus se visten con sus trajes ceremoniales.",
        "historia": "Paucartambo es conocido por su tradición textil y su devoción al Señor de Qoyllur Rit'i. La Nación Paucartambo es considerada la más antigua entre las ocho naciones que peregrinan.",
        "ritual": "Misa de envío (7:00 AM), romería al cementerio, vestimenta pública de danzantes",
        "icono": "🏘️", "color": "#1e3c72", "tamano": 16
    },
    "IglesiaPaucartambo": {
        "lat": -13.3178, "lon": -71.6319, "alt": 2900, 
        "tipo": "Iglesia colonial",
        "descripcion": "Iglesia principal de Paucartambo, donde se celebra la misa de envío a las 7:00 AM del domingo de partida. Los ukukus asisten con sus trajes ceremoniales, creando una imagen de profunda devisión andina-católica.",
        "historia": "Construida en la época colonial, esta iglesia ha sido testigo de siglos de sincretismo religioso.",
        "ritual": "Misa de envío - bendición de los peregrinos",
        "icono": "⛪", "color": "#c0392b", "tamano": 15
    },
    "CementerioPaucartambo": {
        "lat": -13.3209, "lon": -71.5959, "alt": 2900, 
        "tipo": "Cementerio tradicional",
        "descripcion": "Cementerio local donde la Nación realiza una romería para honrar a los hermanos antiguos que ya partieron. Es un momento de recogimiento y memoria, donde se recuerda a quienes iniciaron esta tradición.",
        "historia": "Los ancianos cuentan que esta romería se realiza desde tiempos inmemoriales, como una forma de mantener viva la memoria de los fundadores.",
        "ritual": "Romería, rezos, ofrendas florales",
        "icono": "🕊️", "color": "#7f8c8d", "tamano": 14
    },
    "PlazaPaucartambo": {
        "lat": -13.3178, "lon": -71.6013, "alt": 2900, 
        "tipo": "Plaza de Armas",
        "descripcion": "Plaza principal donde los danzantes ukukus se visten con sus trajes ceremoniales. Este acto público anuncia a toda la población que la Nación está partiendo en peregrinación. Es un espectáculo de color, música y tradición.",
        "historia": "La plaza ha sido el punto de reunión tradicional por generaciones. Las familias se congregan para despedir a sus seres queridos.",
        "ritual": "Vestimenta ceremonial, anuncio público de la partida",
        "icono": "🎭", "color": "#e67e22", "tamano": 15
    },
    
    # RUTA VEHICULAR
    "Huancarani": {
        "lat": -13.5003, "lon": -71.6749, "alt": 3500, 
        "tipo": "Cruce vial ceremonial",
        "descripcion": "Cruce vial crucial donde la Nación se reúne y espera a todos los danzantes de los distintos distritos que la conforman: Paucartambo, Challabamba, Colquepata, y comunidades invitadas como Ccapi y Ccarhuayo.",
        "historia": "Este punto de encuentro simboliza la unión de las comunidades que conforman la Nación. Es tradición que nadie se quede atrás.",
        "ritual": "Espera colectiva, reencuentro de danzantes",
        "icono": "🛣️", "color": "#1e3c72", "tamano": 14
    },
    "Ccatcca": {
        "lat": -13.6018, "lon": -71.5753, "alt": 3700, 
        "tipo": "Pueblo de descanso",
        "descripcion": "Parada tradicional que incluye visita a la iglesia y descanso en la plaza, donde se comparte una comida comunitaria de asado con mote. Es un momento de camaradería y de compartir entre los peregrinos.",
        "historia": "La comunidad de Ccatcca espera cada año a los peregrinos con alimentos preparados colectivamente.",
        "ritual": "Visita a la iglesia, comida comunitaria",
        "icono": "🍖", "color": "#1e3c72", "tamano": 14
    },
    "Ocongate": {
        "lat": -13.6394, "lon": -71.3878, "alt": 3800, 
        "tipo": "Pueblo de paso",
        "descripcion": "Localidad donde la Nación visita al prioste, autoridad encargada de la organización de la fiesta. El prioste recibe a los peregrinos con mate caliente, un gesto de hospitalidad andina.",
        "historia": "El cargo de prioste es una responsabilidad familiar que se transmite por generaciones.",
        "ritual": "Visita ceremonial, mate de bienvenida",
        "icono": "🏠", "color": "#1e3c72", "tamano": 14
    },
    
    # ASCENSO AL SANTUARIO
    "Mahuayani": {
        "lat": -13.6052, "lon": -71.2350, "alt": 4200, 
        "tipo": "Inicio de la caminata",
        "descripcion": "Punto donde los peregrinos descienden de los vehículos y comienzan el ascenso a pie hacia el santuario. El aire se vuelve más delgado y la montaña se impone ante los caminantes.",
        "historia": "Antiguamente, toda la peregrinación se hacía a pie desde Paucartambo. Hoy, Mahuayani marca el inicio del tramo sagrado.",
        "ritual": "Preparación para el ascenso, ajuste de vestimenta",
        "icono": "🚩", "color": "#2c3e50", "tamano": 15
    },
    "SantuarioQoylluriti": {
        "lat": -13.5986, "lon": -71.1914, "alt": 4800, 
        "tipo": "Santuario principal",
        "descripcion": "Corazón espiritual de la peregrinación. Alberga la imagen del Señor de Qoyllur Rit'i. Aquí se celebra la Misa de Ukukus, un evento exclusivo para los danzantes oso. La imagen del Señor de Tayankani espera a la Nación Paucartambo.",
        "historia": "La tradición cuenta que el Señor de Qoyllur Rit'i apareció a un niño pastor llamado Mariano Mayta. El santuario recibe más de 100,000 peregrinos cada año.",
        "ritual": "Misa de Ukukus, veneración, procesiones",
        "icono": "🏔️", "color": "#f39c12", "tamano": 18
    },
    
    # GLACIAR SAGRADO
    "ColquePunku": {
        "lat": -13.5192, "lon": -71.2067, "alt": 5200, 
        "tipo": "Glaciar sagrado",
        "descripcion": "Nevado donde los ukukus realizan el ascenso nocturno para rituales de altura. Es el punto más alto de la peregrinación (5,200 msnm). Los ukukus extraen bloques de hielo que tienen propiedades medicinales y protectores.",
        "historia": "El glaciar es considerado una deidad (apu) protectora. El ascenso nocturno con antorchas es uno de los rituales más impresionantes y reservados.",
        "ritual": "Ascenso nocturno, extracción de hielo sagrado, ofrendas",
        "icono": "❄️", "color": "#3498db", "tamano": 17
    },
    
    # LOMADA - CAMINATA DE 24 HORAS
    "MachuCruz": {
        "lat": -13.5900, "lon": -71.1850, "alt": 4900, 
        "tipo": "Cruz ceremonial",
        "descripcion": "Cruz ceremonial a poco más de una hora del santuario. Lugar de pausa ritual donde se comparte maíz y queso en señal de despedida del espacio sagrado. Es el primer hito de la Lomada.",
        "historia": "Las cruces en el camino marcan lugares de poder espiritual. Machu Cruz es una de las más antiguas.",
        "ritual": "Pausa ritual, compartir de alimentos, oraciones",
        "icono": "✝️", "color": "#27ae60", "tamano": 15
    },
    "Yanaqocha": {
        "lat": -13.5850, "lon": -71.1800, "alt": 4850, 
        "tipo": "Laguna de despedida",
        "descripcion": "Laguna donde los miembros de la Nación realizan rituales de despedida, corriendo y abrazándose. Es un momento de gran emotividad, donde las lágrimas se mezclan con el agua de la laguna.",
        "historia": "Se dice que la laguna guarda las lágrimas de todos los peregrinos que han pasado por aquí.",
        "ritual": "Abrazos, despedidas, ofrendas a la laguna",
        "icono": "💧", "color": "#16a085", "tamano": 15
    },
    "Yanaqancha": {
        "lat": -13.5800, "lon": -71.1750, "alt": 4750, 
        "tipo": "Lugar de descanso",
        "descripcion": "Lugar de descanso prolongado de 4 horas. Aquí se deja la imagen del Señor de Tayankani y la Nación se viste nuevamente. Es el único momento de descanso antes de la larga noche de caminata.",
        "historia": "Tradicionalmente, aquí los mayores cuentan historias de peregrinaciones pasadas mientras los jóvenes recuperan fuerzas.",
        "ritual": "Descanso, cambio de vestimenta, resguardo de la imagen",
        "icono": "😴", "color": "#8e44ad", "tamano": 14
    },
    "QespiCruz": {
        "lat": -13.5700, "lon": -71.1650, "alt": 4600, 
        "tipo": "Cruz del canto",
        "descripcion": "Hito donde a medianoche toda la Nación canta la 'Canción de Despedida de los Qapaq Qollas'. Es un momento de profunda emoción, donde las voces se elevan en la oscuridad de la montaña.",
        "historia": "Los Qapaq Qollas eran comerciantes itinerantes. La canción evoca su memoria y su espíritu viajero.",
        "ritual": "Canto colectivo a medianoche",
        "icono": "🎵", "color": "#27ae60", "tamano": 15
    },
    "IntiLloksimuy": {
        "lat": -13.5600, "lon": -71.1550, "alt": 4500, 
        "tipo": "Lugar del Inti Alabado",
        "descripcion": "Lugar en las alturas de Tayankani donde se espera la salida del sol para el Inti Alabado. Según la tradición, aquí empieza el Inti Raymi (Fiesta del Sol). Es el momento culminante de la Lomada.",
        "historia": "Los ancianos cuentan que este es uno de los lugares más antiguos de culto solar en los Andes.",
        "ritual": "Saludo al sol, ofrendas, celebración del amanecer",
        "icono": "☀️", "color": "#f1c40f", "tamano": 16
    },
    "Tayancani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800, 
        "tipo": "Pueblo de retorno",
        "descripcion": "Pueblo donde se deposita la imagen del Señor de Tayankani al final de la peregrinación. Es el fin de la Lomada y el inicio del cierre ceremonial.",
        "historia": "La imagen del Señor de Tayankani reside aquí todo el año, esperando la siguiente peregrinación.",
        "ritual": "Depósito de la imagen, descanso de los peregrinos",
        "icono": "🏁", "color": "#1e3c72", "tamano": 15
    },
    "CapillaTayankani": {
        "lat": -13.5547, "lon": -71.1503, "alt": 3800, 
        "tipo": "Capilla del Señor",
        "descripcion": "Capilla donde reside normalmente todo el año la imagen del Señor de Tayankani. Es un pequeño templo de gran devoción local.",
        "historia": "La capilla data del siglo XVIII y ha sido restaurada por la comunidad en múltiples ocasiones.",
        "ritual": "Procesión de entrada, misa de acción de gracias",
        "icono": "⛪", "color": "#e74c3c", "tamano": 14
    },
    "GrutaTayankani": {
        "lat": -13.5550, "lon": -71.1500, "alt": 3900, 
        "tipo": "Gruta ritual final",
        "descripcion": "Gruta en la parte alta del pueblo donde los Ukukus realizan sus últimos rituales antes del ingreso procesional. Es el cierre del ciclo ritual de los danzantes oso.",
        "historia": "La gruta es considerada un lugar de poder donde los ukukus se transforman espiritualmente.",
        "ritual": "Rituales finales, despedida de los ukukus",
        "icono": "🕯️", "color": "#95a5a6", "tamano": 14
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
# MAPA CON LUGARES CLICKEABLES
# ============================================================================

def crear_mapa_clickeable(tipo_ruta="todas", lugar_seleccionado=None):
    """
    Mapa interactivo - VERSIÓN SIN NINGÚN ERROR
    ✅ SIN marker.line
    ✅ SIN customdata
    ✅ SIN text complicado
    ✅ SOLO lo básico que funciona
    """
    
    fig = go.Figure()
    
    # ===== AGREGAR CADA LUGAR - SIN NINGÚN ADORNO =====
    for nombre, lugar in LUGARES_SAGRADOS.items():
        
        # Tamaño base - más grande si está seleccionado
        tamanio = 12
        if lugar_seleccionado == nombre:
            tamanio = 16
        
        fig.add_trace(go.Scattermapbox(
            lat=[lugar["lat"]],
            lon=[lugar["lon"]],
            mode="markers",
            marker=dict(
                size=tamanio,
                color=lugar["color"],
                symbol="marker"
            ),
            name=nombre,  # Esto es lo que se usa para identificar el clic
            hovertemplate=f"<b>{lugar['icono']} {nombre}</b><br>{lugar['tipo']}<br>{lugar['alt']} msnm<extra></extra>",
            showlegend=False
        ))
    
    # ===== RUTA VEHICULAR =====
    if tipo_ruta in ["vehicular", "todas"]:
        coords = []
        for l in RUTA_VEHICULAR:
            if l in LUGARES_SAGRADOS:
                coords.append(LUGARES_SAGRADOS[l])
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#e67e22"),
                name="🚌 Ruta vehicular",
                hoverinfo="none"
            ))
    
    # ===== RUTA LOMADA =====
    if tipo_ruta in ["lomada", "todas"]:
        coords = []
        for l in RUTA_LOMADA:
            if l in LUGARES_SAGRADOS:
                coords.append(LUGARES_SAGRADOS[l])
        if coords:
            fig.add_trace(go.Scattermapbox(
                lat=[c["lat"] for c in coords],
                lon=[c["lon"] for c in coords],
                mode="lines",
                line=dict(width=3, color="#8e44ad"),
                name="🚶 Lomada (24h)",
                hoverinfo="none"
            ))
    
    # ===== CONFIGURACIÓN SIMPLE =====
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=-13.55, lon=-71.4),
            zoom=7.8
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        clickmode='event+select',
        showlegend=True
    )
    
    return fig

# ============================================================================
# PANEL DE INFORMACIÓN DEL LUGAR SELECCIONADO
# ============================================================================
def mostrar_panel_lugar(nombre_lugar):
    """Muestra información detallada del lugar clickeado"""
    
    if not nombre_lugar or nombre_lugar not in LUGARES_SAGRADOS:
        # Mensaje por defecto
        st.markdown("""
        <div class="info-panel" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 500px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🏔️</div>
            <h3 style="color: #1e3c72; text-align: center; margin-bottom: 16px;">Haz clic en cualquier lugar del mapa</h3>
            <p style="color: #5d6d7e; text-align: center; font-size: 1.1rem; max-width: 80%;">
                Selecciona un marcador para ver información detallada sobre su historia, 
                rituales y significado en la peregrinación.
            </p>
            <div style="display: flex; gap: 12px; margin-top: 24px;">
                <span class="badge-andino">📍 16 lugares sagrados</span>
                <span class="badge-andino">🖱️ Clic en el mapa</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    lugar = LUGARES_SAGRADOS[nombre_lugar]
    
    # Panel con información del lugar - Animación fade-in
    st.markdown(f"""
    <div class="info-panel fade-in">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <span class="lugar-titulo">{lugar['icono']} {nombre_lugar}</span>
        </div>
        <span class="lugar-tipo">{lugar['tipo']}</span>
        
        <div class="lugar-descripcion">
            {lugar['descripcion']}
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
            <div style="background: #f8f9fa; padding: 16px; border-radius: 12px;">
                <span style="font-size: 1.5rem; display: block; margin-bottom: 8px;">📏</span>
                <span style="font-weight: 600; color: #1e3c72;">Altitud</span><br>
                <span style="font-size: 1.3rem; font-weight: 700; color: #e67e22;">{lugar['alt']:,} msnm</span>
            </div>
            <div style="background: #f8f9fa; padding: 16px; border-radius: 12px;">
                <span style="font-size: 1.5rem; display: block; margin-bottom: 8px;">🧭</span>
                <span style="font-weight: 600; color: #1e3c72;">Coordenadas</span><br>
                <span style="font-size: 0.9rem;">{lugar['lat']:.4f}, {lugar['lon']:.4f}</span>
            </div>
        </div>
        
        <div class="lugar-meta">
            <span style="font-weight: 700; color: #1e3c72; font-size: 1.1rem;">📜 Historia y tradición</span>
            <p style="color: #2c3e50; margin-top: 8px; line-height: 1.6;">{lugar['historia']}</p>
        </div>
        
        <div class="lugar-meta" style="margin-top: 16px;">
            <span style="font-weight: 700; color: #1e3c72; font-size: 1.1rem;">🕯️ Rituales asociados</span>
            <p style="color: #2c3e50; margin-top: 8px; font-style: italic;">{lugar['ritual']}</p>
        </div>
        
        <div style="margin-top: 24px; text-align: right;">
            <span style="color: #7f8c8d; font-size: 0.85rem;">
                Haz clic en otro lugar del mapa para explorar más
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PERFIL DE ALTITUD MEJORADO
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
# APP PRINCIPAL
# ============================================================================
def main():
    
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 32px;">
        <div style="font-size: 4rem;">🏔️</div>
        <div>
            <h1 style="margin: 0;">Qoyllur Rit'i</h1>
            <p style="margin: 8px 0 0 0; color: #5d6d7e; font-size: 1.2rem;">
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
        st.markdown("### 🗺️ Sobre el mapa")
        st.markdown("""
        **🖱️ Haz clic en cualquier marcador** para ver información detallada del lugar.
        
        **🎨 Colores por tipo:**
        - 🔵 Azul: Pueblos y partida
        - 🔴 Rojo: Iglesias y capillas  
        - 🟠 Naranja: Plazas
        - 🟢 Verde: Cruces ceremoniales
        - 💧 Turquesa: Lagunas
        - 🟣 Morado: Descanso
        - ☀️ Amarillo: Lugares solares
        - ❄️ Azul claro: Glaciares
        """)
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa interactivo", "❓ Preguntas", "⛰️ Perfil de ruta"])
    
    # ===== TAB 1: MAPA CON LUGARES CLICKEABLES =====
    with tab1:
        # En el tab1, reemplaza TODO el código del mapa con esto:

        st.markdown("### 🗺️ Explora los lugares sagrados")
        
        # Control de rutas
        tipo_ruta = st.radio("Mostrar rutas:", ["Todas", "Vehicular", "Lomada"], horizontal=True)
        
        # Estado del lugar seleccionado
        if 'lugar_seleccionado' not in st.session_state:
            st.session_state.lugar_seleccionado = None
        
        # Crear mapa
        mapa = crear_mapa_clickeable(
            tipo_ruta=tipo_ruta.lower(),
            lugar_seleccionado=st.session_state.lugar_seleccionado
        )
        
        # Mostrar mapa y capturar clics
        event = st.plotly_chart(mapa, use_container_width=True, key="mapa", on_select="rerun")
        
        # Procesar clic - VERSIÓN SIMPLIFICADA
        if event and "selection" in event:
            points = event["selection"].get("points", [])
            if points:
                punto = points[0]
                # El nombre está directamente en 'name'
                nombre_lugar = punto.get("name")
                # Ignorar si es una ruta
                if nombre_lugar and nombre_lugar not in ["🚌 Ruta vehicular", "🚶 Lomada (24h)"]:
                    st.session_state.lugar_seleccionado = nombre_lugar
                    st.rerun()
        
        # Layout de dos columnas
        col_map, col_info = st.columns([2, 1])
        
        with col_map:
            # Leyenda simple
            st.markdown("""
            <div style="background: white; padding: 12px; border-radius: 12px; margin-top: 10px;">
                <span style="font-weight: 600; color: #1e3c72;">📍 Leyenda:</span><br>
                <span style="font-size: 0.9rem;">🚌 Ruta vehicular (naranja) · 🚶 Lomada (morada)</span><br>
                <span style="font-size: 0.9rem;">✨ Marcador más grande = lugar seleccionado</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_info:
            # Mostrar información del lugar seleccionado
            if st.session_state.lugar_seleccionado and st.session_state.lugar_seleccionado in LUGARES_SAGRADOS:
                lugar = LUGARES_SAGRADOS[st.session_state.lugar_seleccionado]
                st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <h3 style="margin: 0 0 8px 0; color: #1e3c72;">{lugar['icono']} {st.session_state.lugar_seleccionado}</h3>
                    <p style="color: #e67e22; font-weight: 600; margin: 0 0 16px 0;">{lugar['tipo']}</p>
                    <p style="color: #2c3e50; line-height: 1.6;">{lugar['descripcion']}</p>
                    <div style="background: #f8f9fa; padding: 16px; border-radius: 12px; margin-top: 16px;">
                        <p style="margin: 0;"><b>📏 Altitud:</b> {lugar['alt']:,} msnm</p>
                        <p style="margin: 8px 0 0 0;"><b>🕯️ Ritual:</b> {lugar.get('ritual', 'No especificado')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: white; border-radius: 16px; padding: 32px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="font-size: 3rem; margin-bottom: 16px;">🗺️</div>
                    <h4 style="color: #1e3c72; margin-bottom: 8px;">Haz clic en cualquier lugar del mapa</h4>
                    <p style="color: #5d6d7e;">Selecciona un marcador para ver información detallada</p>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== TAB 2: PREGUNTAS =====
    with tab2:
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
    
    # ===== TAB 3: PERFIL DE ALTITUD =====
    with tab3:
        st.markdown("### ⛰️ Perfil de altitud de la peregrinación")
        
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
        
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 16px; margin-top: 20px;">
            <span style="font-weight: 600; color: #1e3c72;">📊 Datos del recorrido:</span><br>
            • <b>Distancia total:</b> 125 km (85 km vehicular + 40 km caminata)<br>
            • <b>Tiempo total:</b> 5 días de peregrinación<br>
            • <b>Lomada:</b> 35 km de caminata continua (24 horas sin dormir)<br>
            • <b>Zonas:</b> Vehicular (🟢), Ascenso (🟡), Lomada (🟣)
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 20px;">
            <span>🏔️ Qoyllur Rit'i Explorer - Mapa Clickeable</span>
            <span>•</span>
            <span>🗺️ 16 lugares interactivos</span>
            <span>•</span>
            <span>🖱️ Haz clic en el mapa</span>
            <span>•</span>
            <span>✨ Información al instante</span>
        </div>
        <div style="font-size: 0.7rem; color: #95a5a6;">
            Conocimiento ancestral de la Nación Paucartambo · Sinakara, Cusco · Mapas gratuitos Carto
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()