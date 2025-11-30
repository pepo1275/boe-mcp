# BOE-MCP Development Framework

**Version**: 2.1.0
**Date**: 2025-11-30
**Methodology**: RPVEA 2.0 Adapted
**Philosophy**: Complete API Client, Zero Business Logic

---

## 0. API Factual Analysis (Audit 2025-11-30)

> **Esta sección documenta el análisis exhaustivo de la API BOE vs el MCP actual.**
> **Propósito**: Servir de referencia para implementación en futuras sesiones.

### 0.1 Capacidades de la API para Fechas y Relaciones

La API del BOE **SÍ proporciona** información completa para:
- Fechas de vigencia, derogación, anulación
- Relaciones entre normas (qué deroga a qué, qué modifica a qué)
- Historial de versiones de artículos

#### Campos de Fecha Disponibles

| Campo | Endpoint | Descripción | Uso para Grafos/Temporal |
|-------|----------|-------------|--------------------------|
| `fecha_disposicion` | Lista + Metadatos | Fecha original de la norma | Ordenación cronológica |
| `fecha_publicacion` | Lista + Metadatos | Cuándo se publicó en BOE | Timeline de publicaciones |
| `fecha_vigencia` | Lista + Metadatos | Cuándo entró en vigor | **Clave para búsqueda temporal** |
| `fecha_derogacion` | **Solo Metadatos** | Cuándo fue derogada | **Clave para validez temporal** |
| `fecha_anulacion` | **Solo Metadatos** | Cuándo fue anulada | Estado legal |
| `estatus_derogacion` | **Solo Metadatos** | S/N - ¿Está derogada? | Filtro rápido |
| `estatus_anulacion` | **Solo Metadatos** | S/N - ¿Está anulada? | Filtro rápido |
| `vigencia_agotada` | Lista | S/N - ¿Vigente? | Filtro de búsqueda |
| `fecha_caducidad` | Bloque de texto | Caducidad de un bloque | Vigencia por artículo |

#### Estructura de Relaciones (Endpoint `/analisis`)

```xml
<referencias>
  <anteriores>  <!-- Esta norma AFECTA A normas anteriores -->
    <anterior>
      <id_norma>BOE-A-1989-14247</id_norma>
      <relacion codigo="210">DEROGA</relacion>
      <texto>Disposición derogatoria única</texto>
    </anterior>
  </anteriores>
  <posteriores>  <!-- Normas posteriores AFECTAN A esta -->
    <posterior>
      <id_norma>BOE-A-2022-17040</id_norma>
      <relacion codigo="420">SE MODIFICA</relacion>
      <texto>el artículo 22, por art. 3 de...</texto>
    </posterior>
  </posteriores>
</referencias>
```

#### Códigos de Relaciones (Tablas Auxiliares)

| Tipo | Tabla | Códigos Ejemplo | Significado |
|------|-------|-----------------|-------------|
| **Anteriores** | `relaciones-anteriores` | 210=DEROGA, 212=MODIFICA, 221=ANULA | Esta norma → afecta a otras |
| **Posteriores** | `relaciones-posteriores` | 406=SE DEROGA, 420=SE MODIFICA, 407=SE AÑADE | Otras normas → afectan a esta |

#### Versiones Históricas en Bloques

```xml
<bloque id="a22" tipo="precepto" titulo="Artículo 22">
  <version id_norma="BOE-A-1995-25444" fecha_publicacion="19951124" fecha_vigencia="19960524">
    <!-- Versión original -->
  </version>
  <version id_norma="BOE-A-2022-17040" fecha_publicacion="20221015" fecha_vigencia="20221016">
    <!-- Versión modificada -->
  </version>
</bloque>
```

### 0.2 Cobertura Actual: Endpoints

| Endpoint API | Tool MCP Actual | Estado |
|-------------|-----------------|--------|
| `/legislacion-consolidada` | `search_laws_list` | ✅ Implementado (parcial) |
| `/legislacion-consolidada/id/{id}` | `get_law_section("completa")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/metadatos` | `get_law_section("metadatos")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/analisis` | `get_law_section("analisis")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/metadata-eli` | `get_law_section("metadata-eli")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/texto` | `get_law_section("texto")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/texto/indice` | `get_law_section("indice")` | ✅ Implementado |
| `/legislacion-consolidada/id/{id}/texto/bloque/{id}` | `get_law_section("bloque")` | ✅ Implementado |
| `/boe/sumario/{fecha}` | `get_boe_summary` | ✅ Implementado |
| `/borme/sumario/{fecha}` | `get_borme_summary` | ✅ Implementado |
| `/datos-auxiliares/{tabla}` | `get_auxiliary_table` | ✅ Implementado |

**Conclusión**: Todos los endpoints están mapeados. El problema está en los **parámetros de búsqueda**.

### 0.3 Gaps Críticos: Parámetros de Búsqueda

| Campo API | En `search_laws_list` | Forma de Acceso Actual |
|-----------|----------------------|------------------------|
| `from` / `to` | ✅ Sí | Parámetros directos |
| `offset` / `limit` | ✅ Sí | Parámetros directos |
| `titulo` | ✅ Sí | Via `query_value` + `search_in_title_only` |
| `texto` | ✅ Sí | Via `query_value` + `search_in_title_only=False` |
| `vigencia_agotada` | ⚠️ Parcial | Via `solo_vigente` (hardcoded "N") |
| `estado_consolidacion@codigo` | ⚠️ Parcial | Via `solo_consolidada` (hardcoded "3") |
| `ambito@codigo` | ⚠️ Parcial | Via `ambito` enum (no código directo) |
| **`departamento@codigo`** | ❌ **GAP** | Solo via `must` dict genérico |
| **`rango@codigo`** | ❌ **GAP** | Solo via `must` dict genérico |
| **`materia@codigo`** | ❌ **GAP** | Solo via `must` dict genérico |
| **`numero_oficial`** | ❌ **GAP** | No expuesto |
| **`fecha_disposicion`** | ❌ **GAP** | No expuesto |
| **`fecha_publicacion` (range)** | ⚠️ Parcial | Solo via `range_filters` dict |
| **`diario_numero`** | ❌ **GAP** | No expuesto |

