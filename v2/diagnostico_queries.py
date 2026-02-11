#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico de Queries - Analiza por qué fallan ciertas preguntas
"""

import sys
from pathlib import Path

# Importar GraphRAG v2.0
sys.path.insert(0, str(Path(__file__).parent))
from graphrag_v2 import GraphRAG_v2


def diagnosticar_query(rag: GraphRAG_v2, query: str):
    """Analiza en detalle qué encuentra el sistema para una query"""
    
    print("\n" + "=" * 80)
    print(f"🔬 DIAGNÓSTICO: {query}")
    print("=" * 80)
    
    # 1. Búsqueda semántica
    print("\n📊 Top-10 Búsqueda Semántica:")
    results_sem = rag.buscar_semantico(query, top_k=10)
    for i, (ent_id, score) in enumerate(results_sem, 1):
        ent = rag.entidades[ent_id]
        nombre = ent['labels'][0] if ent['labels'] else ent_id
        tipo = ent.get('type', 'N/A')
        print(f"   {i:2d}. {nombre:50s} | Score: {score:.3f} | Tipo: {tipo}")
    
    # 2. Búsqueda léxica
    print("\n📚 Top-10 Búsqueda Léxica:")
    results_lex = rag.buscar_lexico(query, top_k=10)
    for i, (ent_id, score) in enumerate(results_lex, 1):
        ent = rag.entidades[ent_id]
        nombre = ent['labels'][0] if ent['labels'] else ent_id
        tipo = ent.get('type', 'N/A')
        print(f"   {i:2d}. {nombre:50s} | Score: {score:.3f} | Tipo: {tipo}")
    
    # 3. Búsqueda híbrida
    print("\n🔀 Top-10 Búsqueda Híbrida (α=0.7):")
    results_hyb = rag.buscar_hibrido(query, top_k=10, alpha=0.7)
    for i, (ent_id, score) in enumerate(results_hyb, 1):
        ent = rag.entidades[ent_id]
        nombre = ent['labels'][0] if ent['labels'] else ent_id
        tipo = ent.get('type', 'N/A')
        print(f"   {i:2d}. {nombre:50s} | Score: {score:.3f} | Tipo: {tipo}")
    
    # 4. Intención detectada
    intencion = rag.identificar_intencion(query)
    print(f"\n🎯 Intención detectada: {intencion}")
    
    # 5. Entidad principal elegida
    mejor_id, mejor_score = results_hyb[0]
    mejor_ent = rag.entidades[mejor_id]
    
    print(f"\n🏆 Entidad Principal Seleccionada:")
    print(f"   ID: {mejor_id}")
    print(f"   Nombre: {mejor_ent['labels'][0] if mejor_ent['labels'] else 'N/A'}")
    print(f"   Tipo: {mejor_ent.get('type', 'N/A')}")
    print(f"   Score: {mejor_score:.3f}")
    
    # 6. Detalles de la entidad
    print(f"\n📋 Detalles de la Entidad:")
    if mejor_ent.get('comments'):
        print(f"   Descripción: {mejor_ent['comments'][0][:100]}...")
    
    print(f"\n   Propiedades:")
    for prop, val in mejor_ent.get('propiedades', {}).items():
        print(f"      • {prop}: {val}")
    
    print(f"\n   Relaciones (primeras 5):")
    for rel, objetos in list(mejor_ent.get('relaciones', {}).items())[:5]:
        objs_nombres = []
        for obj_id in objetos[:3]:
            if obj_id in rag.entidades:
                obj_ent = rag.entidades[obj_id]
                objs_nombres.append(obj_ent['labels'][0] if obj_ent['labels'] else obj_id)
        print(f"      • {rel}: {', '.join(objs_nombres)}")
    
    print(f"\n   Relaciones Inversas (primeras 5):")
    for rel, sujetos in list(mejor_ent.get('relaciones_inversas', {}).items())[:5]:
        subj_nombres = []
        for subj_id in sujetos[:3]:
            if subj_id in rag.entidades:
                subj_ent = rag.entidades[subj_id]
                subj_nombres.append(subj_ent['labels'][0] if subj_ent['labels'] else subj_id)
        print(f"      • {rel}: {', '.join(subj_nombres)}")
    
    # 7. Respuesta generada
    print(f"\n💬 Respuesta Generada:")
    respuesta = rag.responder(query, modo="hibrido", verbose=False)
    print(f"   {respuesta}")
    
    print("\n" + "=" * 80)


def diagnosticar_problemas_comunes(rag: GraphRAG_v2):
    """Diagnostica las queries que suelen fallar"""
    
    queries_problema = [
        ("¿Quién realiza la lomada?", "Nacion Paucartambo"),
        ("¿Qué eventos hay el día 2?", "Dia2_DomingoPartida"),
        ("¿Dónde está el santuario?", "SantuarioQoylluriti"),
        ("¿Qué hacen los ukukus?", "Ukumari"),
    ]
    
    for query, entidad_esperada in queries_problema:
        diagnosticar_query(rag, query)
        
        # Verificar si la entidad esperada está en los resultados
        results = rag.buscar_hibrido(query, top_k=10)
        encontrado = any(ent_id == entidad_esperada or 
                        entidad_esperada.lower() in ent_id.lower() 
                        for ent_id, _ in results)
        
        if encontrado:
            print(f"✅ Entidad esperada '{entidad_esperada}' SÍ está en top-10")
        else:
            print(f"❌ Entidad esperada '{entidad_esperada}' NO está en top-10")
            print(f"   → Necesita ajuste en embeddings o mejor query")


def buscar_entidad(rag: GraphRAG_v2, nombre_parcial: str):
    """Busca entidades que contengan un texto en su nombre"""
    print(f"\n🔍 Buscando entidades con '{nombre_parcial}':")
    
    encontradas = []
    for ent_id, ent in rag.entidades.items():
        for label in ent.get('labels', []):
            if nombre_parcial.lower() in label.lower():
                encontradas.append((ent_id, label, ent.get('type', 'N/A')))
    
    if encontradas:
        for i, (ent_id, label, tipo) in enumerate(encontradas, 1):
            print(f"   {i}. {label} ({ent_id}) - Tipo: {tipo}")
    else:
        print(f"   ❌ No se encontraron entidades con '{nombre_parcial}'")


def main():
    """Main interactivo"""
    
    # Configuración
    ttl_path = "qoyllurity.ttl"
    
    if not Path(ttl_path).exists():
        rutas = [
            "/mnt/user-data/uploads/qoyllurity.ttl",
            "../qoyllurity.ttl",
        ]
        for ruta in rutas:
            if Path(ruta).exists():
                ttl_path = ruta
                break
        else:
            ttl_path = input("Ruta al archivo TTL: ").strip()
    
    # Cargar sistema
    print("Cargando GraphRAG v2.0...")
    rag = GraphRAG_v2(ttl_path)
    
    print("\n" + "=" * 80)
    print("🔬 HERRAMIENTA DE DIAGNÓSTICO")
    print("=" * 80)
    print("\nComandos:")
    print("  1. Escribe una pregunta para diagnosticarla")
    print("  2. 'buscar <texto>' - Busca entidades por nombre")
    print("  3. 'problemas' - Diagnostica queries problemáticas conocidas")
    print("  4. 'salir' - Terminar")
    print("=" * 80 + "\n")
    
    while True:
        try:
            comando = input("🔬 > ").strip()
            
            if not comando:
                continue
            
            if comando.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Adiós!")
                break
            
            if comando.lower() == 'problemas':
                diagnosticar_problemas_comunes(rag)
                continue
            
            if comando.lower().startswith('buscar '):
                texto = comando[7:]
                buscar_entidad(rag, texto)
                continue
            
            # Diagnosticar la query
            diagnosticar_query(rag, comando)
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Adiós!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
