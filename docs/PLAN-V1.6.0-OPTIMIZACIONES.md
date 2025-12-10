# Plan de Implementación v1.6.0 - Optimizaciones

**Fecha:** 2025-12-10
**Rama:** feature/smart-navigation-v2
**Estado:** En progreso

---

## Resumen de Cambios

| # | Mejora | Impacto | Complejidad |
|---|--------|---------|-------------|
| 1 | Reducir default `get_law_index` 100→20 | -79% tokens | Trivial |
| 2 | Limpiar campos redundantes `get_boe_summary_section` | -18% tokens | Bajo |
| 3 | Nueva herramienta `check_law_modifications` | Funcionalidad nueva | Medio |
| 4 | Instrucciones MCP (Fase 1) | UX/Guía LLM | Bajo |
| 5 | Resource MCP (Fase 2) - Opcional | Documentación on-demand | Bajo |

---

## Paso 1: Reducir Default `get_law_index`

### Ubicación
`src/boe_mcp/server.py`, línea ~1458

### Cambio
```python
# Antes
limit: int = 100

# Después
limit: int = 20
```

### Justificación
- Respuesta típica: 18KB → 4KB (-79%)
- 20 elementos es suficiente para navegación inicial
- Usuario puede paginar con `offset` si necesita más

### Test
```bash
# Verificar que funciona con limit=20 por defecto
uv run pytest tests/ -k "law_index" -v
```

---

## Paso 2: Limpiar Campos Redundantes `get_boe_summary_section`

### Ubicación
`src/boe_mcp/server.py`, líneas ~2031-2051

### Campos a Eliminar

| Campo | Razón | Ahorro |
|-------|-------|--------|
| `url_pdf` | Derivable: `https://www.boe.es/boe/dias/YYYY/MM/DD/pdfs/{id}.pdf` | ~8% |
| `url_html` | Derivable: `https://www.boe.es/diario_boe/txt.php?id={id}` | ~7% |
| `departamento_codigo` | Redundante con `departamento` (nombre legible) | ~3% |

### Cambio
```python
# Antes
docs.append({
    "identificador": item.get("identificador", ""),
    "titulo": item.get("titulo", ""),
    "departamento": item.get("departamento", ""),
    "departamento_codigo": item.get("departamento_codigo", ""),
    "rango": item.get("rango", ""),
    "url_pdf": item.get("url_pdf", ""),
    "url_html": item.get("url_html", ""),
})

# Después
docs.append({
    "identificador": item.get("identificador", ""),
    "titulo": item.get("titulo", ""),
    "departamento": item.get("departamento", ""),
    "rango": item.get("rango", ""),
})
```

### Test
```bash
uv run pytest tests/ -k "boe_summary_section" -v
```

---

## Paso 3: Implementar `check_law_modifications`

### Diseño

**Propósito:** Listar TODOS los artículos modificados de una ley con 1 sola llamada API.

**Firma:**
```python
@mcp.tool()
async def check_law_modifications(identifier: str) -> dict:
    """
    Verificar qué artículos de una ley han sido modificados.

    Usa el índice de la ley para detectar modificaciones comparando
    fecha_actualizacion vs fecha original de la norma.

    Args:
        identifier: ID de la ley (ej: "BOE-A-2015-10565")

    Returns:
        {
            "ley_id": "BOE-A-2015-10565",
            "titulo": "Ley 39/2015...",
            "fecha_original": "20151002",
            "total_articulos": 133,
            "articulos_modificados": 10,
            "modificados": [
                {"articulo": "28", "titulo": "Documentos...", "fecha_actualizacion": "20181206"},
                ...
            ]
        }
    """
```

### Lógica Interna
```python
# 1. Obtener índice completo
indice = await get_law_index(identifier, limit=500)  # Cubrir leyes largas

# 2. Obtener fecha original de metadatos
metadatos = await get_law_section(identifier, "metadatos")
fecha_original = extraer_fecha_publicacion(metadatos)

# 3. Filtrar artículos modificados
modificados = []
for item in indice["items"]:
    if item["tipo"] == "articulo":
        if item.get("fecha_actualizacion", fecha_original) > fecha_original:
            modificados.append({
                "articulo": item["numero"],
                "titulo": item["titulo"],
                "fecha_actualizacion": item["fecha_actualizacion"]
            })

return {
    "ley_id": identifier,
    "fecha_original": fecha_original,
    "total_articulos": contar_articulos(indice),
    "articulos_modificados": len(modificados),
    "modificados": modificados
}
```