---

## 0.4 GAPS DETALLADOS: Impacto y Casos de Uso

### GAP 1: `departamento@codigo` - Filtro por Ministerio/Departamento

**Estado actual**: Solo accesible via parámetro genérico `must={"departamento@codigo": "5140"}`

**Problema**:
- El usuario debe conocer el formato exacto del campo
- No hay validación del código
- No es descubrible por el LLM

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Usabilidad | Requiere conocer sintaxis interna | Parámetro claro `departamento_codigo="5140"` |
| Validación | Ninguna | Validar que código existe en tabla auxiliar |
| Descubrimiento | El LLM no sabe que existe | Documentado en docstring |

**Casos de uso habilitados**:

```python
# CASO 1: Buscar todas las leyes del Ministerio de Hacienda
search_laws(departamento_codigo="5140", rango_codigo="1300")
# → Permite análisis de producción normativa por ministerio

# CASO 2: Monitoring de departamento específico
search_laws(departamento_codigo="9562", from_date="20240101")
# → Alertas de nuevas normas de Asuntos Exteriores

# CASO 3: Comparativa inter-ministerial
# Consultar varios departamentos para análisis comparativo
```

**Implementación propuesta**:
```python
departamento_codigo: str | None = None,  # Código del departamento emisor (ver get_auxiliary_table("departamentos"))
```

---

### GAP 2: `rango@codigo` - Filtro por Tipo de Norma

**Estado actual**: Solo accesible via `must={"rango@codigo": "1300"}`

**Problema**:
- Crítico para búsquedas especializadas
- Los códigos no son intuitivos (1300=Ley, 1310=LO, 1200=RD, 1240=RDL)

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Precisión | Mezcla de tipos normativos | Solo el tipo solicitado |
| Volumen | Resultados innecesarios | Reducción significativa |
| Relevancia | Baja para casos específicos | Alta |

**Casos de uso habilitados**:

```python
# CASO 1: Solo Leyes Orgánicas vigentes
search_laws(rango_codigo="1310", vigencia_agotada="N")
# → Catálogo de derechos fundamentales

# CASO 2: Reales Decretos-ley del último año (legislación de urgencia)
search_laws(rango_codigo="1240", fecha_publicacion_desde="20240101")
# → Análisis de uso de legislación de urgencia

# CASO 3: Órdenes ministeriales de un departamento
search_laws(rango_codigo="1650", departamento_codigo="5140")
# → Normativa administrativa de desarrollo

# CASO 4: Construcción de grafo jerárquico
# Ley → Real Decreto de desarrollo → Órdenes ministeriales
# Requiere poder filtrar por rango para cada nivel
```

**Implementación propuesta**:
```python
rango_codigo: str | None = None,  # Código del rango normativo (1300=Ley, 1310=LO, 1200=RD, 1240=RDL, ver get_auxiliary_table("rangos"))
```

---

### GAP 3: `materia@codigo` - Filtro por Temática

**Estado actual**: Solo accesible via `must={"materia@codigo": "6658"}`

**Problema**:
- La tabla de materias tiene ~3000 códigos
- Es el filtro temático principal de la API
- Sin él, las búsquedas textuales son imprecisas

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Precisión temática | Depende de palabras clave | Clasificación oficial BOE |
| Exhaustividad | Puede perder normas relevantes | Cobertura completa por tema |
| Ruido | Alto (falsos positivos) | Bajo |

**Casos de uso habilitados**:

```python
# CASO 1: Toda la normativa de protección de datos
search_laws(materia_codigo="4915")  # Protección de datos personales
# → Base para compliance RGPD

# CASO 2: Legislación laboral vigente
search_laws(materia_codigo="7023", vigencia_agotada="N")  # Relaciones laborales
# → Catálogo para departamento de RRHH

# CASO 3: Normativa medioambiental por comunidad autónoma
search_laws(materia_codigo="5949", ambito_codigo="2")  # Medio ambiente + Autonómico
# → Análisis de transposición de directivas por CCAA

# CASO 4: Grafo de materias relacionadas
# Una ley puede tener múltiples materias → red de conexiones temáticas
```

**Implementación propuesta**:
```python
materia_codigo: str | None = None,  # Código de materia temática (ver get_auxiliary_table("materias"))
```

---

### GAP 4: `numero_oficial` - Búsqueda por Número de Ley

**Estado actual**: No expuesto en absoluto

**Problema**:
- El caso de uso más común: "buscar la Ley 39/2015"
- Actualmente requiere búsqueda textual en título (imprecisa)
- `numero_oficial` es un campo indexado en la API

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Búsqueda directa | Imposible | `numero_oficial="39/2015"` |
| Precisión | Falsos positivos por título | Exactitud 100% |
| Velocidad | Búsqueda full-text | Búsqueda indexada |

**Casos de uso habilitados**:

```python
# CASO 1: Buscar ley específica por número
search_laws(numero_oficial="39/2015")
# → Ley 39/2015 de Procedimiento Administrativo

# CASO 2: Verificar existencia de norma citada
search_laws(numero_oficial="40/2015", rango_codigo="1300")
# → Validar referencias en documentos legales

# CASO 3: Buscar Real Decreto específico
search_laws(numero_oficial="203/2021", rango_codigo="1200")
# → RD 203/2021 (Reglamento de actuación de la Administración)

# CASO 4: Resolver referencias cruzadas en grafo
# Una norma cita "Ley 30/1992" → búsqueda directa para obtener BOE-ID
```

