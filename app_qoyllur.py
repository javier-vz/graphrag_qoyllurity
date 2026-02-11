#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏔️ Qoyllur Rit'i Explorer - VERSIÓN MEJORADA CON RUTA ORDENADA
✅ Extracción completa de datos del TTL
✅ Mapa Folium con marcadores informativos
✅ Ruta cronológica ordenada por marcos temporales y eventos
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from pathlib import Path
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDFS, RDF
import pandas as pd
import plotly.graph_objects as go
import sys

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
st.set_page_config(page_title="Qoyllur Rit'i", page_icon="🏔️", layout="wide")

# Namespaces
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
FESTIVIDAD = Namespace("http://example.org/festividades#")

# ============================================================================
# CSS
# ============================================================================
st.markdown("""
<style>
    .main { background: #fdfaf6; }
    h1 { color: #1e3c72; }
    .stButton button { 
        background: #1e3c72; 
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton button:hover {
        background: #2d5aa0;
    }
    .respuesta-box {
        background: white;
        border-left: 6px solid #e67e22;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .info-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PREGUNTAS FRECUENTES
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
# FUNCIÓN PARA CARGAR DATOS COMPLETOS DEL TTL
# ============================================================================
@st.cache_resource
def cargar_datos_ttl():
    """
    Extrae:
    1. Lugares con coordenadas
    2. Eventos ordenados por marco temporal y orden de evento
    3. Relaciones entre eventos y lugares
    """
    ttl_path = "qoyllurity.ttl"
    if not Path(ttl_path).exists():
        st.error(f"❌ No se encontró el archivo TTL en: {ttl_path}")
        return {}, [], {}
    
    g = Graph()
    try:
        g.parse(ttl_path, format='turtle')
    except Exception as e:
        st.error(f"❌ Error al parsear TTL: {e}")
        return {}, [], {}
    
    lugares = {}
    eventos = []
    marcos_temporales = {}
    
    # ===== PASO 1: Extraer lugares con coordenadas =====
    for s in g.subjects():
        lat = None
        lon = None
        nombre = None
        descripcion = None
        tipos = []
        
        # Coordenadas
        for lat_val in g.objects(s, GEO.lat):
            try:
                lat = float(lat_val)
            except:
                pass
        
        for lon_val in g.objects(s, GEO.long):
            try:
                lon = float(lon_val)
            except:
                pass
        
        if lat and lon:
            # Nombre
            for label in g.objects(s, RDFS.label):
                if isinstance(label, Literal):
                    if label.language == 'es' or not label.language:
                        nombre = str(label)
                        break
            
            if not nombre:
                nombre = str(s).split('#')[-1].replace('_', ' ')
            
            # Descripción
            for comment in g.objects(s, RDFS.comment):
                if isinstance(comment, Literal):
                    if comment.language == 'es' or not comment.language:
                        descripcion = str(comment)
                        break
            
            # Tipos
            for tipo in g.objects(s, RDF.type):
                tipo_str = str(tipo).split('#')[-1]
                if tipo_str not in ['NamedIndividual']:
                    tipos.append(tipo_str)
            
            uri = str(s).split('#')[-1] if '#' in str(s) else str(s)
            
            lugares[uri] = {
                "uri": uri,
                "lat": lat,
                "lon": lon,
                "nombre": nombre,
                "descripcion": descripcion or "Sin descripción disponible",
                "tipos": tipos
            }
    
    # ===== PASO 2: Extraer marcos temporales (días) =====
    for s, p, o in g.triples((None, FESTIVIDAD.defineMarcoTemporal, None)):
        marco_uri = str(s).split('#')[-1] if '#' in str(s) else str(s)
        
        # Obtener orden del marco
        orden = None
        for orden_val in g.objects(s, FESTIVIDAD.tieneOrden):
            try:
                orden = int(orden_val)
            except:
                pass
        
        # Obtener nombre del marco
        nombre_marco = None
        for label in g.objects(s, RDFS.label):
            if isinstance(label, Literal):
                nombre_marco = str(label)
                break
        
        if not nombre_marco:
            nombre_marco = marco_uri
        
        if marco_uri not in marcos_temporales:
            marcos_temporales[marco_uri] = {
                "uri": marco_uri,
                "nombre": nombre_marco,
                "orden": orden or 999,
                "eventos": []
            }
    
    # ===== PASO 3: Extraer eventos y asociarlos a marcos temporales =====
    for s in g.subjects(RDF.type, FESTIVIDAD.EventoRitual):
        evento_uri = str(s).split('#')[-1] if '#' in str(s) else str(s)
        
        # Nombre del evento
        nombre_evento = None
        for label in g.objects(s, RDFS.label):
            if isinstance(label, Literal):
                nombre_evento = str(label)
                break
        
        if not nombre_evento:
            nombre_evento = evento_uri
        
        # Descripción
        descripcion_evento = None
        for comment in g.objects(s, RDFS.comment):
            if isinstance(comment, Literal):
                descripcion_evento = str(comment)
                break
        
        # Orden del evento
        orden_evento = None
        for orden_val in g.objects(s, FESTIVIDAD.tieneOrdenEvento):
            try:
                orden_evento = int(orden_val)
            except:
                pass
        
        # Lugar donde ocurre
        lugares_evento = []
        for lugar_obj in g.objects(s, FESTIVIDAD.ocurreEnLugar):
            lugar_uri = str(lugar_obj).split('#')[-1] if '#' in str(lugar_obj) else str(lugar_obj)
            if lugar_uri in lugares:
                lugares_evento.append(lugar_uri)
        
        # Marco temporal al que pertenece
        marco_del_evento = None
        for marco_s in g.subjects(FESTIVIDAD.defineMarcoTemporal, s):
            marco_del_evento = str(marco_s).split('#')[-1] if '#' in str(marco_s) else str(marco_s)
            break
        
        evento_data = {
            "uri": evento_uri,
            "nombre": nombre_evento,
            "descripcion": descripcion_evento or "Sin descripción",
            "orden_evento": orden_evento or 999,
            "lugares": lugares_evento,
            "marco": marco_del_evento
        }
        
        eventos.append(evento_data)
        
        # Agregar a su marco temporal
        if marco_del_evento and marco_del_evento in marcos_temporales:
            marcos_temporales[marco_del_evento]["eventos"].append(evento_data)
    
    # ===== PASO 4: Ordenar eventos por marco temporal y orden de evento =====
    # Ordenar marcos temporales por orden
    marcos_ordenados = sorted(marcos_temporales.values(), key=lambda x: x["orden"])
    
    # Ordenar eventos dentro de cada marco
    for marco in marcos_ordenados:
        marco["eventos"].sort(key=lambda x: x["orden_evento"])
    
    # Crear lista plana de eventos ordenados
    eventos_ordenados = []
    for marco in marcos_ordenados:
        for evento in marco["eventos"]:
            eventos_ordenados.append(evento)
    
    return lugares, eventos_ordenados, marcos_temporales

# ============================================================================
# FUNCIÓN PARA DETERMINAR COLOR E ICONO
# ============================================================================
def obtener_color_icono(lugar):
    """Determina el color e icono según el tipo de lugar"""
    nombre = lugar["nombre"].lower()
    tipos = [t.lower() for t in lugar["tipos"]]
    
    # Definir categorías
    if "santuario" in nombre or any("santuario" in t for t in tipos):
        return "red", "⛪", "Santuario"
    elif "colque" in nombre or "glaciar" in nombre or any("glaciar" in t for t in tipos):
        return "lightblue", "❄️", "Glaciar"
    elif "cruz" in nombre or any("cruz" in t for t in tipos):
        return "green", "✝️", "Cruz"
    elif "iglesia" in nombre or "capilla" in nombre:
        return "orange", "⛪", "Iglesia/Capilla"
    elif "plaza" in nombre:
        return "purple", "🎭", "Plaza"
    elif "cementerio" in nombre:
        return "gray", "🕊️", "Cementerio"
    elif "laguna" in nombre or "yanaqocha" in nombre:
        return "cadetblue", "💧", "Laguna"
    elif "yanaqancha" in nombre or "descanso" in nombre.lower():
        return "darkpurple", "😴", "Punto de descanso"
    elif "mahuayani" in nombre or "inicio" in nombre:
        return "darkgreen", "🚩", "Punto de inicio"
    elif "gruta" in nombre:
        return "darkred", "🕯️", "Gruta"
    elif "pueblo" in nombre or "paucartambo" in nombre or "ocongate" in nombre or "ccatcca" in nombre or "huancarani" in nombre:
        return "blue", "🏘️", "Pueblo"
    else:
        return "gray", "📍", "Lugar"

# ============================================================================
# FUNCIÓN PARA CREAR MAPA CON FOLIUM Y RUTA ORDENADA
# ============================================================================
def crear_mapa_folium(lugares, eventos_ordenados, mostrar_ruta=True):
    """
    Crea un mapa Folium con:
    1. Marcadores de lugares
    2. Ruta cronológica según eventos ordenados
    """
    # Crear mapa centrado en la región
    mapa = folium.Map(
        location=[-13.55, -71.4],
        zoom_start=9,
        control_scale=True,
        tiles='OpenStreetMap'
    )
    
    # ===== PASO 1: Agregar marcadores de todos los lugares =====
    for nombre_key, lugar in lugares.items():
        color, icono, categoria = obtener_color_icono(lugar)
        
        # Crear popup HTML
        popup_html = f"""
        <div style="font-family: 'Inter', 'Segoe UI', sans-serif; min-width: 250px; max-width: 350px;">
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2d5aa0 100%); 
                        color: white; 
                        padding: 12px; 
                        margin: -10px -10px 10px -10px;
                        border-radius: 4px 4px 0 0;">
                <h4 style="margin: 0; font-size: 1.1rem;">
                    {icono} {lugar['nombre']}
                </h4>
                <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 4px;">
                    {categoria}
                </div>
            </div>
            
            <div style="padding: 8px 0;">
                <p style="margin: 8px 0; color: #2c3e50; font-size: 0.9rem; line-height: 1.5;">
                    <strong>📍 Coordenadas:</strong><br>
                    Lat: {lugar['lat']:.5f}<br>
                    Lon: {lugar['lon']:.5f}
                </p>
        """
        
        if lugar['descripcion'] and lugar['descripcion'] != "Sin descripción disponible":
            popup_html += f"""
                <p style="margin: 12px 0; color: #34495e; font-size: 0.85rem; line-height: 1.6; 
                           border-top: 1px solid #ecf0f1; padding-top: 8px;">
                    <strong>ℹ️ Descripción:</strong><br>
                    {lugar['descripcion']}
                </p>
            """
        
        if lugar['tipos']:
            tipos_str = ", ".join(lugar['tipos'][:3])
            popup_html += f"""
                <p style="margin: 8px 0; color: #7f8c8d; font-size: 0.75rem;">
                    <strong>🏷️ Tipo:</strong> {tipos_str}
                </p>
            """
        
        popup_html += """
            </div>
        </div>
        """
        
        # Crear marcador
        folium.Marker(
            location=[lugar["lat"], lugar["lon"]],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"{icono} {lugar['nombre']}",
            icon=folium.Icon(color=color, icon='info-sign', prefix='glyphicon')
        ).add_to(mapa)
    
    # ===== PASO 2: Agregar ruta cronológica =====
    if mostrar_ruta and eventos_ordenados:
        ruta_coords = []
        eventos_con_coords = []
        
        for i, evento in enumerate(eventos_ordenados):
            if evento["lugares"]:
                # Usar el primer lugar del evento
                lugar_uri = evento["lugares"][0]
                if lugar_uri in lugares:
                    lugar = lugares[lugar_uri]
                    coord = [lugar["lat"], lugar["lon"]]
                    
                    # Evitar duplicados consecutivos
                    if not ruta_coords or ruta_coords[-1] != coord:
                        ruta_coords.append(coord)
                        eventos_con_coords.append({
                            "evento": evento,
                            "lugar": lugar,
                            "orden": i + 1
                        })
        
        # Dibujar línea de ruta
        if len(ruta_coords) > 1:
            folium.PolyLine(
                ruta_coords,
                color='#e67e22',
                weight=3,
                opacity=0.7,
                tooltip="Ruta cronológica de la peregrinación"
            ).add_to(mapa)
            
            # Agregar marcadores numerados en la ruta
            for i, item in enumerate(eventos_con_coords):
                evento = item["evento"]
                lugar = item["lugar"]
                orden = item["orden"]
                
                # Marcador numerado
                folium.CircleMarker(
                    location=[lugar["lat"], lugar["lon"]],
                    radius=8,
                    color='#e67e22',
                    fill=True,
                    fillColor='#fff',
                    fillOpacity=1,
                    weight=2,
                    tooltip=f"#{orden}: {evento['nombre']}"
                ).add_to(mapa)
                
                # Número dentro del círculo
                folium.Marker(
                    location=[lugar["lat"], lugar["lon"]],
                    icon=folium.DivIcon(html=f'''
                        <div style="
                            font-size: 10px;
                            font-weight: bold;
                            color: #e67e22;
                            text-align: center;
                            margin-top: -20px;
                            margin-left: -3px;
                        ">{orden}</div>
                    ''')
                ).add_to(mapa)
    
    return mapa

# ============================================================================
# CARGAR MOTOR DE CONOCIMIENTO
# ============================================================================
@st.cache_resource
def cargar_conocimiento():
    """Carga el motor GraphRAG v2.0 con embeddings semánticos"""
    try:
        # Importar GraphRAG v2.0
        sys.path.insert(0, 'outputs')
        from graphrag_v2 import GraphRAG_v2
        
        # Cargar con la ruta correcta
        ttl_path = "qoyllurity.ttl"
        if not Path(ttl_path).exists():
            st.warning(f"⚠️ No se encontró el archivo TTL en: {ttl_path}")
            return None
        
        with st.spinner("🔄 Cargando GraphRAG v2.0 (embeddings + búsqueda semántica)..."):
            motor = GraphRAG_v2(ttl_path)
        
        st.success("✅ GraphRAG v2.0 cargado - Búsqueda semántica activa")
        return motor
        
    except ImportError as e:
        st.warning(f"⚠️ No se encontró graphrag_v2. Intentando con v1.5...")
        # Fallback a v1.5
        try:
            sys.path.insert(0, 'uploads')
            from ultralite_qoyllur_v15 import UltraLiteQoyllurV15
            ttl_path = "qoyllurity.ttl"
            return UltraLiteQoyllurV15(ttl_path)
        except:
            st.error("❌ No se pudo cargar ningún motor de conocimiento")
            return None
            
    except Exception as e:
        st.warning(f"⚠️ Error al cargar GraphRAG v2.0: {e}")
        return None

# ============================================================================
# FUNCIÓN PARA CREAR PERFIL DE ALTITUD
# ============================================================================
def crear_perfil_altitud(lugares, eventos_ordenados):
    """
    Crea un gráfico de perfil de altitud basado en la cronología real de eventos
    Usa altitudes estimadas basadas en las coordenadas reales
    """
    # Altitudes conocidas aproximadas para algunos lugares clave
    altitudes_conocidas = {
        "Paucartambo": 2900,
        "PlazaPaucartambo": 2900,
        "CementerioPaucartambo": 2900,
        "IglesiaPaucartambo": 2900,
        "Huancarani": 3700,
        "Ccatcca": 3500,
        "PlazaCcatcca": 3500,
        "IglesiaCcatcca": 3500,
        "Ocongate": 3800,
        "CasaPriosteOcongate": 3800,
        "Mahuayani": 4200,
        "SantuarioQoylluriti": 4600,
        "CeldaUkukusPaucartambo": 4600,
        "ColquePunku": 5200,
        "Yanaqancha": 4500,
        "GrutaYanaqancha": 4500,
        "Yanaqocha": 4550,
        "MachuCruz": 4400,
        "QespiCruz": 4300,
        "Escalerachayoq": 4200,
        "IntiAlabado_2025": 3900,
        "Tayancani": 3800,
        "GrutaTayankani": 3850,
        "CapillaTayankani": 3800
    }
    
    # Construir perfil desde eventos ordenados
    perfil_puntos = []
    nombres_puntos = []
    eventos_info = []
    distancia_acumulada = [0]
    
    coord_anterior = None
    
    for i, evento in enumerate(eventos_ordenados):
        if evento["lugares"]:
            lugar_uri = evento["lugares"][0]
            if lugar_uri in lugares:
                lugar = lugares[lugar_uri]
                
                # Obtener altitud (conocida o estimada)
                if lugar_uri in altitudes_conocidas:
                    altitud = altitudes_conocidas[lugar_uri]
                else:
                    # Estimación simple basada en latitud (más al sur = más alto generalmente)
                    # Esto es una aproximación muy simplificada
                    lat = lugar["lat"]
                    if lat < -13.6:  # Zona baja (Paucartambo, Ocongate)
                        altitud = 3000
                    elif lat < -13.58:  # Zona media-baja
                        altitud = 3500
                    elif lat < -13.56:  # Zona media
                        altitud = 4000
                    elif lat < -13.54:  # Zona media-alta
                        altitud = 4500
                    else:  # Zona alta (cerca del glaciar)
                        altitud = 5000
                
                # Evitar duplicados consecutivos
                if not perfil_puntos or perfil_puntos[-1] != altitud or nombres_puntos[-1] != lugar["nombre"]:
                    perfil_puntos.append(altitud)
                    nombres_puntos.append(lugar["nombre"])
                    eventos_info.append({
                        "evento": evento["nombre"],
                        "orden": i + 1,
                        "lugar": lugar["nombre"]
                    })
                    
                    # Calcular distancia aproximada (en km)
                    if coord_anterior:
                        lat1, lon1 = coord_anterior
                        lat2, lon2 = lugar["lat"], lugar["lon"]
                        # Fórmula simple de distancia (aproximada)
                        dist = ((lat2-lat1)**2 + (lon2-lon1)**2)**0.5 * 111  # ~111 km por grado
                        distancia_acumulada.append(distancia_acumulada[-1] + dist)
                    
                    coord_anterior = (lugar["lat"], lugar["lon"])
    
    if len(perfil_puntos) < 2:
        # Fallback a datos de ejemplo si no hay suficientes datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay suficientes datos de eventos para generar el perfil",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(height=400)
        return fig
    
    # Crear gráfico
    fig = go.Figure()
    
    # Línea principal del perfil
    fig.add_trace(go.Scatter(
        x=list(range(len(perfil_puntos))),
        y=perfil_puntos,
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#1e3c72', width=3),
        marker=dict(
            size=8, 
            color=perfil_puntos,
            colorscale='Viridis',
            showscale=False,
            line=dict(color='#e67e22', width=2)
        ),
        name='Altitud',
        text=[f"<b>{nombres_puntos[i]}</b><br>Evento #{eventos_info[i]['orden']}: {eventos_info[i]['evento']}<br>{perfil_puntos[i]} msnm" 
              for i in range(len(perfil_puntos))],
        hovertemplate='%{text}<extra></extra>',
        customdata=nombres_puntos
    ))
    
    # Marcar puntos importantes
    # Punto más alto
    idx_max = perfil_puntos.index(max(perfil_puntos))
    fig.add_annotation(
        x=idx_max, y=perfil_puntos[idx_max],
        text=f"⛰️ Punto más alto<br>{perfil_puntos[idx_max]} msnm",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#e67e22",
        ax=0, ay=-40,
        bgcolor="rgba(230, 126, 34, 0.8)",
        font=dict(color="white", size=10)
    )
    
    # Punto más bajo
    idx_min = perfil_puntos.index(min(perfil_puntos))
    fig.add_annotation(
        x=idx_min, y=perfil_puntos[idx_min],
        text=f"🏘️ Punto más bajo<br>{perfil_puntos[idx_min]} msnm",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#3498db",
        ax=0, ay=40,
        bgcolor="rgba(52, 152, 219, 0.8)",
        font=dict(color="white", size=10)
    )
    
    fig.update_layout(
        title={
            'text': "Perfil de Altitud - Orden Cronológico de la Peregrinación",
            'font': {'size': 16, 'color': '#1e3c72'}
        },
        xaxis_title="Secuencia de eventos",
        yaxis_title="Altitud (msnm)",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(nombres_puntos))),
            ticktext=[f"{i+1}" for i in range(len(nombres_puntos))],
            tickangle=-45
        ),
        hovermode='closest',
        plot_bgcolor='#fdfaf6',
        height=500,
        font=dict(family="Inter, sans-serif"),
        showlegend=False,
        margin=dict(b=100)
    )
    
    # Añadir líneas de referencia
    fig.add_hline(y=4000, line_dash="dash", line_color="gray", opacity=0.3,
                  annotation_text="4000 msnm", annotation_position="right")
    fig.add_hline(y=5000, line_dash="dash", line_color="gray", opacity=0.3,
                  annotation_text="5000 msnm", annotation_position="right")
    
    return fig

# ============================================================================
# APP PRINCIPAL
# ============================================================================
def main():
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
        <div style="font-size: 4rem;">🏔️</div>
        <div>
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; color: #1e3c72;">
                Qoyllur Rit'i Explorer
            </h1>
            <p style="margin: 0; color: #7f8c8d; font-size: 1.2rem;">
                Conocimiento ancestral · Ruta cronológica · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos del TTL
    lugares, eventos_ordenados, marcos_temporales = cargar_datos_ttl()
    
    if not lugares:
        st.error("❌ No se pudieron cargar los datos del archivo TTL")
        st.stop()
    
    st.success(f"✅ Cargados **{len(lugares)}** lugares y **{len(eventos_ordenados)}** eventos ordenados")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown(f"""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📍 Lugares:** {len(lugares)} sitios  
        **📅 Eventos:** {len(eventos_ordenados)} eventos ordenados  
        **🗓️ Días:** {len(marcos_temporales)} marcos temporales  
        **⛰️ Altitud máx:** 5,200 msnm  
        """)
        
        st.markdown("---")
        st.markdown("### 🤖 Sistema de IA")
        
        # Detectar qué versión está cargada
        motor_test = cargar_conocimiento()
        if motor_test:
            version = "v2.0 🚀" if "GraphRAG_v2" in str(type(motor_test)) else "v1.5"
            capacidades = "Semántico + Léxico" if "v2.0" in version else "Solo Léxico"
            st.markdown(f"""
            **GraphRAG {version}**  
            🔍 Búsqueda: {capacidades}  
            📊 Precisión: {'85-100%' if 'v2.0' in version else '50-75%'}  
            ⚡ Latencia: {'~40ms' if 'v2.0' in version else '<1ms'}
            """)
        
        st.markdown("---")
        st.markdown("### 🗺️ Ruta Cronológica")
        mostrar_ruta = st.checkbox("Mostrar ruta ordenada", value=True)
        st.markdown("""
        La ruta sigue el orden cronológico de los eventos según:
        1. **Marco temporal** (días)
        2. **Orden de evento** (dentro de cada día)
        """)
        
        st.markdown("---")
        st.markdown("### 🎨 Leyenda")
        st.markdown("""
        - 🔴 Santuarios
        - ❄️ Glaciares
        - 🟢 Cruces
        - 🟠 Iglesias
        - 🔵 Pueblos
        - 💧 Lagunas
        - 🟣 Plazas
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Mapa Interactivo", 
        "📅 Cronología de Eventos",
        "📊 Estadísticas", 
        "❓ Preguntas", 
        "⛰️ Perfil"
    ])
    
    # ===== TAB 1: MAPA =====
    with tab1:
        st.markdown(f"### 🗺️ Mapa de la peregrinación ({len(lugares)} lugares)")
        
        # Crear y mostrar mapa
        with st.spinner("🗺️ Generando mapa con ruta cronológica..."):
            mapa = crear_mapa_folium(lugares, eventos_ordenados, mostrar_ruta)
            st_folium(mapa, width="100%", height=600)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Lugares", len(lugares))
        with col2:
            st.metric("📅 Eventos", len(eventos_ordenados))
        with col3:
            st.metric("🗓️ Marcos", len(marcos_temporales))
        with col4:
            st.metric("🏔️ Altitud máx", "5,200 msnm")
    
    # ===== TAB 2: CRONOLOGÍA =====
    with tab2:
        st.markdown("### 📅 Cronología de Eventos")
        
        # Ordenar marcos temporales
        marcos_ordenados = sorted(marcos_temporales.values(), key=lambda x: x["orden"])
        
        for marco in marcos_ordenados:
            with st.expander(f"**{marco['nombre']}** (Día {marco['orden']})", expanded=True):
                if marco["eventos"]:
                    for evento in sorted(marco["eventos"], key=lambda x: x["orden_evento"]):
                        st.markdown(f"""
                        <div class="info-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <div style="color: #e67e22; font-weight: bold; font-size: 0.9rem;">
                                        #{evento['orden_evento']} - {evento['nombre']}
                                    </div>
                                    <div style="color: #7f8c8d; font-size: 0.85rem; margin-top: 8px;">
                                        {evento['descripcion']}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar lugares del evento
                        if evento["lugares"]:
                            lugares_nombres = []
                            for lugar_uri in evento["lugares"]:
                                if lugar_uri in lugares:
                                    lugares_nombres.append(f"📍 {lugares[lugar_uri]['nombre']}")
                            if lugares_nombres:
                                st.markdown(f"**Lugares:** {', '.join(lugares_nombres)}")
                        
                        st.markdown("---")
                else:
                    st.info("Sin eventos registrados para este marco temporal")
    
    # ===== TAB 3: ESTADÍSTICAS =====
    with tab3:
        st.markdown("### 📊 Estadísticas de Lugares")
        
        # Crear DataFrame
        df_lugares = pd.DataFrame([
            {
                "Nombre": l["nombre"],
                "Latitud": l["lat"],
                "Longitud": l["lon"],
                "Categoría": obtener_color_icono(l)[2],
                "Descripción": l["descripcion"][:100] + "..." if len(l["descripcion"]) > 100 else l["descripcion"]
            }
            for l in lugares.values()
        ])
        
        # Mostrar tabla
        st.dataframe(
            df_lugares,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nombre": st.column_config.TextColumn("🏔️ Nombre", width="medium"),
                "Latitud": st.column_config.NumberColumn("📍 Lat", format="%.5f"),
                "Longitud": st.column_config.NumberColumn("📍 Lon", format="%.5f"),
                "Categoría": st.column_config.TextColumn("🏷️ Categoría", width="small"),
                "Descripción": st.column_config.TextColumn("ℹ️ Descripción", width="large")
            }
        )
        
        # Distribución por categoría
        st.markdown("### 📈 Distribución por Categoría")
        categorias = {}
        for lugar in lugares.values():
            cat = obtener_color_icono(lugar)[2]
            categorias[cat] = categorias.get(cat, 0) + 1
        
        fig_cat = go.Figure(data=[
            go.Bar(
                x=list(categorias.keys()),
                y=list(categorias.values()),
                marker_color='#1e3c72'
            )
        ])
        fig_cat.update_layout(
            title="Lugares por Categoría",
            xaxis_title="Categoría",
            yaxis_title="Cantidad",
            plot_bgcolor='#fdfaf6',
            height=400
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    # ===== TAB 4: PREGUNTAS =====
    with tab4:
        motor = cargar_conocimiento()
        
        if motor:
            st.markdown("### ❓ Sistema de Preguntas y Respuestas")
            
            # Selector de modo de pregunta
            col1, col2 = st.columns([1, 1])
            with col1:
                modo_pregunta = st.radio(
                    "Selecciona cómo hacer tu pregunta:",
                    ["📋 Elegir de la lista", "✍️ Escribir mi propia pregunta"],
                    horizontal=True
                )
            
            pregunta = ""
            
            if modo_pregunta == "📋 Elegir de la lista":
                # Modo selector
                col1, col2 = st.columns([3, 1])
                with col1:
                    pregunta = st.selectbox(
                        "🔍 Selecciona una pregunta:",
                        options=[""] + TOP_10_PREGUNTAS,
                        format_func=lambda x: "🎯 Elige una pregunta..." if x == "" else x,
                        key="select_pregunta"
                    )
                with col2:
                    st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
                    responder = st.button("✨ Consultar", use_container_width=True, key="btn_select")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Modo texto libre
                col1, col2 = st.columns([3, 1])
                with col1:
                    pregunta = st.text_input(
                        "✍️ Escribe tu pregunta:",
                        placeholder="Ejemplo: ¿Cuántos días dura la peregrinación?",
                        key="input_pregunta"
                    )
                with col2:
                    st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
                    responder = st.button("✨ Consultar", use_container_width=True, key="btn_input")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Mostrar ejemplos de preguntas
                with st.expander("💡 Ver ejemplos de preguntas que puedes hacer"):
                    st.markdown("""
                    **Preguntas sobre ubicación:**
                    - ¿Dónde queda el santuario de Qoyllur Rit'i?
                    - ¿En qué lugar se hace la misa de ukukus?
                    - ¿Dónde está ubicado el glaciar Colque Punku?
                    
                    **Preguntas sobre eventos:**
                    - ¿Qué eventos ocurren el día 3?
                    - ¿Cuándo es la bajada del glaciar?
                    - ¿Qué hacen en la lomada?
                    
                    **Preguntas sobre participantes:**
                    - ¿Quién realiza la lomada?
                    - ¿Qué hacen los ukukus?
                    - ¿Quiénes participan en la peregrinación?
                    
                    **Preguntas generales:**
                    - ¿Qué es Qoyllur Rit'i?
                    - ¿Qué es la danza del ukumari?
                    - ¿Cuántas naciones participan?
                    """)
            
            if responder and pregunta:
                with st.spinner("🔍 Buscando con GraphRAG v2.0 (semántico + léxico)..."):
                    # Usar modo híbrido de v2.0 (mejor precisión)
                    respuesta = motor.responder(pregunta, modo="hibrido", verbose=False)
                    
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
            elif responder and not pregunta:
                st.warning("⚠️ Por favor escribe o selecciona una pregunta primero.")
                
        else:
            st.info("ℹ️ Sistema de preguntas no disponible. Verifica que esté instalado el motor de conocimiento.")
    
    # ===== TAB 5: PERFIL =====
    with tab5:
        st.markdown("### ⛰️ Perfil de Altitud del Recorrido")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Partida", "Paucartambo", "2,900 msnm")
        with col2:
            st.metric("❄️ Punto más alto", "Colque Punku", "5,200 msnm")
        with col3:
            st.metric("📈 Desnivel", "+2,300 m")
        with col4:
            st.metric("🎯 Llegada", "Tayankani", "3,800 msnm")
        
        perfil = crear_perfil_altitud(lugares, eventos_ordenados)
        st.plotly_chart(perfil, use_container_width=True)
        
        st.info("""
        **ℹ️ Nota:** El perfil de altitud sigue el orden cronológico de los eventos extraídos del TTL.
        Las altitudes se basan en datos conocidos de los lugares principales y estimaciones para otros puntos.
        Cada punto en el gráfico representa un evento en la secuencia de la peregrinación.
        """)
        
        # Mostrar tabla de eventos con altitudes
        with st.expander("📋 Ver detalle de eventos y altitudes"):
            eventos_tabla = []
            for i, evento in enumerate(eventos_ordenados):
                if evento["lugares"]:
                    lugar_uri = evento["lugares"][0]
                    if lugar_uri in lugares:
                        lugar = lugares[lugar_uri]
                        eventos_tabla.append({
                            "Orden": i + 1,
                            "Evento": evento["nombre"],
                            "Lugar": lugar["nombre"],
                            "Marco": evento.get("marco", "N/A")
                        })
            
            if eventos_tabla:
                df_eventos = pd.DataFrame(eventos_tabla)
                st.dataframe(df_eventos, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
