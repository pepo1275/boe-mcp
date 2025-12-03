# Plan RPVEA 2.0 - Herramientas de Navegación Inteligente v2

**Fecha:** 2025-12-03
**Versión base:** boe-mcp v1.3.0
**Rama:** `feature/smart-navigation-v2`

---

## Contexto del Problema

Al consultar el índice de leyes grandes como la Ley Concursal (BOE-A-2020-4859), la respuesta XML contiene 750+ bloques que saturan la ventana de contexto de Claude Desktop.

**Solución propuesta:** Implementar herramientas de navegación inteligente que permitan:
- **Opción A:** Paginación de resultados
- **Opción B:** Navegación jerárquica (Libros → Títulos → Capítulos → Artículos)
- **Opción C:** Caché local para análisis profundo (fase futura)
- **Opción D:** Herramientas de búsqueda específica

---

## Casos de Uso Objetivo

### Caso 1: Consulta de modificación de artículo específico
> "¿Se ha modificado el artículo 386 y cuándo fue la última vez?"

**Datos disponibles en el XML:**
```xml
<bloque>
  <id>a3-98</id>
  <titulo>Artículo 386</titulo>
  <fecha_actualizacion>20220906</fecha_actualizacion>
</bloque>
```

### Caso 2: Sistema de alertas para monitorización
> "Dado un listado de artículos, comprobar si se ha publicado alguna nueva modificación"

**Requiere:**
- Consultar `fecha_actualizacion` de múltiples artículos
- Comparar con fechas almacenadas previamente
- Detectar cambios

### Caso 3: Exploración de estructura de ley
> "¿Cómo está organizada la Ley Concursal?"

**Requiere:**
- Resumen compacto de la jerarquía
- Sin listar los 750+ artículos individuales

---

## Herramientas Propuestas

### 1. `get_law_structure_summary`

#### Responsabilidad
Devolver un resumen compacto de la estructura jerárquica de una ley (solo Libros, Títulos y Capítulos), sin incluir artículos individuales. Reduce ~750 bloques a ~30-50.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | str | Sí | - | ID BOE (ej: "BOE-A-2020-4859") |
| `nivel` | Literal["libros", "titulos", "capitulos"] | No | "capitulos" | Profundidad máxima de la estructura |

#### Valor de Retorno

```json
{
  "identifier": "BOE-A-2020-4859",
  "titulo": "TEXTO REFUNDIDO DE LA LEY CONCURSAL",
  "total_articulos": 752,
  "estructura": [
    {
      "id": "lp",
      "tipo": "libro",
      "titulo": "LIBRO PRIMERO",
      "hijos": [
        {
          "id": "ti",
          "tipo": "titulo",
          "titulo": "TÍTULO I",
          "num_articulos": 43,
          "hijos": [
            {"id": "ci", "tipo": "capitulo", "titulo": "CAPÍTULO I", "num_articulos": 2},
            {"id": "ci-2", "tipo": "capitulo", "titulo": "CAPÍTULO II", "num_articulos": 2}
          ]
        }
      ]
    }
  ]
}
```

#### Errores

| Condición | Mensaje |
|-----------|---------|
| Identificador inválido | `ValidationError: Identificador BOE inválido` |
| Ley no encontrada | `No se pudo recuperar la estructura de {identifier}` |
| Error de parsing XML | `Error procesando estructura de la ley` |

#### Algoritmo

1. Validar `identifier` con `validate_boe_identifier()`
2. Llamar a `get_law_section(identifier, "indice", format="xml")`
3. Parsear XML con `xml.etree.ElementTree`
4. Filtrar bloques estructurales por prefijo de ID:
   - `lp|ls` → Libro
   - `ti` → Título
   - `ci|cv` → Capítulo
   - `s` → Sección (opcional según nivel)
5. Construir árbol jerárquico basado en orden de aparición
6. Contar artículos por rama (bloques con prefijo `a`)
7. Devolver estructura JSON compacta

---

### 2. `get_article_info`

#### Responsabilidad
Obtener información detallada de un artículo específico, incluyendo su fecha de última modificación y si fue modificado respecto a la versión original de la ley.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | str | Sí | - | ID BOE de la ley |
| `articulo` | str | Sí | - | Número del artículo (ej: "386", "224 bis", "37 quater") |
| `incluir_texto` | bool | No | False | Si incluir el texto completo del artículo |

#### Valor de Retorno

```json
{
  "identifier": "BOE-A-2020-4859",
  "articulo": "386",
  "block_id": "a3-98",
  "titulo_completo": "Artículo 386. Legitimación",
  "fecha_actualizacion": "20220906",
  "fecha_ley_original": "20200507",
  "modificado": true,
  "dias_desde_modificacion": 819,
  "ubicacion": {
    "libro": "LIBRO TERCERO",
    "titulo": "TÍTULO II",
    "capitulo": "CAPÍTULO I",
    "seccion": "Sección 1"
  },
  "url_bloque": "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/BOE-A-2020-4859/texto/bloque/a3-98",
  "texto": "1. Están legitimados para..."
}
```