### Ventajas
- 1 llamada API vs N llamadas (una por artículo)
- Ley 39/2015: 1 llamada vs 133 llamadas
- Respuesta compacta: ~500 bytes típico

### Test
```python
def test_check_law_modifications_ley_39_2015():
    result = check_law_modifications("BOE-A-2015-10565")
    assert result["articulos_modificados"] >= 10  # Conocemos al menos 10
    assert "28" in [m["articulo"] for m in result["modificados"]]
```

---

## Paso 4: Instrucciones MCP (Fase 1)

### Ubicación
`src/boe_mcp/server.py`, línea ~30

### Contenido de Instructions
```python
mcp = FastMCP(
    name="boe-mcp",
    instructions="""
BOE-MCP: Servidor para consultar el Boletín Oficial del Estado español.

## DECISIÓN RÁPIDA DE HERRAMIENTAS

### Sumarios BOE (publicaciones diarias)
| Necesito... | Herramienta |
|-------------|-------------|
| Vista general del día | get_boe_summary_metadata |
| Documentos de una sección | get_boe_summary_section |
| Detalles de un documento | get_boe_document_info |
| ⚠️ NO usar get_boe_summary | Devuelve 300KB+ |

### Legislación Consolidada (leyes vigentes)
| Necesito... | Herramienta |
|-------------|-------------|
| Buscar leyes | search_laws_list |
| Estructura de una ley | get_law_structure_summary |
| Índice paginado | get_law_index |
| Texto de artículo | get_article_info |
| ¿Fue modificado un artículo? | get_article_modifications |
| ¿Qué artículos fueron modificados? | check_law_modifications |
| Buscar texto en una ley | search_in_law |

### Flujos Recomendados

**Explorar BOE del día:**
1. get_boe_summary_metadata(fecha) → ver secciones
2. get_boe_summary_section(fecha, seccion) → listar docs
3. get_boe_document_info(id) → detalles

**Investigar una ley:**
1. search_laws_list(query) → encontrar ID
2. get_law_structure_summary(id) → ver estructura
3. get_article_info(id, articulo) → leer artículo

**Auditar modificaciones:**
1. check_law_modifications(id) → ver todos los modificados
2. get_article_modifications(id, art) → detalles de uno
"""
)
```

---

## Paso 5: Resource MCP (Fase 2) - Opcional

### Implementación
```python
@mcp.resource("guide://herramientas")
def get_usage_guide() -> str:
    """Guía completa de uso de herramientas BOE-MCP"""
    guide_path = Path(__file__).parent.parent.parent / "docs" / "GUIA-USO-HERRAMIENTAS.md"
    return guide_path.read_text()
```

### Ventajas
- Guía completa disponible bajo demanda
- No consume contexto siempre
- El LLM puede consultarla cuando necesite más detalle

### Consideración
Depende de si el cliente MCP soporta resources. Claude Desktop sí lo soporta.

---

## Orden de Implementación

```
[ ] Paso 1: Reducir default get_law_index (5 min)
    └── Cambiar línea 1458
    └── Ejecutar tests

[ ] Paso 2: Limpiar campos get_boe_summary_section (10 min)
    └── Eliminar 3 campos
    └── Actualizar tests si es necesario

[ ] Paso 3: Implementar check_law_modifications (30 min)
    └── Crear función
    └── Añadir tests
    └── Documentar

[ ] Paso 4: Añadir instructions (15 min)
    └── Actualizar constructor FastMCP
    └── Verificar que se muestra en cliente

[ ] Paso 5 (Opcional): Añadir resource (10 min)
    └── Crear decorator @mcp.resource
    └── Probar en Claude Desktop

[ ] Actualizar documentación
    └── GUIA-USO-HERRAMIENTAS.md
    └── CATALOGO-HERRAMIENTAS-BOE-MCP.md
    └── pyproject.toml (versión)

[ ] Commit y tag v1.6.0
```

---

## Métricas de Éxito

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| `get_law_index` default | 18KB | 4KB | -79% |
| `get_boe_summary_section` | 6KB | 5KB | -17% |
| Detectar mods de 133 arts | 133 llamadas | 1 llamada | -99% |
| Instructions disponibles | No | Sí | ✓ |

---

## Notas

- Los cambios son retrocompatibles (reducir defaults no rompe nada)
- Las instrucciones usan ~800 caracteres (dentro del límite recomendado)
- El resource es opcional pero recomendado para Claude Desktop
