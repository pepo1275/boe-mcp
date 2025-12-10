# Catálogo Completo de Herramientas BOE-MCP

**Versión:** v1.6.0
**Fecha:** 2025-12-10
**Propósito:** Referencia exhaustiva con ejemplos reales de respuestas

---

## Índice

1. [Herramientas de Sumario BOE (Smart Summary)](#1-herramientas-de-sumario-boe-smart-summary)
2. [Herramientas de Legislación Consolidada](#2-herramientas-de-legislación-consolidada)
3. [Herramientas Auxiliares](#3-herramientas-auxiliares)
4. [Herramientas Deprecadas](#4-herramientas-deprecadas)
5. [Resumen de Tamaños de Respuesta](#5-resumen-de-tamaños-de-respuesta)
6. [Propuestas de Nuevas Herramientas](#6-propuestas-de-nuevas-herramientas)

---

## 1. Herramientas de Sumario BOE (Smart Summary)

### 1.1 `get_boe_summary_metadata`

**Propósito:** Vista general del BOE de un día con conteo por sección.

**Cuándo usar:**
- Primer paso para explorar el BOE del día
- Saber cuántos documentos hay en cada sección
- Decidir qué sección explorar en detalle

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `fecha` | string | Sí | Fecha en formato AAAAMMDD |

**Ejemplo de llamada:**
```python
get_boe_summary_metadata("20241209")
```

**Respuesta real (944 bytes):**
```json
{
  "fecha": "20241209",
  "numero_boe": "296",
  "identificador": "BOE-S-2024-296",
  "url_pdf_sumario": "https://www.boe.es/boe/dias/2024/12/09/pdfs/BOE-S-2024-296.pdf",
  "total_documentos": 310,
  "secciones": [
    {"codigo": "1", "nombre": "I. Disposiciones generales", "num_items": 3},
    {"codigo": "2A", "nombre": "II. Autoridades y personal. - A. Nombramientos...", "num_items": 13},
    {"codigo": "2B", "nombre": "II. Autoridades y personal. - B. Oposiciones...", "num_items": 32},
    {"codigo": "3", "nombre": "III. Otras disposiciones", "num_items": 47},
    {"codigo": "4", "nombre": "IV. Administración de Justicia", "num_items": 44},
    {"codigo": "5A", "nombre": "V. Anuncios. - A. Contratación...", "num_items": 108},
    {"codigo": "5B", "nombre": "V. Anuncios. - B. Otros anuncios oficiales", "num_items": 63},
    {"codigo": "5C", "nombre": "V. Anuncios. - C. Anuncios particulares", "num_items": 0}
  ]
}
```

**Tamaño típico:** ~900-1000 bytes

---

### 1.2 `get_boe_summary_section`

**Propósito:** Obtener documentos de una sección específica con paginación.

**Cuándo usar:**
- Después de `get_boe_summary_metadata` para ver detalle de una sección
- Navegar documentos de oposiciones (2B), disposiciones (1), etc.
- Cuando hay muchos documentos y necesitas paginar

**Parámetros:**
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `fecha` | string | Sí | - | Fecha AAAAMMDD |
| `seccion` | string | Sí | - | Código: 1, 2A, 2B, 3, 4, 5A, 5B, 5C |
| `limit` | int | No | 20 | Máximo documentos (max: 100) |
| `offset` | int | No | 0 | Para paginación |

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

**Ejemplo de llamada:**
```python
get_boe_summary_section("20241209", "1", limit=5)
```

**Respuesta real (2130 bytes):**
```json
{
  "fecha": "20241209",
  "seccion": {
    "codigo": "1",
    "nombre": "I. Disposiciones generales"
  },
  "total_items": 3,
  "offset": 0,
  "limit": 5,
  "hay_mas": false,
  "documentos": [
    {
      "identificador": "BOE-A-2024-25585",
      "titulo": "Adenda n.º 1 al Acuerdo administrativo entre el Ministerio de Asuntos Exteriores...",
      "departamento": "MINISTERIO DE ASUNTOS EXTERIORES, UNIÓN EUROPEA Y COOPERACIÓN",
      "departamento_codigo": "9562",
      "epigrafe": "Acuerdos internacionales administrativos",
      "url_pdf": "https://www.boe.es/boe/dias/2024/12/09/pdfs/BOE-A-2024-25585.pdf",
      "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-25585"
    },
    {
      "identificador": "BOE-A-2024-25586",
      "titulo": "Orden CNU/1385/2024, de 3 de diciembre, por la que se regula...",
      "departamento": "MINISTERIO DE CIENCIA, INNOVACIÓN Y UNIVERSIDADES",
      "departamento_codigo": "9565",
      "epigrafe": "Cuerpos docentes universitarios",
      "url_pdf": "https://www.boe.es/boe/dias/2024/12/09/pdfs/BOE-A-2024-25586.pdf",
      "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-25586"
    },
    {
      "identificador": "BOE-A-2024-25587",
      "titulo": "Ley 5/2024, de 21 de noviembre, de modificación de la Ley 21/2023...",
      "departamento": "COMUNIDAD AUTÓNOMA DEL PAÍS VASCO",
      "departamento_codigo": "8140",
      "epigrafe": "Presupuestos",
      "url_pdf": "https://www.boe.es/boe/dias/2024/12/09/pdfs/BOE-A-2024-25587.pdf",
      "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-25587"
    }
  ]
}
```

**Tamaño típico:** ~500-700 bytes por documento × limit

---

### 1.3 `get_boe_document_info`

**Propósito:** Obtener información detallada de un documento específico.

**Cuándo usar:**
- Cuando conoces el identificador (BOE-A-YYYY-NNNNN)
- Para obtener URLs del PDF/HTML/XML
- Para ver páginas, sección y epígrafe

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identificador` | string | Sí | ID del documento (ej: BOE-A-2024-25586) |
| `fecha` | string | No | Fecha de publicación (mejora resultados) |

**Ejemplo de llamada:**
```python
get_boe_document_info("BOE-A-2024-25586", "20241209")
```

**Respuesta real (754 bytes):**
```json
{
  "identificador": "BOE-A-2024-25586",
  "titulo": "Orden CNU/1385/2024, de 3 de diciembre, por la que se regula el procedimiento específico para reconocer como acreditado al profesorado de las universidades de Estados Miembros de la Unión Europea.",
  "departamento": "MINISTERIO DE CIENCIA, INNOVACIÓN Y UNIVERSIDADES",
  "departamento_codigo": "9565",
  "seccion": {
    "codigo": "1",
    "nombre": "I. Disposiciones generales"
  },
  "epigrafe": "Cuerpos docentes universitarios",
  "url_pdf": "https://www.boe.es/boe/dias/2024/12/09/pdfs/BOE-A-2024-25586.pdf",
  "url_html": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-25586",
  "url_xml": "https://www.boe.es/diario_boe/xml.php?id=BOE-A-2024-25586",
  "paginas": {
    "inicial": "166972",
    "final": "166977"
  }
}
```

**Tamaño típico:** ~500-800 bytes

---

## 2. Herramientas de Legislación Consolidada

### 2.1 `search_laws_list`

**Propósito:** Buscar normas en la legislación consolidada.

**Cuándo usar:**
- Encontrar una ley por nombre/número
- Buscar normas sobre un tema
- Filtrar por rango (ley, RD, orden), departamento, fechas

**Parámetros principales:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `query_value` | string | None | Texto a buscar |
| `solo_vigente` | bool | True | Solo normas vigentes |
| `rango_codigo` | string | None | 1300=Ley, 1290=LO, 1340=RD, 1320=RD-ley |
| `numero_oficial` | string | None | Número oficial (ej: "39/2015") |
| `limit` | int | 50 | Máximo resultados |
| `offset` | int | 0 | Para paginación |

**Ejemplo de llamada:**
```python
search_laws_list(
    query_value="procedimiento administrativo",
    solo_vigente=True,
    rango_codigo="1300",
    limit=3
)
```

**Respuesta real (3086 bytes con 3 resultados):**
```json
{
  "endpoint": "/datosabiertos/api/legislacion-consolidada",
  "params": {...},
  "data": {
    "status": {"code": "200", "text": "ok"},
    "data": [
      {
        "identificador": "BOE-A-2015-10565",
        "titulo": "Ley 39/2015, de 1 de octubre, del Procedimiento Administrativo Común de las Administraciones Públicas.",
        "rango": {"codigo": "1300", "texto": "Ley"},
        "fecha_disposicion": "20151001",
        "numero_oficial": "39/2015",
        "departamento": {"codigo": "7723", "texto": "Jefatura del Estado"},
        "vigencia_agotada": "N",
        "url_eli": "https://www.boe.es/eli/es/l/2015/10/01/39",
        "url_html_consolidada": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565"
      },
      {...},
      {...}
    ]
  }
}
```

**Tamaño típico:** ~800-1200 bytes por resultado

---

### 2.2 `get_law_structure_summary`

**Propósito:** Obtener la estructura jerárquica de una ley (títulos, capítulos, artículos).

**Cuándo usar:**
- Ver el índice de una ley
- Saber cuántos artículos tiene
- Identificar artículos modificados

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identifier` | string | Sí | ID de la ley (ej: BOE-A-2015-10565) |

**Ejemplo de llamada:**
```python
get_law_structure_summary("BOE-A-2015-10565")
```

**Respuesta real (2565 bytes):**
```json
{
  "identifier": "BOE-A-2015-10565",
  "titulo": "TÍTULO PRELIMINAR",
  "fecha_publicacion": "20151002",
  "total_articulos": 133,
  "total_modificados": 10,
  "estructura": [
    {
      "id": "ti",
      "tipo": "titulo",
      "titulo": "TÍTULO I",
      "num_articulos": 10,
      "num_modificados": 3,
      "hijos": [
        {
          "id": "ci",
          "tipo": "capitulo",
          "titulo": "CAPÍTULO I",
          "num_articulos": 6,
          "num_modificados": 1,
          "hijos": []
        },
        {...}
      ]
    },
    {...}
  ]
}
```

**Tamaño típico:** ~1500-4000 bytes según complejidad de la ley

---

### 2.3 `get_article_info`

**Propósito:** Obtener información de un artículo específico.

**Cuándo usar:**
- Consultar el texto de un artículo concreto
- Ver si un artículo ha sido modificado
- Conocer la ubicación (título/capítulo) del artículo

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identifier` | string | Sí | ID de la ley |
| `articulo` | string | Sí | Número del artículo (ej: "21", "15 bis") |

**Ejemplo de llamada:**
```python
get_article_info("BOE-A-2015-10565", "21")
```

**Respuesta real (441 bytes):**
```json
{
  "identifier": "BOE-A-2015-10565",
  "articulo": "21",
  "block_id": "a21",
  "titulo_completo": "Artículo 21",
  "fecha_actualizacion": "20151002",
  "fecha_ley_original": "20151002",
  "modificado": false,
  "ubicacion": {
    "libro": null,
    "titulo": "TÍTULO II",
    "capitulo": "CAPÍTULO I",
    "seccion": null
  },
  "url_bloque": "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2015-10565/texto/bloque/a21",
  "texto": null
}
```

**Tamaño típico:** ~400-600 bytes (sin texto), ~1000-5000 bytes (con texto)

---

### 2.4 `get_article_modifications` (v1.6.0)

**Propósito:** Verificar si un artículo ha sido modificado y por qué normas.

**Cuándo usar:**
- Auditar procedimientos que usan artículos específicos
- Monitorizar cambios legislativos (cron)
- Verificar si un artículo sigue vigente como estaba

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identifier` | string | Sí | ID de la ley (ej: BOE-A-2000-323) |
| `articulo` | string | Sí | Número del artículo (ej: "458", "21 bis") |

**Ejemplo de llamada:**
```python
get_article_modifications("BOE-A-2000-323", "458")
```

**Respuesta real - Artículo modificado (~600 bytes):**
```json
{
  "modificado": true,
  "articulo": "458",
  "ley_id": "BOE-A-2000-323",
  "titulo_articulo": "Artículo 458. Tramitación del recurso de apelación.",
  "fecha_version_original": "20010108",
  "fecha_version_actual": "20231121",
  "total_versiones": 5,
  "modificaciones": [
    {
      "fecha": "20090504",
      "norma_modificadora": "Ley 13/2009, de 3 de noviembre"
    },
    {
      "fecha": "20151006",
      "norma_modificadora": "Ley 42/2015, de 5 de octubre"
    },
    {
      "fecha": "20231121",
      "norma_modificadora": "Real Decreto-ley 6/2023, de 19 de diciembre"
    }
  ]
}
```

**Respuesta real - Artículo sin modificaciones (~300 bytes):**
```json
{
  "modificado": false,
  "articulo": "386",
  "ley_id": "BOE-A-2020-4859",
  "titulo_articulo": "Artículo 386. Objeto.",
  "fecha_version_original": "20200901",
  "fecha_version_actual": "20200901",
  "total_versiones": 1,
  "modificaciones": []
}
```

**Tamaño típico:** ~300 bytes (sin modificar), ~400-800 bytes (modificado)

**IDs de leyes comunes:**
| Ley | Identificador |
|-----|---------------|
| LEC (Ley Enjuiciamiento Civil) | BOE-A-2000-323 |
| TRLC (Texto Refundido Ley Concursal) | BOE-A-2020-4859 |
| LPAC (Procedimiento Administrativo) | BOE-A-2015-10565 |
| LRJSP (Régimen Jurídico Sector Público) | BOE-A-2015-10566 |

---

### 2.5 `search_in_law`

**Propósito:** Buscar texto dentro de una ley específica.

**Cuándo usar:**
- Encontrar dónde se menciona un término en una ley
- Buscar artículos sobre un tema concreto
- Filtrar por artículos modificados

**Parámetros:**
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | string | Sí | - | ID de la ley |
| `query` | string | Sí | - | Texto a buscar |
| `limit` | int | No | 10 | Máximo resultados |
| `offset` | int | No | 0 | Para paginación |
| `solo_modificados` | bool | No | False | Solo arts. modificados |

**Ejemplo de llamada:**
```python
search_in_law("BOE-A-2015-10565", "plazo", limit=5)
```

**Respuesta (252 bytes si no hay resultados):**
```json
{
  "identifier": "BOE-A-2015-10565",
  "criterios": {
    "query": "plazo",
    "articulos": null,
    "solo_modificados": false,
    "modificados_desde": null,
    "modificados_hasta": null
  },
  "total_encontrados": 0,
  "offset": 0,
  "limit": 5,
  "hay_mas": false,
  "resultados": []
}
```

**Tamaño típico:** ~250 bytes base + ~500 bytes por resultado

---

### 2.5 `get_law_index`

**Propósito:** Obtener índice paginado de una ley con más detalle.

**Cuándo usar:**
- Cuando `get_law_structure_summary` no es suficiente
- Navegar leyes muy grandes con paginación
- Obtener lista de artículos con títulos

**Parámetros:**
| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | string | Sí | - | ID de la ley |
| `limit` | int | No | 50 | Máximo items |
| `offset` | int | No | 0 | Para paginación |

---

### 2.6 `get_law_section`

**Propósito:** Obtener partes específicas de una ley (metadatos, texto, análisis).

**Cuándo usar:**
- Obtener metadatos completos de una ley
- Obtener el texto completo consolidado
- Ver análisis jurídico (materias, referencias)

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identifier` | string | Sí | ID de la ley |
| `section` | string | Sí | completa, metadatos, analisis, texto, indice, bloque |
| `block_id` | string | Solo si section=bloque | ID del bloque |

**⚠️ Precaución:** `section="completa"` o `section="texto"` pueden devolver respuestas MUY grandes (megabytes).

---

## 3. Herramientas Auxiliares

### 3.1 `get_auxiliary_table`

**Propósito:** Obtener tablas de códigos de referencia.

**Cuándo usar:**
- Obtener códigos de rangos (1300=Ley, etc.)
- Obtener códigos de departamentos/ministerios
- Buscar códigos de materias temáticas

**Parámetros:**
| Parámetro | Tipo | Valores válidos |
|-----------|------|-----------------|
| `table_name` | string | rangos, materias, departamentos, ambitos, estados-consolidacion, relaciones-anteriores, relaciones-posteriores |

**Ejemplo de llamada:**
```python
get_auxiliary_table("rangos")
```

**Respuesta real:**
```json
{
  "status": {"code": "200", "text": "ok"},
  "data": {
    "1020": "Acuerdo",
    "1070": "Constitución",
    "1290": "Ley Orgánica",
    "1300": "Ley",
    "1310": "Real Decreto Legislativo",
    "1320": "Real Decreto-ley",
    "1340": "Real Decreto",
    "1350": "Orden",
    "1370": "Resolución",
    "1390": "Circular",
    "1410": "Instrucción",
    "1470": "Decreto Legislativo",
    "1500": "Decreto-ley",
    "1510": "Decreto"
  }
}
```

**Tamaño típico:** ~500 bytes (rangos), ~50KB (materias), ~20KB (departamentos)

---

### 3.2 `get_borme_summary`

**Propósito:** Obtener sumario del BORME (Boletín Oficial del Registro Mercantil).

**Cuándo usar:**
- Consultar publicaciones mercantiles del día
- Buscar actos de sociedades

**⚠️ Nota:** Esta herramienta NO tiene versión "Smart". Devuelve respuestas grandes.

---

## 4. Herramientas Deprecadas

### 4.1 `get_boe_summary` ⚠️ DEPRECADA

**NO USAR.** Devuelve ~150KB de datos, bloquea la ventana de contexto.

**Usar en su lugar:**
1. `get_boe_summary_metadata` para vista general
2. `get_boe_summary_section` para sección específica
3. `get_boe_document_info` para documento específico

---

## 5. Resumen de Tamaños de Respuesta

| Herramienta | Tamaño Típico | Máximo | Paginación |
|-------------|---------------|--------|------------|
| `get_boe_summary_metadata` | ~950 bytes | ~1.2 KB | No necesaria |
| `get_boe_summary_section` | ~2 KB (limit=5) | ~15 KB | ✅ Sí |
| `get_boe_document_info` | ~700 bytes | ~1 KB | No necesaria |
| `search_laws_list` | ~3 KB (limit=3) | ~30 KB | ✅ Sí |
| `get_law_structure_summary` | ~2.5 KB | ~10 KB | No |
| `get_article_info` | ~450 bytes | ~5 KB | No |
| `get_article_modifications` | ~300-600 bytes | ~800 bytes | No |
| `search_in_law` | ~250 bytes base | ~10 KB | ✅ Sí |
| `get_auxiliary_table` | ~500 bytes - 50 KB | Variable | No |
| ~~`get_boe_summary`~~ | ~~150 KB~~ | ~~300 KB~~ | ~~No~~ |

---

## 6. Propuestas de Nuevas Herramientas

### 6.1 `search_boe_summary` (PROPUESTA)

**Propósito:** Buscar dentro del sumario del día por texto, departamento o materia.

**Problema que resuelve:**
Actualmente para buscar "¿hay algo sobre vivienda hoy?" hay que:
1. Llamar a `get_boe_summary_section` para CADA sección
2. Filtrar manualmente los resultados

**Parámetros propuestos:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `fecha` | string | Sí | Fecha AAAAMMDD |
| `query` | string | No | Texto a buscar en títulos |
| `departamento_codigo` | string | No | Filtrar por departamento |
| `seccion` | string | No | Limitar a una sección |
| `limit` | int | No | Máximo resultados (default: 10) |

**Ejemplo de uso:**
```python
# ¿Hay algo sobre universidades hoy?
search_boe_summary("20241209", query="universidad")

# ¿Qué publicó el Ministerio de Hacienda?
search_boe_summary("20241209", departamento_codigo="4710")
```

**Respuesta simulada (~800 bytes):**
```json
{
  "fecha": "20241209",
  "criterios": {
    "query": "universidad",
    "departamento_codigo": null,
    "seccion": null
  },
  "total_encontrados": 2,
  "hay_mas": false,
  "documentos": [
    {
      "identificador": "BOE-A-2024-25586",
      "titulo": "Orden CNU/1385/2024... profesorado de las universidades...",
      "departamento": "MINISTERIO DE CIENCIA, INNOVACIÓN Y UNIVERSIDADES",
      "seccion": "1",
      "relevancia": "titulo"
    },
    {
      "identificador": "BOE-A-2024-25601",
      "titulo": "Resolución de la Universidad de Salamanca...",
      "departamento": "UNIVERSIDADES",
      "seccion": "2B",
      "relevancia": "titulo"
    }
  ]
}
```

**Beneficio:** Una sola llamada en lugar de 8 (una por sección).

---

### 6.2 `check_law_updates` (PROPUESTA)

**Propósito:** Verificar si una ley ha sido afectada por publicaciones recientes.

**Problema que resuelve:**
Actualmente para saber "¿El BOE de hoy afecta a la Ley 39/2015?" hay que:
1. Buscar en cada sección del sumario
2. Leer títulos buscando referencias
3. No hay forma automatizada

**Parámetros propuestos:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `identifier` | string | Sí | ID de la ley a verificar |
| `fecha_desde` | string | No | Fecha inicio (default: hoy) |
| `fecha_hasta` | string | No | Fecha fin (default: hoy) |

**Ejemplo de uso:**
```python
# ¿Se publicó algo hoy que afecte a la Ley 39/2015?
check_law_updates("BOE-A-2015-10565")

# ¿En la última semana?
check_law_updates("BOE-A-2015-10565", fecha_desde="20241202", fecha_hasta="20241209")
```

**Respuesta simulada (~600 bytes):**
```json
{
  "identifier": "BOE-A-2015-10565",
  "titulo_ley": "Ley 39/2015, del Procedimiento Administrativo Común",
  "periodo": {
    "desde": "20241209",
    "hasta": "20241209"
  },
  "afectaciones_encontradas": 0,
  "documentos": []
}
```

**O si hay afectaciones:**
```json
{
  "identifier": "BOE-A-2015-10565",
  "titulo_ley": "Ley 39/2015, del Procedimiento Administrativo Común",
  "periodo": {
    "desde": "20241201",
    "hasta": "20241209"
  },
  "afectaciones_encontradas": 1,
  "documentos": [
    {
      "identificador": "BOE-A-2024-XXXXX",
      "titulo": "Real Decreto-ley X/2024 que modifica el artículo 21...",
      "fecha_publicacion": "20241205",
      "tipo_afectacion": "modifica",
      "articulos_afectados": ["21", "32"]
    }
  ]
}
```

**Beneficio:** Monitorización proactiva de cambios legislativos.

---

### 6.3 `get_boe_summary_compact` (PROPUESTA ALTERNATIVA)

**Propósito:** Versión ultra-compacta del sumario para sesiones largas.

**Problema que resuelve:**
Incluso con Smart Summary, una exploración completa del BOE puede consumir tokens rápidamente si el usuario navega varias secciones.

**Parámetros propuestos:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `fecha` | string | Sí | Fecha AAAAMMDD |
| `seccion` | string | No | Filtrar por sección |
| `formato` | string | No | "lista" (default) o "tabla" |

**Respuesta simulada - formato lista (~400 bytes para sección 1):**
```json
{
  "fecha": "20241209",
  "seccion": "1",
  "items": [
    "BOE-A-2024-25585: Adenda Acuerdo Myanmar [MAEC]",
    "BOE-A-2024-25586: Orden profesorado UE [MCIU]",
    "BOE-A-2024-25587: Ley presupuestos Euskadi [CAPV]"
  ]
}
```

**Beneficio:** ~70% menos tokens que `get_boe_summary_section`.

---

### 6.4 Reducción de Límites (PROPUESTA)

**Alternativa a nuevas herramientas:** Reducir los defaults actuales.

| Herramienta | Actual | Propuesto | Justificación |
|-------------|--------|-----------|---------------|
| `search_laws_list` | 50 | 10 | Rara vez se necesitan 50 |
| `get_boe_summary_section` | 20 | 10 | Típico: explorar primeros |
| `search_in_law` | 10 | 5 | Búsquedas suelen ser específicas |

**Impacto estimado:**
- `search_laws_list`: de ~30KB a ~10KB por llamada
- `get_boe_summary_section`: de ~7KB a ~3.5KB por llamada

---

## 7. Matriz de Decisión: Qué Herramienta Usar

| Necesito... | Herramienta | Tamaño |
|-------------|-------------|--------|
| Vista general del BOE del día | `get_boe_summary_metadata` | ~1 KB |
| Lista de oposiciones de hoy | `get_boe_summary_section(seccion="2B")` | ~3-7 KB |
| ¿Hay algo sobre X tema hoy? | **[PROPUESTA]** `search_boe_summary` | ~1 KB |
| Detalles de un documento BOE | `get_boe_document_info` | ~700 B |
| Buscar una ley por nombre | `search_laws_list` | ~3 KB |
| Estructura de una ley | `get_law_structure_summary` | ~2.5 KB |
| Texto de un artículo | `get_article_info` | ~500 B |
| ¿Ha sido modificado el artículo X? | `get_article_modifications` | ~300-600 B |
| ¿Se modificó la ley X? | **[PROPUESTA]** `check_law_updates` | ~600 B |
| Códigos de rangos/materias | `get_auxiliary_table` | ~500 B - 50 KB |

---

**FIN DEL CATÁLOGO**