**Nota:** `texto` solo se incluye si `incluir_texto=True`

#### Errores

| Condición | Mensaje |
|-----------|---------|
| Artículo no encontrado | `No se encontró el artículo {articulo} en {identifier}` |
| Número de artículo inválido | `ValidationError: Formato de artículo inválido` |
| Identificador inválido | `ValidationError: Identificador BOE inválido` |

#### Algoritmo

1. Validar `identifier` con `validate_boe_identifier()`
2. Validar formato de `articulo` (números, "bis", "ter", etc.)
3. Obtener índice completo de la ley
4. Buscar bloque cuyo título coincida con "Artículo {articulo}"
   - Normalizar búsqueda: "386" debe encontrar "Artículo 386" o "Artículo 386. Título"
5. Extraer `fecha_actualizacion` del bloque encontrado
6. Obtener `fecha_ley_original` de los metadatos de la ley (primera publicación)
7. Determinar `modificado = fecha_actualizacion > fecha_ley_original`
8. Reconstruir ubicación jerárquica recorriendo bloques anteriores
9. Si `incluir_texto=True`:
   - Llamar a `get_law_section(identifier, "bloque", block_id)`
   - Extraer texto del XML
10. Devolver objeto con toda la información

---

### 3. `search_in_law`

#### Responsabilidad
Buscar artículos dentro de una ley que coincidan con criterios específicos: por número, por texto en título, o por estado de modificación.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | str | Sí | - | ID BOE de la ley |
| `query` | str | No | None | Texto a buscar en títulos de artículos |
| `articulos` | list[str] | No | None | Lista de números de artículos específicos |
| `solo_modificados` | bool | No | False | Filtrar solo artículos modificados |
| `modificados_desde` | str | No | None | Fecha mínima de modificación (AAAAMMDD) |
| `modificados_hasta` | str | No | None | Fecha máxima de modificación (AAAAMMDD) |
| `limit` | int | No | 50 | Máximo de resultados a devolver |
| `offset` | int | No | 0 | Índice inicial para paginación |

**Validación:** Debe proporcionarse al menos uno de: `query`, `articulos`, `solo_modificados`, `modificados_desde`

#### Valor de Retorno

```json
{
  "identifier": "BOE-A-2020-4859",
  "criterios": {
    "solo_modificados": true,
    "modificados_desde": "20220101"
  },
  "total_encontrados": 125,
  "offset": 0,
  "limit": 50,
  "hay_mas": true,
  "resultados": [
    {
      "articulo": "1",
      "block_id": "a1",
      "titulo": "Artículo 1. Presupuesto objetivo",
      "fecha_actualizacion": "20220906",
      "modificado": true
    },
    {
      "articulo": "2",
      "block_id": "a2",
      "titulo": "Artículo 2. Presupuesto subjetivo",
      "fecha_actualizacion": "20220906",
      "modificado": true
    }
  ]
}
```

#### Errores

| Condición | Mensaje |
|-----------|---------|
| Sin criterios de búsqueda | `Debe proporcionar al menos un criterio: query, articulos, solo_modificados o modificados_desde` |
| Fecha inválida | `ValidationError: Formato de fecha inválido` |
| Rango de fechas inválido | `ValidationError: modificados_desde no puede ser posterior a modificados_hasta` |

#### Algoritmo

1. Validar que existe al menos un criterio de búsqueda
2. Validar `identifier` y fechas si se proporcionan
3. Obtener índice completo de la ley (XML)
4. Obtener `fecha_ley_original` de metadatos
5. Filtrar bloques de tipo artículo (título empieza con "Artículo")
6. Aplicar filtros en orden:
   - Si `articulos`: filtrar por números en la lista
   - Si `query`: filtrar por coincidencia en título (case-insensitive)
   - Si `solo_modificados`: filtrar donde `fecha_actualizacion > fecha_ley_original`
   - Si `modificados_desde`: filtrar donde `fecha_actualizacion >= modificados_desde`
   - Si `modificados_hasta`: filtrar donde `fecha_actualizacion <= modificados_hasta`
7. Contar total antes de paginar
8. Aplicar `offset` y `limit`
9. Devolver resultados con metadatos de paginación

---

### 4. `get_law_index`

#### Responsabilidad
Obtener el índice de una ley con soporte para paginación y filtrado por tipo de bloque. Versión mejorada de `get_law_section(..., section="indice")`.

#### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `identifier` | str | Sí | - | ID BOE de la ley |
| `tipo_bloque` | Literal["todos", "estructura", "articulos", "disposiciones"] | No | "todos" | Tipo de bloques a incluir |
| `limit` | int | No | 100 | Máximo de resultados |
| `offset` | int | No | 0 | Índice inicial |

**Tipos de bloque:**
- `todos`: Sin filtro
- `estructura`: Solo libros, títulos, capítulos, secciones
- `articulos`: Solo artículos (prefijo `a` en id)
- `disposiciones`: Adicionales, transitorias, derogatorias, finales (prefijos `da`, `dt`, `dd`, `df`)