**Implementación propuesta**:
```python
numero_oficial: str | None = None,  # Número oficial de la norma (ej: "39/2015", "1/2023")
```

---

### GAP 5: `fecha_disposicion` - Fecha Original de la Norma

**Estado actual**: No expuesto como filtro de rango

**Problema**:
- Diferente de `fecha_publicacion` (puede haber días/semanas de diferencia)
- Importante para búsquedas históricas precisas
- Crítico para determinar "qué norma existía en fecha X"

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Precisión temporal | Solo por publicación | Por fecha real de la norma |
| Búsquedas históricas | Imprecisas | Exactas |
| Grafos temporales | Basados en publicación | Basados en disposición real |

**Casos de uso habilitados**:

```python
# CASO 1: Normas dictadas en un período legislativo
search_laws(
    fecha_disposicion_desde="20191203",  # Inicio XIV Legislatura
    fecha_disposicion_hasta="20231127"   # Fin XIV Legislatura
)
# → Producción normativa de una legislatura

# CASO 2: Respuesta a crisis (fechas exactas de disposición)
search_laws(
    fecha_disposicion_desde="20200314",  # Estado de alarma COVID
    fecha_disposicion_hasta="20200321",
    rango_codigo="1240"  # Reales Decretos-ley
)
# → Normativa de urgencia en primera semana de pandemia

# CASO 3: Timeline preciso para grafo temporal
# La fecha de disposición es cuando "nace" la norma jurídicamente
```

**Implementación propuesta**:
```python
fecha_disposicion_desde: str | None = None,  # Fecha disposición mínima (AAAAMMDD)
fecha_disposicion_hasta: str | None = None,  # Fecha disposición máxima (AAAAMMDD)
```

---

### GAP 6: `diario_numero` - Número del BOE

**Estado actual**: No expuesto

**Problema**:
- Necesario para referenciar publicaciones específicas del BOE
- Útil para verificar citas bibliográficas legales
- Permite acceso a sumarios específicos

**Impacto de solucionarlo**:

| Aspecto | Sin solucionar | Con solución |
|---------|----------------|--------------|
| Referencias | Solo por fecha | Por número exacto de BOE |
| Verificación | Imposible verificar citas | Verificación directa |
| Correlación | Manual | Automática con sumarios |

**Casos de uso habilitados**:

```python
# CASO 1: Todas las disposiciones de un BOE concreto
search_laws(diario_numero="130")
# → Contenido normativo del BOE-130

# CASO 2: Verificar cita legal
# Cita: "BOE núm. 236, de 1 de octubre de 2015"
search_laws(diario_numero="236", fecha_publicacion_desde="20151001", fecha_publicacion_hasta="20151001")
# → Confirmar existencia y obtener identificador

# CASO 3: Correlacionar con sumario
# get_boe_summary devuelve diario_numero → usar para búsqueda detallada
```

**Implementación propuesta**:
```python
diario_numero: int | None = None,  # Número del BOE
```

---

### 0.5 Resumen de Implementación de Gaps

| Gap | Prioridad | Esfuerzo | Casos de Uso Principales |
|-----|-----------|----------|--------------------------|
| `rango_codigo` | 🔴 Alta | Bajo | Filtro por tipo de norma, grafos jerárquicos |
| `materia_codigo` | 🔴 Alta | Bajo | Búsquedas temáticas, compliance |
| `numero_oficial` | 🔴 Alta | Bajo | Búsqueda directa de normas citadas |
| `departamento_codigo` | 🟡 Media | Bajo | Análisis por ministerio, monitoring |
| `fecha_disposicion` | 🟡 Media | Bajo | Búsquedas históricas precisas |
| `diario_numero` | 🟢 Baja | Bajo | Verificación de citas, correlación sumarios |

**Esfuerzo total estimado**: 1-2 horas (son parámetros simples que se añaden a la query)

### 0.6 Lo que NO Necesita Implementación (Ya Funciona)

| Capacidad | Cómo acceder | Tool |
|-----------|--------------|------|
| Obtener fecha de derogación de una norma | Campo `fecha_derogacion` en respuesta | `get_law_section("metadatos")` |
| Ver qué normas deroga/modifica una ley | `referencias.anteriores` en respuesta | `get_law_section("analisis")` |
| Ver qué normas han modificado una ley | `referencias.posteriores` en respuesta | `get_law_section("analisis")` |
| Historial de versiones de un artículo | `version[]` en bloque | `get_law_section("bloque", block_id)` |
| Códigos de tipos de relaciones | Tabla completa | `get_auxiliary_table("relaciones-anteriores/posteriores")` |

**Conclusión**: El MCP ya expone los datos necesarios para construir grafos y hacer búsquedas temporales. Solo falta mejorar los parámetros de búsqueda para facilitar el acceso.

---

## 1. Design Philosophy

### 1.1 Core Principle

> **El MCP es un cliente completo de la API del BOE, no un sistema de lógica de negocio.**

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Usuario/LLM]                                                 │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────┐                  │
│   │            BOE-MCP Server               │                  │
│   │  ┌─────────────────────────────────┐   │                  │
│   │  │   Validators (Input Security)   │   │  ← Seguridad     │
│   │  └─────────────────────────────────┘   │                  │
│   │  ┌─────────────────────────────────┐   │                  │
│   │  │   Tools (API Exposure Layer)    │   │  ← Exposición    │
│   │  └─────────────────────────────────┘   │                  │
│   │  ┌─────────────────────────────────┐   │                  │
│   │  │   HTTP Client (Transport)       │   │  ← Transporte    │
│   │  └─────────────────────────────────┘   │                  │
│   └─────────────────────────────────────────┘                  │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────┐                  │
│   │         API BOE (boe.es)                │                  │
│   │   /datosabiertos/api/...                │                  │
│   └─────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Responsibilities

