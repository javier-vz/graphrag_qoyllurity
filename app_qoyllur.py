#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏔️ Qoyllur Rit'i Explorer - VERSIÓN MEJORADA
✅ Extracción completa de datos del TTL
✅ Mapa Folium con marcadores informativos
✅ Popups con toda la información disponible
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
# FUNCIÓN MEJORADA PARA CARGAR LUGARES DEL TTL
# ============================================================================
@st.cache_resource
def cargar_lugares_desde_ttl():
    """
    Extrae lugares del TTL con TODA su información:
    - Coordenadas (geo:lat, geo:long)
    - Nombre (rdfs:label)
    - Descripción (rdfs:comment)
    - Tipo de entidad (rdf:type)
    """
    ttl_path = "qoyllurity.ttl"
    if not Path(ttl_path).exists():
        st.error(f"❌ No se encontró el archivo TTL en: {ttl_path}")
        return {}
    
    g = Graph()
    try:
        g.parse(ttl_path, format='turtle')
    except Exception as e:
        st.error(f"❌ Error al parsear TTL: {e}")
        return {}
    
    lugares = {}
    
    # Iterar sobre todos los sujetos del grafo
    for s in g.subjects():
        lat = None
        lon = None
        nombre = None
        descripcion = None
        tipos = []
        
        # Extraer coordenadas
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
        
        # Solo procesar si tiene coordenadas
        if lat and lon:
            # Extraer nombre (label en español)
            for label in g.objects(s, RDFS.label):
                if isinstance(label, Literal):
                    if label.language == 'es' or not label.language:
                        nombre = str(label)
                        break
            
            # Si no hay label, usar el URI
            if not nombre:
                nombre = str(s).split('#')[-1].replace('_', ' ')
            
            # Extraer descripción (comment en español)
            for comment in g.objects(s, RDFS.comment):
                if isinstance(comment, Literal):
                    if comment.language == 'es' or not comment.language:
                        descripcion = str(comment)
                        break
            
            # Extraer tipos
            for tipo in g.objects(s, RDF.type):
                tipo_str = str(tipo).split('#')[-1]
                if tipo_str not in ['NamedIndividual']:
                    tipos.append(tipo_str)
            
            # Guardar lugar
            lugares[nombre] = {
                "lat": lat,
                "lon": lon,
                "nombre": nombre,
                "descripcion": descripcion or "Sin descripción disponible",
                "tipos": tipos,
                "uri": str(s)
            }
    
    return lugares

