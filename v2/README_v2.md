# 🚀 GraphRAG v2.0 - Guía Rápida

## 📋 Contenido

- [Instalación](#instalación)
- [Uso Básico](#uso-básico)
- [Evaluación v1.5 vs v2.0](#evaluación)
- [Optimización para Raspberry Pi](#optimización-raspberry-pi)
- [Próximos Pasos](#próximos-pasos)

---

## 🔧 Instalación

### Requisitos Previos
- Python 3.8+
- 2GB RAM mínimo (recomendado 4GB+)
- 500MB espacio en disco

### Instalación en Raspberry Pi 5

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias del sistema
sudo apt install -y python3-pip python3-dev build-essential

# 3. Crear entorno virtual (recomendado)
python3 -m venv venv_graphrag
source venv_graphrag/bin/activate

# 4. Actualizar pip
pip install --upgrade pip

# 5. Instalar dependencias de GraphRAG v2.0
pip install -r requirements_v2.txt

# Nota: La primera instalación descargará ~200MB de modelos
```

### Instalación Rápida (Cualquier Sistema)

```bash
pip install rdflib sentence-transformers scikit-learn numpy
```

---

## 🎮 Uso Básico

### Modo Interactivo

```bash
python graphrag_v2.py
```

Esto iniciará:
1. Carga del grafo TTL
2. Carga del modelo de embeddings (~80MB)
3. Precálculo de embeddings de todas las entidades
4. Modo interactivo de preguntas

### Uso Programático

```python
from graphrag_v2 import GraphRAG_v2

# Inicializar
rag = GraphRAG_v2("qoyllurity.ttl")

# Hacer preguntas
respuesta = rag.responder(
    "¿Qué hacen los ukukus?",
    modo="hibrido",  # 'semantico', 'lexico', o 'hibrido'
    verbose=True     # Muestra debug info
)

print(respuesta)
```

### Modos de Búsqueda

**1. Semántico** (Recomendado para preguntas naturales)
```python
# Entiende sinónimos y paráfrasis
respuesta = rag.responder("¿Cuál es la función de los ukumaris?", modo="semantico")
```

**2. Léxico** (Compatible con v1.5)
```python
# Búsqueda por palabras clave exactas
respuesta = rag.responder("ukukus danza", modo="lexico")
```

**3. Híbrido** (Mejor balance) ⭐
```python
# Combina ambos con pesos ajustables
respuesta = rag.responder("¿Dónde está el santuario?", modo="hibrido")
```

### Guardar y Cargar Caché

```python
# Guardar embeddings para carga rápida
rag.guardar_cache("cache_embeddings.pkl")

# En siguiente ejecución, cargar desde caché
rag2 = GraphRAG_v2("qoyllurity.ttl")
if rag2.cargar_cache("cache_embeddings.pkl"):
    print("✅ Caché cargado - inicio rápido!")
```

---

## 📊 Evaluación

### Ejecutar Suite de Evaluación Completa

```bash
python evaluar_v15_vs_v20.py
```

Esto ejecutará:
- ⏱️ **Test de latencia** (v1.5 vs v2.0 en 3 modos)
- 🎯 **Test de calidad** (precisión de respuestas)
- 🔤 **Test de sinónimos** (capacidad semántica de v2.0)

### Resultados Esperados

| Métrica | v1.5 | v2.0 (híbrido) |
|---------|------|----------------|
| Latencia media | ~80ms | ~250ms |
| RAM uso | ~100MB | ~500MB |
| Precisión | 75-80% | 85-90% |
| Sinónimos | ❌ No | ✅ Sí |

### Benchmark Manual

```python
from graphrag_v2 import GraphRAG_v2, benchmark

rag = GraphRAG_v2("qoyllurity.ttl")

queries = [
    "¿Qué es Qoyllur Rit'i?",
    "¿Dónde está el santuario?",
    "¿Qué hacen los ukukus?",
]

benchmark(rag, queries)
```

---

## 🔧 Optimización para Raspberry Pi

### 1. Reducir Uso de RAM

```python
# Usar modelo más pequeño (inglés only, pero más rápido)
rag = GraphRAG_v2(
    "qoyllurity.ttl",
    model_name="all-MiniLM-L6-v2"  # 80MB vs 120MB
)
```

### 2. Ajustar Batch Size

```python
# En _compute_embeddings(), cambiar:
self.embeddings = self.model.encode(
    self.entity_texts,
    batch_size=16,  # Reducir de 32 a 16 para menos RAM
    show_progress_bar=True
)
```

### 3. Usar Swap si es Necesario

```bash
# Agregar 2GB de swap en RPi
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hacer permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. Compilar PyTorch con Optimizaciones ARM

```bash
# Para máximo rendimiento (opcional, tarda ~2 horas)
pip install torch --no-cache-dir --index-url https://download.pytorch.org/whl/cpu
```

---

## 🎯 Comparación Rápida: ¿Cuándo usar qué?

### Usar v1.5 si:
- ✅ Necesitas latencia <100ms
- ✅ RAM muy limitada (<512MB disponible)
- ✅ Consultas con términos exactos
- ✅ Sistema embebido simple

### Usar v2.0 si:
- ✅ Preguntas en lenguaje natural
- ✅ Usuarios escriben con sinónimos/paráfrasis
- ✅ 200-300ms de latencia es aceptable
- ✅ Tienes >1GB RAM disponible
- ✅ Necesitas mejor calidad de respuestas

### Modo Recomendado v2.0
```python
# Usar modo híbrido con alpha=0.7
respuesta = rag.responder(query, modo="hibrido")
# 70% peso semántico + 30% léxico = mejor balance
```

---

## 📈 Próximos Pasos

### Cuando v2.0 funcione bien y necesites MÁS:

**→ v4.0 - LLM Small + RAG Completo**
- Genera respuestas en lenguaje natural
- Query decomposition
- Razonamiento básico multi-hop
- Modelo: Phi-3-mini-4k (2.3GB)
- RAM: ~3GB
- Latencia: ~2s

### Migración a v4.0

1. Asegurar que v2.0 funciona bien
2. Medir que la calidad justifica esperar 2s
3. Instalar llama-cpp-python
4. Descargar modelo Phi-3-mini-4k
5. Integrar generación de lenguaje natural

---

## 🐛 Troubleshooting

### Error: "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### Error: "Killed" durante compute_embeddings
- **Causa**: RAM insuficiente
- **Solución**: Agregar swap o reducir batch_size

### Latencia muy alta (>1s)
- **Causa**: Modelo muy grande o CPU lenta
- **Solución**: Usar modelo más pequeño: `all-MiniLM-L6-v2`

### Embeddings no se guardan en caché
```python
# Verificar permisos
import os
print(os.access('.', os.W_OK))  # Debe ser True
```

---

## 📚 Referencias

- Modelo embeddings: [sentence-transformers](https://www.sbert.net/)
- Modelos multilingües: [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- Roadmap completo: Ver `ROADMAP_GraphRAG_RPi5.md`

---

## 💡 Tips y Trucos

### 1. Primera ejecución lenta
Es normal. El modelo se descarga una vez (~120MB).

### 2. Ajustar peso híbrido
```python
# Más peso a semántico (mejor para lenguaje natural)
resultados = rag.buscar_hibrido(query, alpha=0.8)

# Más peso a léxico (mejor para términos técnicos)
resultados = rag.buscar_hibrido(query, alpha=0.5)
```

### 3. Ver top-K resultados
```python
# Ver las 10 entidades más relevantes
results = rag.buscar_semantico("ukukus", top_k=10)
for ent_id, score in results:
    ent = rag.entidades[ent_id]
    print(f"{ent['labels'][0]}: {score:.3f}")
```

### 4. Búsqueda solo sin respuesta
```python
# Solo recuperar entidades, sin generar respuesta
results = rag.buscar_hibrido("lomada", top_k=5)
```

---

## 🎓 Arquitectura v2.0

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Embedding Generation       │
│  (SentenceTransformer)      │
└────────┬────────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ┌────────┐    ┌─────────┐   ┌──────────┐
    │Semantic│    │ Lexical │   │ Hybrid   │
    │ Search │    │ Search  │   │ (α=0.7)  │
    └────┬───┘    └────┬────┘   └────┬─────┘
         │             │              │
         └─────────────┴──────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │  Top-K Entities  │
            └─────────┬────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Intent Detection │
            │  (Rule-based)    │
            └─────────┬────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Template         │
            │ Selection        │
            └─────────┬────────┘
                      │
                      ▼
            ┌──────────────────┐
            │  Final Response  │
            └──────────────────┘
```

---

**¿Preguntas? ¿Problemas? ¡Pregunta! 🚀**
