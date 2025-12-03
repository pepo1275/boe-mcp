# Guía de Uso de Herramientas BOE-MCP

**Versión:** v1.5.0
**Fecha:** 2025-12-03
**Propósito:** Documento de referencia para selección de herramientas según caso de uso.

---

## Resumen de Herramientas

### Herramientas de Legislación Consolidada

| Herramienta | Propósito | Cuándo usar |
|-------------|-----------|-------------|
| `search_laws_list` | Buscar normas | Encontrar leyes por texto, fecha, rango |
| `get_law_section` | Obtener partes de ley | Acceder a metadatos, texto, bloques |
| `get_law_structure_summary` | Estructura de ley | Ver índice compacto de una norma |
| `get_law_index` | Índice paginado | Navegar estructura con paginación |
| `get_article_info` | Info de artículo | Detalles de artículo específico |
| `search_in_law` | Buscar en ley | Encontrar texto dentro de una norma |

### Herramientas de Sumarios BOE (Smart Summary v1.5.0)

| Herramienta | Propósito | Cuándo usar |
|-------------|-----------|-------------|
| `get_boe_summary_metadata` | Resumen compacto | Vista general del día (~1KB) |
| `get_boe_summary_section` | Docs de sección | Listar docs de una sección específica |
| `get_boe_document_info` | Info de documento | Detalles de un documento por ID |
| `get_boe_summary` | Sumario completo | ⚠️ DEPRECADO - Devuelve 300KB+ |

### Herramientas Auxiliares

| Herramienta | Propósito | Cuándo usar |
|-------------|-----------|-------------|
| `get_auxiliary_table` | Tablas de códigos | Obtener materias, rangos, departamentos |
| `get_borme_summary` | Sumario BORME | Publicaciones del boletín mercantil |

---

## Casos de Uso y Herramienta Recomendada

### Caso 1: "¿Qué se publicó hoy en el BOE?"

**Flujo recomendado:**
```
1. get_boe_summary_metadata(fecha="AAAAMMDD")
   → Vista general: 8 secciones con conteos

2. Usuario elige sección → get_boe_summary_section(fecha, seccion)
   → Lista paginada de documentos

3. Usuario quiere detalles → get_boe_document_info(identificador)
   → Información completa del documento
```

**NO usar:** `get_boe_summary` (330KB de respuesta)

---

### Caso 2: "Buscar una ley específica"

**Ejemplos:**
- "Busca la Ley 39/2015"
- "¿Existe una ley sobre protección de datos?"

**Flujo recomendado:**
```
1. search_laws_list(query_value="39/2015", rango_codigo="1300")
   → Lista de resultados con identificadores

2. get_law_structure_summary(identifier="BOE-A-2015-10565")
   → Estructura compacta de la ley
```

---

### Caso 3: "Ver el artículo X de una ley"

**Ejemplos:**
- "Muéstrame el artículo 21 de la Ley 39/2015"
- "¿Qué dice el artículo 5?"

**Flujo recomendado:**
```
1. get_article_info(identifier="BOE-A-2015-10565", articulo="21")
   → Texto completo del artículo con contexto
```

**Alternativa si no se conoce el identificador:**
```
1. search_laws_list(query_value="39/2015")
2. get_article_info(identifier, articulo)
```

---

### Caso 4: "Buscar dentro de una ley"

**Ejemplos:**
- "Busca 'plazo' en la Ley 39/2015"
- "¿Dónde menciona 'recurso de alzada'?"

**Flujo recomendado:**
```
1. search_in_law(identifier="BOE-A-2015-10565", query="plazo", limit=10)
   → Artículos que contienen el término
```

---

### Caso 5: "Ver estructura de una ley"

**Ejemplos:**
- "¿Cómo está organizada la Ley 40/2015?"
- "Dame el índice de la ley"

**Flujo recomendado:**
```
1. get_law_structure_summary(identifier="BOE-A-2015-10566")
   → Índice compacto (títulos, capítulos, artículos)

Si necesita más detalle:
2. get_law_index(identifier, limit=50, offset=0)
   → Índice paginado con más información
```

---

### Caso 6: "Oposiciones publicadas hoy"

**Flujo recomendado:**
```
1. get_boe_summary_metadata(fecha)
   → Ver cuántos items hay en sección "2B"

2. get_boe_summary_section(fecha, seccion="2B", limit=20)
   → Lista de convocatorias de oposiciones
```

---

### Caso 7: "Disposiciones generales de hoy"

**Flujo recomendado:**
```
1. get_boe_summary_section(fecha, seccion="1", limit=20)
   → Leyes, decretos y disposiciones del día
```

**Códigos de sección:**
| Código | Contenido |
|--------|-----------|
| 1 | Disposiciones generales (leyes, RD, órdenes) |
| 2A | Nombramientos, situaciones, ceses |
| 2B | Oposiciones y concursos |
| 3 | Otras disposiciones |
| 4 | Administración de Justicia |
| 5A | Contratación del Sector Público |
| 5B | Otros anuncios oficiales |
| 5C | Anuncios particulares |

---

### Caso 8: "Buscar leyes vigentes sobre X tema"

**Flujo recomendado:**
```
1. search_laws_list(
     query_value="protección datos",
     solo_vigente=True,
     limit=10
   )
   → Lista de normas vigentes sobre el tema
```

---

### Caso 9: "Leyes de un ministerio específico"