#### Valor de Retorno

```json
{
  "identifier": "BOE-A-2020-4859",
  "tipo_bloque": "articulos",
  "total_bloques": 752,
  "offset": 0,
  "limit": 100,
  "hay_mas": true,
  "bloques": [
    {
      "id": "a1",
      "titulo": "Artículo 1. Presupuesto objetivo",
      "fecha_actualizacion": "20220906",
      "url": "https://www.boe.es/datosabiertos/api/..."
    }
  ]
}
```

#### Errores

| Condición | Mensaje |
|-----------|---------|
| Identificador inválido | `ValidationError: Identificador BOE inválido` |
| Ley no encontrada | `No se pudo recuperar el índice de {identifier}` |
| tipo_bloque inválido | `ValidationError: tipo_bloque debe ser uno de: todos, estructura, articulos, disposiciones` |

#### Algoritmo

1. Validar `identifier` y `tipo_bloque`
2. Obtener índice XML completo
3. Parsear todos los bloques
4. Filtrar según `tipo_bloque`:
   - `estructura`: IDs que empiezan con `lp|ls|ti|ci|cv|s` (no seguido de número)
   - `articulos`: IDs que empiezan con `a`
   - `disposiciones`: IDs que empiezan con `da|dt|dd|df`
   - `todos`: sin filtro
5. Contar total
6. Aplicar paginación
7. Devolver con metadatos

---

## Mapeo Herramientas → Casos de Uso

| Caso de Uso | Herramienta Principal | Herramientas de Apoyo |
|-------------|----------------------|----------------------|
| "¿Se ha modificado el artículo 386?" | `get_article_info` | - |
| "¿Cuándo fue la última modificación del art. 386?" | `get_article_info` | - |
| "Dame los artículos modificados desde 2022" | `search_in_law(modificados_desde="20220101")` | - |
| "Explorar estructura de la Ley Concursal" | `get_law_structure_summary` | - |
| "Listar todos los artículos (paginado)" | `get_law_index(tipo_bloque="articulos")` | - |
| "Monitorizar lista de artículos específicos" | `search_in_law(articulos=["1","2","386"])` | Caché local (futuro) |
| "Buscar artículos sobre 'legitimación'" | `search_in_law(query="legitimación")` | - |

---

## Orden de Implementación Propuesto

### Fase 1: Fundamentos (cubre Caso 1)
1. **`get_article_info`** - Permite consultar si un artículo específico fue modificado

### Fase 2: Búsqueda (cubre Caso 2)
2. **`search_in_law`** - Permite búsquedas múltiples y filtros por modificación

### Fase 3: Navegación (cubre Caso 3)
3. **`get_law_structure_summary`** - Exploración de estructura sin saturar contexto
4. **`get_law_index`** - Índice paginado como fallback

### Fase 4: Caché Local (futuro)
5. Sistema de almacenamiento local para alertas y monitorización continua

---

## Consideraciones Técnicas

### Parsing del XML del Índice
El XML del índice tiene estructura plana (no anidada). La jerarquía se infiere por:
1. Orden de aparición de los bloques
2. Prefijos de ID:
   - `no` - Nota
   - `pr` - Preámbulo
   - `au` - Artículo único
   - `te` - Texto (título principal)
   - `lp|ls` - Libro
   - `ti` - Título
   - `ci|cv` - Capítulo
   - `s` - Sección/Subsección
   - `a` - Artículo
   - `da` - Disposición adicional
   - `dt` - Disposición transitoria
   - `dd` - Disposición derogatoria
   - `df` - Disposición final
   - `fi` - Firma

### Determinación de Modificación
- `fecha_ley_original`: Se obtiene de los metadatos de la ley (fecha de publicación inicial)
- `modificado = fecha_actualizacion > fecha_ley_original`
- Ejemplo: Ley Concursal publicada `20200507`, artículo con `fecha_actualizacion=20220906` → modificado=true

### Validadores Necesarios
- `validate_boe_identifier()` - Ya existe en v1.3.0
- `validate_articulo()` - **Nuevo**: validar formato "386", "224 bis", "37 quater"
- `validate_fecha()` - Ya existe en v1.3.0

---

## Preguntas Abiertas

1. **¿Incluir secciones en `get_law_structure_summary`?**
   - Pro: Más detalle
   - Contra: Más bloques en respuesta

2. **¿Límite máximo para `search_in_law`?**
   - Propuesta: limit máximo = 200

3. **¿Cachear índice en memoria durante sesión?**
   - Evitaría múltiples llamadas a la API para la misma ley
   - Complejidad adicional

4. **¿Formato de salida alternativo (markdown resumido)?**
   - Para casos donde JSON sea demasiado verboso

---

## Referencias

- API BOE Datos Abiertos: https://www.boe.es/datosabiertos/
- Ejemplo de ley grande: BOE-A-2020-4859 (Ley Concursal, 752 artículos)
- Versión base: boe-mcp v1.3.0
