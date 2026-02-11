#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UltraLite GraphRAG para Qoyllur Riti
"""

import sys
import re
from pathlib import Path
from collections import defaultdict
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

class UltraLiteQoyllurV15:
    """Versión mejorada con stemming y plantillas"""
    
    def __init__(self, ttl_path):
        print("🚀 Cargando Qoyllur Riti - Fase 1.5...")
        self.g = Graph()
        try:
            self.g.parse(ttl_path, format='turtle')
            print(f"✅ Grafo: {len(self.g)} tripletas")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        
        # Índices
        self.index_palabras = defaultdict(list)  # palabra -> [entidades]
        self.index_propiedades = defaultdict(list)  # propiedad+valor -> [entidades]
        self.entidades = {}
        
        # Stemming manual (reglas simples)
        self.stem_rules = [
            (r'es$', ''),    # ukumaris → ukumari
            (r's$', ''),     # danzantes → danzante
            (r'ón$', 'on'),  # procesión → procesion
            (r'í$', 'i'),    # ukukú → ukuku
        ]
        
        self._build_index()
        print(f"📚 Índice: {len(self.index_palabras)} términos")
        print("✅ Sistema listo.\n")
    
    def _stem(self, word):
        """Stemming básico en español"""
        word = word.lower()
        for pattern, replacement in self.stem_rules:
            word = re.sub(pattern, replacement, word)
        return word
    
    def _normalize(self, text):
        """Normalización mejorada con stemming"""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)
        replacements = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ü':'u', 'ñ':'n'}
        for a, b in replacements.items():
            text = text.replace(a, b)
        words = text.split()
        # Aplicar stemming a cada palabra
        words = [self._stem(w) for w in words if len(w) > 2]
        return ' '.join(words)
    
    def _index_text(self, text, entidad_id):
        """Indexa texto con stemming"""
        palabras = set(self._normalize(text).split())
        for palabra in palabras:
            if len(palabra) > 2:
                self.index_palabras[palabra].append(entidad_id)
    
    def _build_index(self):
        """Construye índices completos"""
        for s, p, o in self.g:
            sujeto_uri = str(s)
            sujeto_id = sujeto_uri.split('#')[-1] if '#' in sujeto_uri else sujeto_uri
            
            # Inicializar entidad
            if sujeto_id not in self.entidades:
                self.entidades[sujeto_id] = {
                    'uri': sujeto_uri,
                    'labels': [],
                    'descriptions': [],
                    'comments': [],
                    'type': None,
                    'propiedades': {},
                    'relaciones': defaultdict(list),  # predicado -> [objetos]
                    'relaciones_inversas': defaultdict(list)  # predicado -> [sujetos]
                }
            
            ent = self.entidades[sujeto_id]
            
            # --- PROPIEDADES ANOTACIÓN (texto) ---
            if p == RDFS.label and isinstance(o, Literal) and o.language == 'es':
                texto = str(o)
                ent['labels'].append(texto)
                self._index_text(texto, sujeto_id)
            
            elif str(p).endswith('tieneDescripcion') and isinstance(o, Literal) and o.language == 'es':
                texto = str(o)
                ent['descriptions'].append(texto)
                self._index_text(texto, sujeto_id)
            
            elif p == RDFS.comment and isinstance(o, Literal) and o.language == 'es':
                texto = str(o)
                ent['comments'].append(texto)
                self._index_text(texto, sujeto_id)
            
            # --- TIPO ---
            elif str(p).endswith('type'):
                tipo = str(o).split('#')[-1] if '#' in str(o) else str(o)
                ent['type'] = tipo
            
            # --- PROPIEDADES DATATYPE (fechas, órdenes) ---
            else:
                prop = str(p).split('#')[-1] if '#' in str(p) else str(p)
                if isinstance(o, Literal):
                    valor = str(o)
                    ent['propiedades'][prop] = valor
                    # Indexar propiedades importantes
                    if prop in ['tieneOrden', 'tieneOrdenEvento', 'tieneFecha']:
                        clave_index = f"{prop}:{valor}"
                        self.index_propiedades[clave_index].append(sujeto_id)
                        # También indexar el valor como texto
                        self._index_text(valor, sujeto_id)
                else:
                    # Es una relación con otra entidad
                    obj_id = str(o).split('#')[-1] if '#' in str(o) else str(o)
                    ent['relaciones'][prop].append(obj_id)
                    # Indexar la relación para búsqueda inversa
                    clave_rel = f"{prop}:{obj_id}"
                    self.index_propiedades[clave_rel].append(sujeto_id)
                    
                    # También indexar el nombre del objeto
                    if obj_id:
                        self._index_text(obj_id, sujeto_id)
        
        # Construir relaciones inversas (segunda pasada)
        for ent_id, ent_data in self.entidades.items():
            for prop, objetos in ent_data['relaciones'].items():
                for obj_id in objetos:
                    if obj_id in self.entidades:
                        self.entidades[obj_id]['relaciones_inversas'][prop].append(ent_id)
    
    def buscar_entidades(self, query, top_k=10):
        """Búsqueda por palabras clave con stemming"""
        palabras = self._normalize(query).split()
        if not palabras:
            return []
        
        scores = defaultdict(int)
        for palabra in palabras:
            if palabra in self.index_palabras:
                for ent_id in self.index_palabras[palabra]:
                    scores[ent_id] += 1
        
        # Bonus por coincidencia exacta en labels
        for ent_id, ent in self.entidades.items():
            for label in ent['labels']:
                if query.lower() in label.lower():
                    scores[ent_id] += 3
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def buscar_por_propiedad(self, prop, valor):
        """Búsqueda específica por propiedad:valor"""
        clave = f"{prop}:{valor}"
        return self.index_propiedades.get(clave, [])
    
    def identificar_intencion(self, pregunta):
        """Detecta qué tipo de pregunta es"""
        p = pregunta.lower()
        
        # Palabras clave para cada tipo
        if any(w in p for w in ['dónde', 'donde', 'lugar', 'ubicación', 'sitio']):
            return 'donde'
        elif any(w in p for w in ['cuándo', 'cuando', 'fecha', 'día', 'hora']):
            return 'cuando'
        elif any(w in p for w in ['quién', 'quien', 'quiénes', 'quienes', 'participa']):
            return 'quien'
        elif any(w in p for w in ['qué', 'que', 'cómo', 'como', 'cuál', 'cual']):
            if 'evento' in p or 'actividad' in p or 'hito' in p:
                return 'que_eventos'
            elif 'danza' in p or 'baile' in p:
                return 'que_danzas'
            else:
                return 'que'
        elif 'cuántos' in p or 'cuantos' in p or 'número' in p or 'cantidad' in p:
            return 'cuantos'
        else:
            return 'general'
    
    def responder_donde(self, pregunta, entidad_principal):
        """Plantilla para preguntas de ubicación"""
        ent = self.entidades.get(entidad_principal, {})
        if not ent:
            return None
        
        nombre = ent['labels'][0] if ent['labels'] else entidad_principal
        
        # Buscar ocurreEnLugar
        lugares = ent['relaciones'].get('ocurreEnLugar', [])
        if lugares:
            lugar_ids = lugares[:3]
            lugares_nombres = []
            for lid in lugar_ids:
                lent = self.entidades.get(lid, {})
                lname = lent['labels'][0] if lent['labels'] else lid
                lugares_nombres.append(lname)
            
            if len(lugares_nombres) == 1:
                return f"📍 **{nombre}** ocurre en **{lugares_nombres[0]}**."
            else:
                return f"📍 **{nombre}** ocurre en: {', '.join(lugares_nombres)}."
        
        # Buscar estaEn (para lugares)
        esta_en = ent['relaciones'].get('estaEn', [])
        if esta_en:
            lugar = esta_en[0]
            lent = self.entidades.get(lugar, {})
            lname = lent['labels'][0] if lent['labels'] else lugar
            return f"📍 **{nombre}** está ubicado en **{lname}**."
        
        return None
    
    def responder_cuando(self, pregunta, entidad_principal):
        """Plantilla para preguntas de fecha/hora"""
        ent = self.entidades.get(entidad_principal, {})
        if not ent:
            return None
        
        nombre = ent['labels'][0] if ent['labels'] else entidad_principal
        props = ent['propiedades']
        
        fecha = props.get('tieneFecha')
        orden = props.get('tieneOrden')
        orden_evento = props.get('tieneOrdenEvento')
        
        respuestas = []
        if fecha:
            respuestas.append(f"📅 **{nombre}** ocurre el {fecha}.")
        if orden:
            respuestas.append(f"📋 Es el día {orden} de la festividad.")
        if orden_evento:
            respuestas.append(f"🔢 Es el evento #{orden_evento} en su día.")
        
        return ' '.join(respuestas) if respuestas else None
    
    def responder_que_eventos(self, pregunta, entidad_principal=None):
        """¿Qué eventos hay en X día?"""
        # Buscar por "día 2", "dia2", etc.
        dias = {
            '1': 'Dia1_SabadoPreparacion',
            '2': 'Dia2_DomingoPartida',
            '3': 'Dia3_LunesAscenso',
            '4': 'NocheLunesMartes_Glaciar',
            '5': 'Dia4_MartesDescensoYLomada',
            '6': 'NocheMartesMiercoles_Lomada',
            '7': 'Dia5_MiercolesAlba'
        }
        
        dia_num = None
        p = pregunta.lower()
        for num, dia_id in dias.items():
            if f'día {num}' in p or f'dia {num}' in p or f'dia{num}' in p:
                dia_num = num
                dia_ent = dia_id
                break
        
        if dia_num:
            # Buscar eventos que tienen este marco como defineMarcoTemporal
            eventos = []
            for ent_id, ent in self.entidades.items():
                # Es un evento? (tipo EventoRitual)
                if ent.get('type') == 'EventoRitual':
                    # Tiene relación defineMarcoTemporal inversa?
                    for sup_id in ent.get('relaciones_inversas', {}).get('defineMarcoTemporal', []):
                        if sup_id == dia_ent:
                            eventos.append(ent_id)
            
            if eventos:
                nombres = []
                for ev_id in eventos[:10]:
                    ev_ent = self.entidades.get(ev_id, {})
                    ev_name = ev_ent['labels'][0] if ev_ent['labels'] else ev_id
                    orden = ev_ent['propiedades'].get('tieneOrdenEvento', '')
                    if orden:
                        ev_name = f"{ev_name} (orden {orden})"
                    nombres.append(ev_name)
                
                dia_nombre = self.entidades[dia_ent]['labels'][0] if dia_ent in self.entidades else f"Día {dia_num}"
                return f"📅 **Eventos del {dia_nombre}**:\n• " + "\n• ".join(nombres)
        
        return None
    
    def responder_quien(self, pregunta, entidad_principal):
        """¿Quién realiza X evento?"""
        ent = self.entidades.get(entidad_principal, {})
        if not ent:
            return None
        
        nombre = ent['labels'][0] if ent['labels'] else entidad_principal
        
        # Buscar realizadoPor
        realizadores = ent['relaciones'].get('realizadoPor', [])
        if realizadores:
            parts = []
            for pid in realizadores:
                pent = self.entidades.get(pid, {})
                pname = pent['labels'][0] if pent['labels'] else pid
                parts.append(pname)
            
            if len(parts) == 1:
                return f"👥 **{nombre}** es realizado por **{parts[0]}**."
            else:
                return f"👥 **{nombre}** es realizado por: {', '.join(parts)}."
        
        # Buscar participaEn inverso
        participantes = ent.get('relaciones_inversas', {}).get('participaEn', [])
        if participantes:
            parts = []
            for pid in participantes[:3]:
                pent = self.entidades.get(pid, {})
                pname = pent['labels'][0] if pent['labels'] else pid
                parts.append(pname)
            
            return f"👥 **{nombre}** tiene la participación de: {', '.join(parts)}."
        
        return None
    
    def responder(self, pregunta):
        """Punto de entrada principal con detección de intención"""
        # 1. Buscar entidades relevantes
        resultados = self.buscar_entidades(pregunta, top_k=5)
        
        if not resultados:
            return "Lo siento, no encontré información relacionada con tu pregunta."
        
        mejor_id, score = resultados[0]
        
        # 2. Identificar tipo de pregunta
        intencion = self.identificar_intencion(pregunta)
        
        # 3. Responder según plantilla
        respuesta = None
        if intencion == 'donde':
            respuesta = self.responder_donde(pregunta, mejor_id)
        elif intencion == 'cuando':
            respuesta = self.responder_cuando(pregunta, mejor_id)
        elif intencion == 'quien':
            respuesta = self.responder_quien(pregunta, mejor_id)
        elif intencion == 'que_eventos':
            respuesta = self.responder_que_eventos(pregunta, mejor_id)
        
        # 4. Si hay respuesta de plantilla, usarla
        if respuesta:
            return respuesta
        
        # 5. Fallback: respuesta genérica con contexto
        ent = self.entidades.get(mejor_id, {})
        nombre = ent['labels'][0] if ent['labels'] else mejor_id
        
        lines = [f"**{nombre}**"]
        
        if ent['descriptions']:
            lines.append(f"\n{ent['descriptions'][0]}")
        elif ent['comments']:
            lines.append(f"\n{ent['comments'][0]}")
        
        # Añadir algunas propiedades clave
        props = []
        if 'tieneFecha' in ent['propiedades']:
            props.append(f"Fecha: {ent['propiedades']['tieneFecha']}")
        if 'tieneOrden' in ent['propiedades']:
            props.append(f"Orden día: {ent['propiedades']['tieneOrden']}")
        if 'tieneOrdenEvento' in ent['propiedades']:
            props.append(f"Orden evento: {ent['propiedades']['tieneOrdenEvento']}")
        
        if props:
            lines.append("\n" + "\n".join(props))
        
        # Mencionar otras entidades relevantes
        if len(resultados) > 1:
            otros = []
            for eid, s in resultados[1:3]:
                e = self.entidades.get(eid, {})
                ename = e['labels'][0] if e['labels'] else eid
                otros.append(f"**{ename}**")
            if otros:
                lines.append(f"\n\nTambién relacionado: {', '.join(otros)}")
        
        return "\n".join(lines)


def main():
    print("=" * 60)
    print("🤖 QOYLLUR RIT'I - FASE 1.5 (Stemming + Plantillas)")
    print("=" * 60)
    
    ttl_file = "qoyllurity.ttl"
    if not Path(ttl_file).exists():
        alt = input(f"Ruta TTL: ").strip()
        ttl_file = alt if alt else ttl_file
    
    rag = UltraLiteQoyllurV15(ttl_file)
    
    print("\n💡 Ejemplos:")
    print("  • ¿Dónde ocurre la misa de ukukus?")
    print("  • ¿Cuándo es la bajada del glaciar?")
    print("  • ¿Qué eventos hay el día 2?")
    print("  • ¿Quién realiza la lomada?")
    print("  • 'salir' para terminar\n")
    
    while True:
        try:
            q = input("❓ ").strip()
            if not q:
                continue
            if q.lower() in ['salir', 'exit', 'quit']:
                break
            
            r = rag.responder(q)
            print(f"\n📢 {r}\n")
            print("-" * 60)
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()