# ============================================================================
# FUNCIÓN PARA DETERMINAR COLOR E ICONO
# ============================================================================
def obtener_color_icono(lugar):
    """
    Determina el color e icono según el tipo de lugar
    """
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
# FUNCIÓN PARA CREAR MAPA CON FOLIUM
# ============================================================================
def crear_mapa_folium(lugares):
    """
    Crea un mapa Folium con todos los lugares del TTL
    """
    # Crear mapa centrado en la región
    mapa = folium.Map(
        location=[-13.55, -71.4],
        zoom_start=9,
        control_scale=True,
        tiles='OpenStreetMap'
    )
    
    # Agregar marcadores
    for nombre, lugar in lugares.items():
        color, icono, categoria = obtener_color_icono(lugar)
        
        # Crear popup HTML con información completa
        popup_html = f"""
        <div style="font-family: 'Inter', 'Segoe UI', sans-serif; min-width: 250px; max-width: 350px;">
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2d5aa0 100%); 
                        color: white; 
                        padding: 12px; 
                        margin: -10px -10px 10px -10px;
                        border-radius: 4px 4px 0 0;">
                <h4 style="margin: 0; font-size: 1.1rem;">
                    {icono} {nombre}
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
        
        # Agregar descripción si existe
        if lugar['descripcion'] and lugar['descripcion'] != "Sin descripción disponible":
            popup_html += f"""
                <p style="margin: 12px 0; color: #34495e; font-size: 0.85rem; line-height: 1.6; 
                           border-top: 1px solid #ecf0f1; padding-top: 8px;">
                    <strong>ℹ️ Descripción:</strong><br>
                    {lugar['descripcion']}
                </p>
            """
        
        # Agregar tipos si existen
        if lugar['tipos']:
            tipos_str = ", ".join(lugar['tipos'][:3])  # Máximo 3 tipos
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
            tooltip=f"{icono} {nombre}",
            icon=folium.Icon(color=color, icon='info-sign', prefix='glyphicon')
        ).add_to(mapa)
    
    return mapa

# ============================================================================
# CARGAR MOTOR DE CONOCIMIENTO (SI EXISTE)
# ============================================================================
@st.cache_resource
def cargar_conocimiento():
    """Carga el motor de conocimiento si existe el archivo"""
    try:
        # Importar el módulo
        import sys
        sys.path.insert(0, '/mnt/user-data/uploads')
        from ultralite_qoyllur_v15 import UltraLiteQoyllurV15
        
        # Cargar con la ruta correcta
        ttl_path = "qoyllurity.ttl"
        if not Path(ttl_path).exists():
            st.warning(f"⚠️ No se encontró el archivo TTL en: {ttl_path}")
            return None
        
        return UltraLiteQoyllurV15(ttl_path)
    except ImportError as e:
        st.warning(f"⚠️ No se encontró el módulo ultralite_qoyllur_v15: {e}")
        return None
    except Exception as e:
        st.warning(f"⚠️ Error al cargar motor de conocimiento: {e}")
        return None

# ============================================================================
# FUNCIÓN PARA CREAR PERFIL DE ALTITUD
# ============================================================================
def crear_perfil_altitud():
    """Crea un gráfico de perfil de altitud simplificado"""
    # Datos de ejemplo del recorrido
    puntos = {
        "Paucartambo": 2900,
        "Ccatcca": 3500,
        "Huancarani": 3700,
        "Ocongate": 3800,
        "Mahuayani": 4200,
        "Yanaqancha": 4500,
        "Santuario": 4600,
        "Colque Punku": 5200
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(puntos.keys()),
        y=list(puntos.values()),
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#1e3c72', width=3),
        marker=dict(size=10, color='#e67e22'),
        name='Altitud',
        hovertemplate='<b>%{x}</b><br>Altitud: %{y} msnm<extra></extra>'
    ))
    
    fig.update_layout(
        title="Perfil de Altitud - Ruta Qoyllur Rit'i",
        xaxis_title="Ubicación",
        yaxis_title="Altitud (msnm)",
        hovermode='x unified',
        plot_bgcolor='#fdfaf6',
        height=400,
        font=dict(family="Inter, sans-serif"),
        showlegend=False
    )
    
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
                Conocimiento ancestral · Mapas interactivos · Sinakara, Cusco
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar lugares del TTL
    lugares = cargar_lugares_desde_ttl()
    
    if not lugares:
        st.error("❌ No se pudieron cargar los lugares del archivo TTL")
        st.stop()
    
    st.success(f"✅ Se cargaron **{len(lugares)}** lugares desde el TTL")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏔️ Qoyllur Rit'i")
        st.markdown(f"""
        **Señor de Qoyllur Rit'i**  
        Peregrinación andina anual en Sinakara, Cusco.
        
        **📍 Lugares en mapa:** {len(lugares)} sitios sagrados  
        **📅 Fecha:** 58 días después del Miércoles de Ceniza  
        **⛰️ Altitud máxima:** 5,200 msnm  
        **👥 Participantes:** Ocho naciones
        """)
        
        st.markdown("---")
        st.markdown("""
        ### 🗺️ Características del Mapa
        - **Marcadores de colores** según tipo de lugar
        - **Popups informativos** con descripción completa
        - **Tooltips** al pasar el mouse
        - Información extraída del TTL
        """)
        
        # Leyenda de colores
        st.markdown("### 🎨 Leyenda")
        st.markdown("""
        - 🔴 Santuarios
        - ❄️ Glaciares
        - 🟢 Cruces
        - 🟠 Iglesias/Capillas
        - 🟣 Plazas
        - 🔵 Pueblos
        - 💧 Lagunas
        - 🟤 Descansos
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa Interactivo", "📊 Estadísticas", "❓ Preguntas", "⛰️ Perfil de Altitud"])
    
    # ===== TAB 1: MAPA =====
    with tab1:
        st.markdown(f"### 🗺️ Mapa de lugares sagrados ({len(lugares)} puntos)")
        
        # Crear y mostrar mapa
        with st.spinner("🗺️ Generando mapa interactivo..."):
            mapa = crear_mapa_folium(lugares)
            st_folium(mapa, width="100%", height=600)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Total lugares", len(lugares))
        with col2:
            santuarios = sum(1 for l in lugares.values() if "santuario" in l["nombre"].lower())
            st.metric("⛪ Santuarios", santuarios)
        with col3:
            pueblos = sum(1 for l in lugares.values() if any(p in l["nombre"].lower() for p in ["pueblo", "paucartambo", "ocongate", "ccatcca"]))
            st.metric("🏘️ Pueblos", pueblos)
        with col4:
            st.metric("🏔️ Altitud máx", "5,200 msnm")
    
    # ===== TAB 2: ESTADÍSTICAS =====
    with tab2:
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
    
    # ===== TAB 3: PREGUNTAS =====
    with tab3:
        motor = cargar_conocimiento()
        
        if motor:
            st.markdown("### ❓ Sistema de Preguntas y Respuestas")
            
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
                    respuesta = motor.responder(pregunta)
                    
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
        else:
            st.info("ℹ️ Sistema de preguntas no disponible. Verifica que esté instalado el motor de conocimiento.")
    
    # ===== TAB 4: PERFIL =====
    with tab4:
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
        
        perfil = crear_perfil_altitud()
        st.plotly_chart(perfil, use_container_width=True)
        
        st.info("""
        **ℹ️ Nota:** El perfil de altitud es una representación aproximada basada en los principales puntos del recorrido.
        Las altitudes reales pueden variar según la ruta específica tomada.
        """)

if __name__ == "__main__":
    main()