| Capa | Responsabilidad | NO hace |
|------|-----------------|---------|
| **Validators** | Validar formato de inputs | Lógica de negocio |
| **Tools** | Exponer endpoints de la API | Interpretar resultados |
| **HTTP Client** | Transportar requests/responses | Transformar datos |

### 1.3 Anti-Patterns to Avoid

```
❌ INCORRECTO: Tool que determina si una ley "aplica" a un caso
✅ CORRECTO: Tool que obtiene metadatos de una ley (el consumidor decide)

❌ INCORRECTO: Tool que filtra "normas relevantes" según criterio propio
✅ CORRECTO: Tool que expone todos los filtros de la API

❌ INCORRECTO: Tool que interpreta relaciones como "esta ley es mejor"
✅ CORRECTO: Tool que devuelve relaciones tal cual las da la API

❌ INCORRECTO: Tool que calcula "vigencia efectiva" con lógica propia
✅ CORRECTO: Tool que devuelve campos de vigencia para que el consumidor calcule
```

---

## 2. API Coverage Matrix

### 2.1 Endpoints de la API BOE

Fuente: `BOE API doc/API_BOE_DOCUMENTACION_COMPLETA.md`

#### Legislación Consolidada

| Endpoint | Descripción | Formatos | Tool MCP |
|----------|-------------|----------|----------|
| `GET /legislacion-consolidada` | Lista de normas con búsqueda | JSON, XML | `search_laws` |
| `GET /legislacion-consolidada/id/{id}` | Norma completa | XML | `get_law` |
| `GET /legislacion-consolidada/id/{id}/metadatos` | Metadatos | JSON, XML | `get_law_metadata` |
| `GET /legislacion-consolidada/id/{id}/analisis` | Análisis (materias, referencias) | JSON, XML | `get_law_analysis` |
| `GET /legislacion-consolidada/id/{id}/metadata-eli` | Metadatos ELI | XML | `get_law_eli` |
| `GET /legislacion-consolidada/id/{id}/texto` | Texto consolidado completo | XML | `get_law_text` |
| `GET /legislacion-consolidada/id/{id}/texto/indice` | Índice de bloques | JSON, XML | `get_law_index` |
| `GET /legislacion-consolidada/id/{id}/texto/bloque/{id_bloque}` | Bloque específico | XML | `get_law_block` |

#### Sumarios

| Endpoint | Descripción | Formatos | Tool MCP |
|----------|-------------|----------|----------|
| `GET /boe/sumario/{fecha}` | Sumario BOE | JSON, XML | `get_boe_summary` |
| `GET /borme/sumario/{fecha}` | Sumario BORME | JSON, XML | `get_borme_summary` |

#### Tablas Auxiliares