**Flujo recomendado:**
```
1. get_auxiliary_table("departamentos")
   → Obtener código del ministerio (ej: "4710" = Hacienda)

2. search_laws_list(departamento_codigo="4710", limit=20)
   → Normas de ese ministerio
```

---

### Caso 10: "Obtener metadatos de una ley"

**Flujo recomendado:**
```
1. get_law_section(identifier="BOE-A-2015-10565", section="metadatos")
   → Título, fecha, rango, estado de consolidación
```

---

## Matriz de Decisión Rápida

| Necesito... | Herramienta |
|-------------|-------------|
| Vista general del BOE del día | `get_boe_summary_metadata` |
| Documentos de una sección | `get_boe_summary_section` |
| Detalles de un documento BOE | `get_boe_document_info` |
| Buscar leyes por texto/fecha | `search_laws_list` |
| Estructura de una ley | `get_law_structure_summary` |
| Índice paginado de ley | `get_law_index` |
| Texto de un artículo | `get_article_info` |
| Buscar dentro de una ley | `search_in_law` |
| Metadatos de una ley | `get_law_section(section="metadatos")` |
| Texto completo de una ley | `get_law_section(section="texto")` |
| Códigos de materias/rangos | `get_auxiliary_table` |

---

## Anti-patrones: Qué NO hacer

### ❌ NO usar `get_boe_summary` para ver el día
**Problema:** Devuelve 300KB+ de datos
**Usar:** `get_boe_summary_metadata` + `get_boe_summary_section`

### ❌ NO usar `get_law_section(section="completa")` inicialmente
**Problema:** Puede devolver megabytes de datos
**Usar:** `get_law_structure_summary` primero, luego navegar

### ❌ NO buscar sin filtros
**Problema:** Demasiados resultados
**Usar:** Siempre añadir `solo_vigente=True`, `limit`, filtros de fecha

### ❌ NO ignorar la paginación
**Problema:** Respuestas truncadas
**Usar:** Siempre verificar `hay_mas` y usar `offset` para continuar

---

## Flujos Completos de Ejemplo

### Flujo A: Investigar ley específica

```
Usuario: "Háblame de la Ley 39/2015 de Procedimiento Administrativo"

1. search_laws_list(numero_oficial="39/2015", rango_codigo="1300")
   → identificador: BOE-A-2015-10565

2. get_law_section(identifier, section="metadatos")
   → Título, fecha, vigencia

3. get_law_structure_summary(identifier)
   → Índice: 4 títulos, 133 artículos

4. [Si usuario pregunta por artículo específico]
   get_article_info(identifier, articulo="21")
   → Texto del artículo 21
```

### Flujo B: Resumen del BOE diario

```
Usuario: "¿Qué hay en el BOE de hoy?"

1. get_boe_summary_metadata(fecha="20241203")
   → 85 documentos en 8 secciones

2. [Usuario interesado en oposiciones]
   get_boe_summary_section(fecha, seccion="2B", limit=10)
   → 10 primeras convocatorias

3. [Usuario quiere detalles de una]
   get_boe_document_info(identificador="BOE-A-2024-25060")
   → Información completa
```

### Flujo C: Búsqueda temática

```
Usuario: "Busca leyes sobre energías renovables"

1. get_auxiliary_table("materias")
   → Buscar código de "energía" o "renovables"

2. search_laws_list(
     query_value="energías renovables",
     solo_vigente=True,
     limit=10
   )
   → Lista de normas vigentes

3. [Para cada resultado interesante]
   get_law_structure_summary(identifier)
   → Ver estructura antes de profundizar
```

---

## Tamaños de Respuesta Esperados

| Herramienta | Tamaño típico | Máximo |
|-------------|---------------|--------|
| `get_boe_summary_metadata` | ~1 KB | ~2 KB |
| `get_boe_summary_section` | ~6 KB | ~15 KB |
| `get_boe_document_info` | ~500 B | ~1 KB |
| `get_law_structure_summary` | ~3 KB | ~10 KB |
| `get_law_index` (limit=20) | ~5 KB | ~15 KB |
| `get_article_info` | ~2 KB | ~20 KB |
| `search_in_law` (limit=10) | ~3 KB | ~10 KB |
| `search_laws_list` (limit=20) | ~10 KB | ~30 KB |

---

## Códigos de Error Comunes

| Código | Significado | Acción |
|--------|-------------|--------|
| `VALIDATION_ERROR` | Parámetro inválido | Revisar formato de fecha, ID |
| `SUMARIO_NO_DISPONIBLE` | No hay BOE ese día | Es domingo/festivo |
| `LEY_NO_ENCONTRADA` | ID inexistente | Verificar identificador |
| `SECCION_NO_ENCONTRADA` | Sección no existe | Usar códigos válidos (1, 2A...) |
| `ARTICULO_NO_ENCONTRADO` | Artículo no existe | Verificar número de artículo |
| `SIN_RESULTADOS` | Búsqueda vacía | Ampliar criterios de búsqueda |

---

## Notas para Implementación en MCP

Este documento puede incluirse en las instrucciones del servidor MCP para que los LLMs seleccionen automáticamente la herramienta correcta.

**Ejemplo de instrucción MCP:**
```
Cuando el usuario pregunte sobre el BOE del día, usa get_boe_summary_metadata
primero para obtener un resumen, NO uses get_boe_summary que devuelve
demasiados datos.
```

---

**FIN DE LA GUÍA**
