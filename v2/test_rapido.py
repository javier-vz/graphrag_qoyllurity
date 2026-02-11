#!/usr/bin/env python3
"""Prueba rápida de las queries problemáticas"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from graphrag_v2 import GraphRAG_v2

# Cargar
ttl_path = "qoyllurity.ttl"
if not Path(ttl_path).exists():
    ttl_path = input("Ruta TTL: ").strip()

print("\n🔄 Cargando GraphRAG v2.0 mejorado...")
rag = GraphRAG_v2(ttl_path)

# Test 1
print("\n" + "="*80)
print("TEST 1: ¿Quién realiza la lomada?")
print("="*80)

results = rag.buscar_hibrido("¿Quién realiza la lomada?", top_k=10)
print("\n📊 Top-10 Híbrido (con boost mejorado):")
for i, (ent_id, score) in enumerate(results, 1):
    ent = rag.entidades[ent_id]
    nombre = ent['labels'][0] if ent['labels'] else ent_id
    tipo = ent.get('type', 'N/A')
    
    # Marcar si es la entidad esperada
    marca = "🎯" if "lomada" in ent_id.lower() and "2025" in ent_id else "  "
    print(f"{marca} {i:2d}. {nombre:50s} | {score:.3f} | {tipo}")

print("\n💬 Respuesta generada:")
resp = rag.responder("¿Quién realiza la lomada?", modo="hibrido", verbose=False)
print(resp)

# Verificar
lomada_en_top5 = any("lomada_2025" in ent_id.lower() for ent_id, _ in results[:5])
print(f"\n{'✅' if lomada_en_top5 else '❌'} Lomada_2025 en top-5: {lomada_en_top5}")

# Test 2
print("\n" + "="*80)
print("TEST 2: ¿Qué eventos hay el día 2?")
print("="*80)

results = rag.buscar_hibrido("¿Qué eventos hay el día 2?", top_k=10)
print("\n📊 Top-10 Híbrido (con boost mejorado):")
for i, (ent_id, score) in enumerate(results, 1):
    ent = rag.entidades[ent_id]
    nombre = ent['labels'][0] if ent['labels'] else ent_id
    tipo = ent.get('type', 'N/A')
    
    # Marcar si es la entidad esperada
    marca = "🎯" if "dia2" in ent_id.lower() else "  "
    print(f"{marca} {i:2d}. {nombre:50s} | {score:.3f} | {tipo}")

print("\n💬 Respuesta generada:")
resp = rag.responder("¿Qué eventos hay el día 2?", modo="hibrido", verbose=False)
print(resp)

# Verificar
dia2_en_top5 = any("dia2" in ent_id.lower() for ent_id, _ in results[:5])
print(f"\n{'✅' if dia2_en_top5 else '❌'} Dia2 en top-5: {dia2_en_top5}")

print("\n" + "="*80)
print("🎯 RESUMEN")
print("="*80)
print(f"Lomada_2025 en top-5: {'✅ SÍ' if lomada_en_top5 else '❌ NO'}")
print(f"Dia2 en top-5: {'✅ SÍ' if dia2_en_top5 else '❌ NO'}")
print(f"\nPrecisión esperada: {'✅ 100%' if lomada_en_top5 and dia2_en_top5 else '⚠️ 75%'}")
print("="*80)