| Endpoint | Descripción | Formatos | Tool MCP |
|----------|-------------|----------|----------|
| `GET /datos-auxiliares/materias` | Catálogo de materias | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/ambitos` | Ámbitos territoriales | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/departamentos` | Departamentos emisores | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/rangos` | Rangos normativos | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/estados-consolidacion` | Estados de consolidación | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/relaciones-anteriores` | Tipos de relaciones anteriores | JSON, XML | `get_auxiliary_table` |
| `GET /datos-auxiliares/relaciones-posteriores` | Tipos de relaciones posteriores | JSON, XML | `get_auxiliary_table` |

### 2.2 Current vs Target Coverage

| Categoría | Endpoints API | Tools Actuales | Tools Objetivo | Cobertura |
|-----------|---------------|----------------|----------------|-----------|
| Búsqueda | 1 | 1 (parcial) | 1 (completo) | 60% → 100% |
| Norma Individual | 7 | 1 (unificado) | 7 (granulares) | 100% → 100% |
| Sumarios | 2 | 2 | 2 | 100% |
| Auxiliares | 7 | 1 (unificado) | 1 (unificado) | 100% |
| **TOTAL** | **17** | **5** | **11** | **70% → 100%** |

---

## 3. Tools Specification

### 3.1 Diseño de Tools: Principios

```
1. UNA TOOL = UN ENDPOINT (o grupo lógico mínimo)
2. TODOS los parámetros de la API expuestos
3. CERO transformación de datos (passthrough)
4. Validación SOLO de formato, no de semántica
5. Errores de API propagados tal cual
```

### 3.2 Tools de Búsqueda

#### `search_laws` (Mejorada)

**Endpoint**: `GET /datosabiertos/api/legislacion-consolidada`

**Objetivo**: Exponer TODOS los parámetros de búsqueda de la API.

```python
@mcp.tool()
async def search_laws(
    # === Parámetros de paginación ===
    offset: int = 0,
    limit: int = 50,  # -1 para todos

    # === Parámetros de fecha de actualización ===
    from_date: str | None = None,  # AAAAMMDD - Fecha mínima actualización
    to_date: str | None = None,    # AAAAMMDD - Fecha máxima actualización

    # === Parámetros de query_string (campos de búsqueda) ===
    # Todos los campos permitidos por la API:
    titulo: str | None = None,
    texto: str | None = None,  # Full-text search
    numero_oficial: str | None = None,

    # === Filtros por código ===
    ambito_codigo: str | None = None,  # 1=Estatal, 2=Autonómico
    departamento_codigo: str | None = None,
    rango_codigo: str | None = None,  # 1300=Ley, 1310=LO, 1200=RD, etc.
    materia_codigo: str | None = None,
    estado_consolidacion_codigo: str | None = None,  # 3=Finalizado

    # === Filtros de vigencia ===
    vigencia_agotada: str | None = None,  # S/N

    # === Filtros de fecha (range) ===
    fecha_publicacion_desde: str | None = None,
    fecha_publicacion_hasta: str | None = None,
    fecha_disposicion_desde: str | None = None,
    fecha_disposicion_hasta: str | None = None,

    # === Ordenación ===
    sort_field: str | None = None,  # Campo por el que ordenar
    sort_order: str = "desc",  # asc/desc

    # === Formato de respuesta ===
    format: Literal["json", "xml"] = "json"

) -> dict | str:
    """
    Búsqueda de normas en la colección de Legislación Consolidada.

    Expone todos los parámetros de búsqueda de la API del BOE.
    Los resultados se devuelven tal cual los proporciona la API.

    Args:
        offset: Primer resultado a devolver (paginación)
        limit: Número máximo de resultados (-1 para todos)
        from_date: Fecha inicio última actualización (AAAAMMDD)
        to_date: Fecha fin última actualización (AAAAMMDD)
        titulo: Búsqueda en campo título
        texto: Búsqueda full-text en todo el documento
        numero_oficial: Número oficial de la norma (ej: "40/2015")
        ambito_codigo: Código de ámbito (1=Estatal, 2=Autonómico)
        departamento_codigo: Código del departamento emisor
        rango_codigo: Código del rango normativo (1300=Ley, etc.)
        materia_codigo: Código de materia temática
        estado_consolidacion_codigo: Código estado consolidación
        vigencia_agotada: Filtro vigencia (S=agotada, N=vigente)
        fecha_publicacion_desde: Fecha publicación mínima (AAAAMMDD)
        fecha_publicacion_hasta: Fecha publicación máxima (AAAAMMDD)
        fecha_disposicion_desde: Fecha disposición mínima (AAAAMMDD)
        fecha_disposicion_hasta: Fecha disposición máxima (AAAAMMDD)
        sort_field: Campo para ordenar resultados
        sort_order: Dirección de ordenación (asc/desc)
        format: Formato de respuesta (json/xml)

    Returns:
        Respuesta de la API sin transformar

    API Reference:
        Endpoint: GET /datosabiertos/api/legislacion-consolidada
        Docs: BOE API doc/APIconsolidada.md, sección 2.1
    """
```

### 3.3 Tools de Norma Individual

#### `get_law` (Norma completa)

```python
@mcp.tool()
async def get_law(
    identifier: str,
    format: Literal["xml"] = "xml"  # Solo XML disponible
) -> str:
    """
    Obtiene una norma consolidada completa.

    Incluye: metadatos + análisis + metadata-eli + texto

    Args:
        identifier: ID de la norma (ej: "BOE-A-2015-10566")
        format: Formato de respuesta (solo XML)

    Returns:
        XML completo de la norma

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}
    """
