#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug rápido de las queries problemáticas
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from graphrag_v2 import GraphRAG_v2

# Cargar sistema
ttl_path = "qoyllurity.ttl"
if not Path(ttl_path).exists():
    ttl_path = input("Ruta al TTL: ").strip()

print("Cargando sistema...")
rag = GraphRAG_v2(ttl_path)

# Query problemática 1
print("\n" + "="*80)
print("🔬 Query: ¿Quién realiza la lomada?")
print("="*80)

results = rag.buscar_hibrido("¿Quién realiza la lomada?", top_k=10)
print("\nTop-10 resultados:")
for i, (ent_id, score) in enumerate(results, 1):
    ent = rag.entidades[ent_id]
    nombre = ent['labels'][0] if ent['labels'] else ent_id
    tipo = ent.get('type', 'N/A')
    print(f"{i:2d}. {nombre:60s} | {score:.3f} | {tipo}")

# Buscar "Lomada" específicamente
print("\n🔍 Buscando entidades con 'Lomada' en el nombre:")
for ent_id, ent in rag.entidades.items():
    for label in ent.get('labels', []):
        if 'lomada' in label.lower():
            print(f"   • {label} ({ent_id})")
            
            # Ver quién lo realiza
            realiza = ent['relaciones'].get('realizadoPor', [])
            if realiza:
                for r_id in realiza:
                    r_ent = rag.entidades.get(r_id, {})
                    r_nombre = r_ent['labels'][0] if r_ent['labels'] else r_id
                    print(f"      → Realizado por: {r_nombre}")

# Query problemática 2
print("\n" + "="*80)
print("🔬 Query: ¿Qué eventos hay el día 2?")
print("="*80)

results = rag.buscar_hibrido("¿Qué eventos hay el día 2?", top_k=10)
print("\nTop-10 resultados:")
for i, (ent_id, score) in enumerate(results, 1):
    ent = rag.entidades[ent_id]
    nombre = ent['labels'][0] if ent['labels'] else ent_id
    tipo = ent.get('type', 'N/A')
    print(f"{i:2d}. {nombre:60s} | {score:.3f} | {tipo}")

# Buscar "Día 2" específicamente
print("\n🔍 Buscando entidades con 'Dia2' o 'Día 2':")
for ent_id, ent in rag.entidades.items():
    if 'dia2' in ent_id.lower() or any('día 2' in l.lower() for l in ent.get('labels', [])):
        label = ent['labels'][0] if ent['labels'] else ent_id
        print(f"   • {label} ({ent_id})")
        
        # Ver eventos que define
        eventos = ent['relaciones'].get('defineMarcoTemporal', [])
        if eventos:
            print(f"      → Define {len(eventos)} eventos:")
            for e_id in eventos[:5]:
                e_ent = rag.entidades.get(e_id, {})
                e_nombre = e_ent['labels'][0] if e_ent['labels'] else e_id
                orden = e_ent['propiedades'].get('tieneOrdenEvento', '?')
                print(f"         {orden}. {e_nombre}")

print("\n" + "="*80)