```

#### `get_law_metadata`

```python
@mcp.tool()
async def get_law_metadata(
    identifier: str,
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene los metadatos de una norma.

    Campos incluidos:
        - fecha_actualizacion, identificador
        - ambito (codigo, descripcion)
        - departamento (codigo, nombre)
        - rango (codigo, nombre)
        - fecha_disposicion, numero_oficial, titulo
        - fecha_publicacion, diario_numero
        - fecha_vigencia, vigencia_agotada
        - estatus_derogacion, fecha_derogacion
        - estatus_anulacion, fecha_anulacion
        - estado_consolidacion (codigo, descripcion)
        - url_eli, url_html_consolidada

    Args:
        identifier: ID de la norma
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/metadatos
    """
```

#### `get_law_analysis`

```python
@mcp.tool()
async def get_law_analysis(
    identifier: str,
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene el análisis de una norma (materias, notas, referencias).

    Estructura:
        - materias: Lista de materias (codigo, descripcion)
        - notas: Notas informativas
        - referencias:
            - anteriores: Normas que esta norma afecta
            - posteriores: Normas que afectan a esta

    Cada referencia incluye:
        - id_norma: Identificador de la norma relacionada
        - relacion: Tipo de relación (codigo, texto)
        - texto: Descripción de la relación

    Args:
        identifier: ID de la norma
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/analisis
    """
```

#### `get_law_eli`

```python
@mcp.tool()
async def get_law_eli(
    identifier: str
) -> str:
    """
    Obtiene los metadatos ELI (European Legislation Identifier).

    Args:
        identifier: ID de la norma

    Returns:
        XML con metadatos ELI

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/metadata-eli
        Info: https://boe.es/legislacion/eli.php
    """
```

#### `get_law_text`

```python
@mcp.tool()
async def get_law_text(
    identifier: str
) -> str:
    """
    Obtiene el texto consolidado completo de una norma.

    El texto se estructura en bloques (<bloque>), cada uno con:
        - id: Identificador del bloque
        - tipo: Tipo (precepto, preambulo, firma, etc.)
        - titulo: Título del bloque
        - versiones: Histórico de versiones del bloque

    Cada versión incluye:
        - id_norma: Norma que introdujo esta versión
        - fecha_publicacion: Fecha de la modificación
        - fecha_vigencia: Fecha de entrada en vigor
        - Contenido HTML (párrafos, tablas, imágenes)

    Args:
        identifier: ID de la norma

    Returns:
        XML con texto consolidado completo

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/texto
    """
```

#### `get_law_index`

```python
@mcp.tool()
async def get_law_index(
    identifier: str,
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene el índice de bloques de una norma.

    Cada bloque incluye:
        - id: Identificador para usar con get_law_block
        - titulo: Título del bloque
        - fecha_actualizacion: Última modificación
        - url: URL directa al bloque

    Tipos de bloque comunes:
        - pr: Preámbulo
        - a1, a2, ...: Artículos
        - da1, da2, ...: Disposiciones adicionales
        - dt1, dt2, ...: Disposiciones transitorias
        - dd: Disposición derogatoria
        - df, df1, ...: Disposiciones finales
        - fi: Firma
        - an, an1, ...: Anexos

    Args:
        identifier: ID de la norma
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/texto/indice
    """
```

#### `get_law_block`

```python
@mcp.tool()
async def get_law_block(
    identifier: str,
    block_id: str
) -> str:
    """
    Obtiene un bloque específico del texto de una norma.

    Args:
        identifier: ID de la norma (ej: "BOE-A-2015-10566")
        block_id: ID del bloque (ej: "a1", "da1", "dd")

    Returns:
        XML del bloque con todas sus versiones

    Block IDs comunes:
        - a1, a2, a100: Artículos
        - da1, da2: Disposiciones adicionales
        - dt1, dt2: Disposiciones transitorias
        - dd, dd1: Disposiciones derogatorias
        - df, df1: Disposiciones finales
        - pr: Preámbulo
        - fi: Firma
        - an, an1: Anexos

    API Reference:
        Endpoint: GET /legislacion-consolidada/id/{id}/texto/bloque/{id_bloque}
    """
```

### 3.4 Tools de Sumarios

#### `get_boe_summary` (Sin cambios funcionales)

```python
@mcp.tool()
async def get_boe_summary(
    fecha: str,
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene el sumario del BOE para una fecha.

    Estructura de respuesta:
        - metadatos: publicacion, fecha_publicacion
        - diario[]: Puede haber múltiples (extraordinarios)
            - numero: Número del diario
            - sumario_diario: ID y PDF del sumario
            - seccion[]: Secciones del BOE
                - codigo: 1, 2A, 2B, 3, 4, 5
                - nombre: Nombre de la sección
                - departamento[]: Departamentos
                    - item[]: Disposiciones/anuncios

    Secciones del BOE:
        - 1: Disposiciones generales
        - 2A: Autoridades y personal - Nombramientos
        - 2B: Autoridades y personal - Oposiciones
        - 3: Otras disposiciones
        - 4: Administración de Justicia
        - 5: Anuncios

    Args:
        fecha: Fecha del sumario (AAAAMMDD)
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /boe/sumario/{fecha}
    """
```

#### `get_borme_summary` (Sin cambios funcionales)

```python
@mcp.tool()
async def get_borme_summary(
    fecha: str,
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene el sumario del BORME para una fecha.

    Args:
        fecha: Fecha del sumario (AAAAMMDD)
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /borme/sumario/{fecha}
    """
```

### 3.5 Tools de Tablas Auxiliares

#### `get_auxiliary_table` (Sin cambios)

```python
@mcp.tool()
async def get_auxiliary_table(
    table_name: Literal[
        "materias",
        "ambitos",
        "estados-consolidacion",
        "departamentos",
        "rangos",
        "relaciones-anteriores",
        "relaciones-posteriores"
    ],
    format: Literal["json", "xml"] = "json"
) -> dict | str:
    """
    Obtiene una tabla auxiliar de códigos del BOE.

    Tablas disponibles:
        - materias: Catálogo de materias/temáticas (~3000 entradas)
        - ambitos: Ámbitos territoriales (Estatal, Autonómico)
        - estados-consolidacion: Estados de consolidación
        - departamentos: Departamentos emisores
        - rangos: Rangos normativos (Ley, RD, etc.)
        - relaciones-anteriores: Tipos de relación con normas anteriores
        - relaciones-posteriores: Tipos de relación con normas posteriores

    Cada entrada tiene:
        - codigo: Código numérico
        - descripcion: Texto descriptivo

    Args:
        table_name: Nombre de la tabla
        format: Formato de respuesta

    API Reference:
        Endpoint: GET /datos-auxiliares/{tabla}
    """
```

---

## 4. Validators Specification

### 4.1 Diseño de Validadores: Principios

```
1. Validación de FORMATO, no de SEMÁNTICA
2. Fail-fast: Validar ANTES de llamar a la API
3. Mensajes de error claros y útiles
4. Logging de intentos sospechosos (sin exponer detalles)
5. NO bloquear inputs válidos por exceso de celo
```

### 4.2 Estructura de Validadores

```
src/boe_mcp/
├── validators/
│   ├── __init__.py          # Exports públicos
│   ├── identifiers.py       # Identificadores BOE, block_ids
│   ├── dates.py             # Fechas AAAAMMDD
│   └── queries.py           # Valores de búsqueda
```

### 4.3 Especificación de Validadores

#### `validators/identifiers.py`

| Validador | Input | Validación | Ejemplo válido | Ejemplo inválido |
|-----------|-------|------------|----------------|------------------|
| `validate_boe_identifier` | string | Formato `BOE-[A\|B]-YYYY-NNNNN` | `BOE-A-2015-10566` | `BOE-2015-10566` |
| `validate_block_id` | string | Formato de bloque válido | `a1`, `da1`, `dd` | `articulo1`, `xyz` |

**Patrones de block_id válidos**:
```
a[1-9999]     → Artículos (a1, a22, a100)
da[1-99]      → Disposiciones adicionales
dt[1-99]      → Disposiciones transitorias
dd[1-9]?      → Disposiciones derogatorias (dd, dd1)
df[1-99]?     → Disposiciones finales (df, df1, df10)
pr            → Preámbulo
fi            → Firma
an[1-9]?      → Anexos (an, an1)
no            → Nota inicial
in            → Índice
```

#### `validators/dates.py`

| Validador | Input | Validación | Ejemplo válido | Ejemplo inválido |
|-----------|-------|------------|----------------|------------------|
| `validate_fecha` | string | Formato `AAAAMMDD`, fecha real | `20241125` | `20241335` |
| `validate_date_range` | from, to | from <= to | `20240101`, `20241231` | `20241231`, `20240101` |

**Reglas**:
- Año: 1960-2100 (rango razonable para API BOE)
- Mes: 01-12
- Día: Validar según mes (28/29/30/31)
- No permitir fechas futuras

#### `validators/queries.py`

| Validador | Input | Validación | Ejemplo válido | Ejemplo inválido |
|-----------|-------|------------|----------------|------------------|
| `validate_query_value` | string | Sin patrones de inyección | `procedimiento administrativo` | `") OR ("` |

**Patrones bloqueados** (mínimos, para no afectar búsquedas legítimas):
- Secuencias de paréntesis con operadores: `)\s*(OR|AND)\s*(`
- Caracteres de control: `[\x00-\x1f]`
- Wildcards excesivos: `\*{3,}`

**NO bloquear** (son búsquedas legítimas):
- Comillas simples: `Ley 40/2015, de 1 de octubre`
- Operadores en contexto: `crisis AND sanitaria` (si la API lo soporta)
- Caracteres especiales normales: `artículo 22.1.a)`

---

## 5. Implementation Phases

### 5.1 Phase 0: Validators (Foundation)

**Objetivo**: Establecer capa de seguridad de inputs.

**Entregables**:
```
src/boe_mcp/validators/
├── __init__.py
├── identifiers.py
├── dates.py
└── queries.py

tests/validators/
├── test_identifiers.py
├── test_dates.py
└── test_queries.py
```

**Duración estimada**: 2-3 horas

**Criterio de éxito**: 100% tests passing, 0 falsos positivos en inputs válidos

### 5.2 Phase 1: Search Enhancement

**Objetivo**: Exponer TODOS los parámetros de búsqueda de la API.

**Cambios en `search_laws`**:
| Parámetro | Estado actual | Acción |
|-----------|---------------|--------|
| `offset`, `limit` | ✅ | Mantener |
| `from_date`, `to_date` | ✅ | Mantener |
| `titulo` (via query_value) | ✅ | Refactorizar |
| `texto` | ⚠️ Parcial | Exponer como parámetro |
| `numero_oficial` | ❌ | Añadir |
| `ambito_codigo` | ⚠️ String | Exponer código directo |
| `departamento_codigo` | ❌ | Añadir |
| `rango_codigo` | ❌ | Añadir |
| `materia_codigo` | ❌ | Añadir |
| `estado_consolidacion_codigo` | ⚠️ Parcial | Exponer código directo |
| `vigencia_agotada` | ⚠️ Bool | Exponer S/N directo |
| `fecha_publicacion` range | ❌ | Añadir |
| `fecha_disposicion` range | ❌ | Añadir |
| `sort_field`, `sort_order` | ⚠️ Parcial | Exponer completo |

**Duración estimada**: 2-3 horas

### 5.3 Phase 2: Granular Law Tools

**Objetivo**: Separar `get_law_section` en tools específicas.

**Refactorización**:
```
ANTES:
  get_law_section(identifier, section, block_id, format)

DESPUÉS:
  get_law(identifier)           → Norma completa
  get_law_metadata(identifier)  → Solo metadatos
  get_law_analysis(identifier)  → Análisis y referencias
  get_law_eli(identifier)       → Metadatos ELI
  get_law_text(identifier)      → Texto consolidado
  get_law_index(identifier)     → Índice de bloques
  get_law_block(identifier, block_id) → Bloque específico
```

**Beneficios**:
- Cada tool tiene un propósito claro
- Documentación más específica
- Mejor descubrimiento por el LLM
- Mantener `get_law_section` como alias para compatibilidad

**Duración estimada**: 2-3 horas

### 5.4 Phase 3: Format Support

**Objetivo**: Soporte consistente de formatos JSON/XML.

**Matriz de formatos**:
| Tool | JSON | XML | Default |
|------|------|-----|---------|
| `search_laws` | ✅ | ✅ | JSON |
| `get_law` | ❌ | ✅ | XML |
| `get_law_metadata` | ✅ | ✅ | JSON |
| `get_law_analysis` | ✅ | ✅ | JSON |
| `get_law_eli` | ❌ | ✅ | XML |
| `get_law_text` | ❌ | ✅ | XML |
| `get_law_index` | ✅ | ✅ | JSON |
| `get_law_block` | ❌ | ✅ | XML |
| `get_boe_summary` | ✅ | ✅ | JSON |
| `get_borme_summary` | ✅ | ✅ | JSON |
| `get_auxiliary_table` | ✅ | ✅ | JSON |

**Duración estimada**: 1-2 horas

### 5.5 Phase 4: Documentation & Testing

**Objetivo**: Documentación completa y tests exhaustivos.

**Entregables**:
- README actualizado con ejemplos de cada tool
- Docstrings completos con referencia a API
- Tests de integración con API real
- Tests de validadores con edge cases

**Duración estimada**: 2-3 horas

---

## 6. RPVEA Workflow per Feature

### 6.1 Workflow Standard

```
┌─────────────────────────────────────────────────────────────────┐
│ R - RESEARCH (15-20 min)                                        │
├─────────────────────────────────────────────────────────────────┤
│ □ Leer documentación API del endpoint                           │
│ □ Identificar TODOS los parámetros disponibles                  │
│ □ Probar endpoint con curl/httpx                                │
│ □ Documentar estructura de respuesta                            │
│ □ Identificar edge cases (errores, límites)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ P - PREPARE (15-20 min)                                         │
├─────────────────────────────────────────────────────────────────┤
│ □ Diseñar firma de la tool                                      │
│ □ Escribir docstring con referencia a API                       │
│ □ Definir validadores necesarios                                │
│ □ Preparar test cases                                           │
│ □ PROTOTIPAR validadores en REPL                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ V - VALIDATE (20-25 min)                                        │
├─────────────────────────────────────────────────────────────────┤
│ □ V1: Validar diseño contra docs API                            │
│ □ V2: Probar con datos reales                                   │
│ □ V3: Validar patterns de validadores en REPL                   │
│                                                                 │
│ ⚠️  Si V3 falla → STOP → Volver a Research                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ E - EXECUTE (20-30 min)                                         │
├─────────────────────────────────────────────────────────────────┤
│ □ Implementar validadores                                       │
│ □ Implementar tool                                              │
│ □ Ejecutar tests unitarios                                      │
│ □ Test de integración con API                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ A - ASSESS (10-15 min)                                          │
├─────────────────────────────────────────────────────────────────┤
│ □ Actualizar README con ejemplos                                │
│ □ Actualizar CHANGELOG                                          │
│ □ Documentar lecciones aprendidas                               │
│ □ Marcar feature como completada                                │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Checklist por Feature

```markdown
## Feature: [nombre]

### R - Research
- [ ] Docs API leídos: [archivo, sección]
- [ ] Endpoint probado: `curl -X GET ...`
- [ ] Parámetros identificados: [lista]
- [ ] Estructura respuesta documentada

### P - Prepare
- [ ] Firma de tool definida
- [ ] Docstring escrito
- [ ] Validadores identificados: [lista]
- [ ] Test cases preparados: [N casos]

### V - Validate
- [ ] V1 Design review: OK/FAIL
- [ ] V2 API test: OK/FAIL
- [ ] V3 Validators REPL: OK/FAIL

### E - Execute
- [ ] Validadores implementados
- [ ] Tool implementada
- [ ] Tests passing: [N/N]
- [ ] Integration test: OK/FAIL

### A - Assess
- [ ] README actualizado
- [ ] CHANGELOG actualizado
- [ ] Lessons learned documentadas
```

---

## 7. Quality Criteria

### 7.1 Tool Quality

| Criterio | Descripción | Medición |
|----------|-------------|----------|
| **Completitud** | Todos los parámetros API expuestos | Checklist vs docs |
| **Transparencia** | Respuesta sin transformar | Diff API vs Tool |
| **Documentación** | Docstring completo con referencia | Code review |
| **Validación** | Inputs validados antes de request | Test coverage |
| **Errores** | Errores API propagados claramente | Error handling test |

### 7.2 Validator Quality

| Criterio | Descripción | Medición |
|----------|-------------|----------|
| **Precisión** | Solo bloquea inputs inválidos | False positive rate |
| **Cobertura** | Todos los formatos válidos aceptados | Test cases |
| **Claridad** | Mensajes de error útiles | User feedback |
| **Performance** | Validación rápida | Benchmark |

### 7.3 Test Coverage

| Área | Coverage mínimo | Coverage objetivo |
|------|-----------------|-------------------|
| Validadores | 95% | 100% |
| Tools (unit) | 80% | 90% |
| Integration | 70% | 85% |
| Edge cases | 90% | 100% |

---

## 8. File Structure

### 8.1 Current Structure

```
src/boe_mcp/
├── __init__.py
└── server.py          # Todo en un archivo
```

### 8.2 Target Structure

```
src/boe_mcp/
├── __init__.py
├── server.py              # Entry point + MCP setup
├── validators/
│   ├── __init__.py        # from .identifiers import *
│   ├── identifiers.py     # validate_boe_identifier, validate_block_id
│   ├── dates.py           # validate_fecha, validate_date_range
│   └── queries.py         # validate_query_value
├── tools/
│   ├── __init__.py
│   ├── search.py          # search_laws
│   ├── laws.py            # get_law, get_law_metadata, etc.
│   ├── summaries.py       # get_boe_summary, get_borme_summary
│   └── auxiliary.py       # get_auxiliary_table
└── client.py              # make_boe_request, make_boe_raw_request

tests/
├── validators/
│   ├── test_identifiers.py
│   ├── test_dates.py
│   └── test_queries.py
├── tools/
│   ├── test_search.py
│   ├── test_laws.py
│   ├── test_summaries.py
│   └── test_auxiliary.py
└── integration/
    └── test_api_integration.py
```

---

## 9. References

### 9.1 API Documentation
- `BOE API doc/API_BOE_DOCUMENTACION_COMPLETA.md` - Documentación consolidada
- `BOE API doc/APIconsolidada.md` - API Legislación Consolidada (oficial)
- `BOE API doc/APIsumarioBOE.md` - API Sumarios (oficial)

### 9.2 Testing Results
- `BOE_MCP_Testing/RESUMEN_EJECUTIVO.md` - Score 4.90/5
- `BOE_MCP_Testing/Datos_Capturados/Hallazgos/` - Limitaciones conocidas

### 9.3 Framework
- `RPVEA_ARCGIS_FRAMEWORK.md` - Framework original
- `mcp-security-kit/` - Referencia para validadores

---

**Version**: 2.0.0
**Philosophy**: Complete API Client, Zero Business Logic
**Last Updated**: 2025-11-29
