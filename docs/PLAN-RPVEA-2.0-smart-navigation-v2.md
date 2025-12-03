# Plan RPVEA 2.0 Estricto - Smart Navigation v2

**Fecha:** 2025-12-03
**Versión base:** boe-mcp v1.3.0
**Rama:** `feature/smart-navigation-v2`
**Autor:** Claude + Usuario

---

## Resumen Ejecutivo

Implementar herramientas de navegación inteligente que procesen localmente las respuestas de la API BOE para reducir el consumo de tokens (30-50x) y permitir casos de uso como:
- Consultar si un artículo específico fue modificado
- Buscar artículos modificados en un rango de fechas
- Explorar la estructura jerárquica de una ley sin saturar contexto

---

## Decisión Arquitectónica

**Opción elegida:** MCP + Utilidades de procesamiento (Opción 3)

**Justificación:**
1. Más rápido de implementar (infraestructura existente)
2. Ahorro de tokens: ~500 tokens vs ~30,000 tokens por consulta
3. Rama separada mantiene MCP puro en `master`

---

# HERRAMIENTA 1: `get_article_info`

## R - Responsabilidad

Obtener información detallada de un artículo específico de una ley consolidada, incluyendo:
- Fecha de última modificación
- Si fue modificado respecto a la versión original
- Ubicación jerárquica dentro de la ley
- Opcionalmente, el texto completo

### Tests PRE (Fase R) - Verificar comprensión del requisito

| ID | Test | Input | Output Esperado | Estado |
|----|------|-------|-----------------|--------|
| R1.1 | Artículo simple existe | `BOE-A-2020-4859`, `articulo="1"` | Info del Artículo 1 | Pendiente |
| R1.2 | Artículo con número alto | `BOE-A-2020-4859`, `articulo="386"` | Info del Artículo 386 | Pendiente |
| R1.3 | Artículo con sufijo latino | `BOE-A-2020-4859`, `articulo="224 bis"` | Info del Artículo 224 bis | Pendiente |
| R1.4 | Artículo no existente | `BOE-A-2020-4859`, `articulo="9999"` | Error: no encontrado | Pendiente |
| R1.5 | Ley no existente | `BOE-A-0000-0000`, `articulo="1"` | Error: ley no encontrada | Pendiente |
| R1.6 | Con texto incluido | `articulo="1"`, `incluir_texto=True` | Info + campo texto | Pendiente |
| R1.7 | Sin texto (default) | `articulo="1"` | Info sin campo texto | Pendiente |

---

## P - Parámetros

| Parámetro | Tipo | Requerido | Default | Validador | Descripción |
|-----------|------|-----------|---------|-----------|-------------|
| `identifier` | str | Sí | - | `validate_boe_identifier()` | ID BOE de la ley |
| `articulo` | str | Sí | - | `validate_articulo()` **NUEVO** | Número del artículo |
| `incluir_texto` | bool | No | False | built-in | Incluir texto completo |

### Validador nuevo: `validate_articulo()`

**Ubicación:** `src/boe_mcp/validators/articles.py`

**Patrones válidos:**
- Números simples: `"1"`, `"386"`, `"1234"`
- Con sufijos latinos: `"224 bis"`, `"37 ter"`, `"37 quater"`, `"37 quinquies"`, `"37 sexies"`, `"37 septies"`
- Artículo único: `"único"`

**Regex:** `^(\d{1,4}(\s+(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies))?|único)$`

**Tests del validador:**

| ID | Input | Output | Descripción |
|----|-------|--------|-------------|
| V1.1 | `"1"` | `"1"` | Número simple |
| V1.2 | `"386"` | `"386"` | Número alto |
| V1.3 | `"224 bis"` | `"224 bis"` | Con sufijo bis |
| V1.4 | `"37 quater"` | `"37 quater"` | Con sufijo quater |
| V1.5 | `"único"` | `"único"` | Artículo único |
| V1.6 | `"  386  "` | `"386"` | Whitespace stripped |
| V1.7 | `"ÚNICO"` | `"único"` | Normalizado a minúscula |
| V1.8 | `""` | ValidationError | Vacío rechazado |
| V1.9 | `None` | ValidationError | None rechazado |
| V1.10 | `"abc"` | ValidationError | Texto inválido |
| V1.11 | `"-1"` | ValidationError | Negativo rechazado |
| V1.12 | `"1; DROP TABLE"` | ValidationError | Inyección bloqueada |
| V1.13 | `"../../../etc"` | ValidationError | Path traversal bloqueado |

---

## V - Valor de Retorno

### Estructura de éxito

```python
{
    "identifier": str,           # "BOE-A-2020-4859"
    "articulo": str,             # "386"
    "block_id": str,             # "a3-98"
    "titulo_completo": str,      # "Artículo 386. Legitimación"
    "fecha_actualizacion": str,  # "20220906"
    "fecha_ley_original": str,   # "20200507"
    "modificado": bool,          # True
    "ubicacion": {
        "libro": str | None,     # "LIBRO TERCERO"
        "titulo": str | None,    # "TÍTULO II"
        "capitulo": str | None,  # "CAPÍTULO I"
        "seccion": str | None    # "Sección 1" o None
    },
    "url_bloque": str,           # URL completa del bloque
    "texto": str | None          # Solo si incluir_texto=True
}
```

### Estructura de error

```python
{
    "error": True,
    "codigo": str,               # "ARTICULO_NO_ENCONTRADO" | "LEY_NO_ENCONTRADA" | "VALIDATION_ERROR"
    "mensaje": str,              # Descripción legible
    "detalles": dict | None      # Info adicional
}
```

---

## E - Errores

| Código | Condición | Mensaje | HTTP equiv |
|--------|-----------|---------|------------|
| `VALIDATION_ERROR` | Parámetros inválidos | Detalle del validador | 400 |
| `LEY_NO_ENCONTRADA` | Identifier no existe en BOE | `No se pudo recuperar la ley {identifier}` | 404 |
| `ARTICULO_NO_ENCONTRADO` | Artículo no existe en la ley | `No se encontró el artículo {articulo} en {identifier}` | 404 |
| `ERROR_PARSING` | XML malformado | `Error procesando respuesta de la API` | 500 |
| `API_ERROR` | Error de conexión/timeout | `Error de comunicación con la API BOE` | 503 |

---

## A - Algoritmo

```
FUNCIÓN get_article_info(identifier, articulo, incluir_texto=False):

    # 1. VALIDACIÓN
    identifier = validate_boe_identifier(identifier)
    articulo = validate_articulo(articulo)

    # 2. OBTENER ÍNDICE
    indice_xml = await get_law_section(identifier, "indice", format="xml")
    SI indice_xml es None:
        RETORNAR error LEY_NO_ENCONTRADA

    # 3. PARSEAR XML
    INTENTAR:
        root = ET.fromstring(indice_xml)
        bloques = root.findall(".//bloque")
    EXCEPTO:
        RETORNAR error ERROR_PARSING

    # 4. BUSCAR ARTÍCULO
    patron_titulo = f"Artículo {articulo}" (case-insensitive)
    bloque_encontrado = None

    PARA cada bloque EN bloques:
        titulo = bloque.find("titulo").text
        SI titulo empieza con patron_titulo:
            bloque_encontrado = bloque
            ROMPER

    SI bloque_encontrado es None:
        RETORNAR error ARTICULO_NO_ENCONTRADO

    # 5. EXTRAER DATOS DEL BLOQUE
    block_id = bloque_encontrado.find("id").text
    titulo_completo = bloque_encontrado.find("titulo").text
    fecha_actualizacion = bloque_encontrado.find("fecha_actualizacion").text
    url_bloque = bloque_encontrado.find("url").text

    # 6. OBTENER FECHA ORIGINAL DE LA LEY
    # La fecha más antigua entre todos los bloques es la fecha original
    fecha_ley_original = MIN(b.find("fecha_actualizacion").text PARA b EN bloques)

    # 7. DETERMINAR SI FUE MODIFICADO
    modificado = fecha_actualizacion > fecha_ley_original

    # 8. RECONSTRUIR UBICACIÓN JERÁRQUICA
    ubicacion = reconstruir_ubicacion(bloques, bloque_encontrado)

    # 9. OBTENER TEXTO SI SE SOLICITA
    texto = None
    SI incluir_texto:
        texto_xml = await get_law_section(identifier, "bloque", block_id)
        texto = extraer_texto_de_bloque(texto_xml)

    # 10. RETORNAR RESULTADO
    RETORNAR {
        identifier, articulo, block_id, titulo_completo,
        fecha_actualizacion, fecha_ley_original, modificado,
        ubicacion, url_bloque, texto
    }


FUNCIÓN reconstruir_ubicacion(bloques, bloque_objetivo):
    """
    Recorre los bloques anteriores al objetivo para encontrar
    la jerarquía: libro → título → capítulo → sección
    """
    ubicacion = {libro: None, titulo: None, capitulo: None, seccion: None}

    PARA i, bloque EN enumerar(bloques):
        SI bloque == bloque_objetivo:
            ROMPER

        id_bloque = bloque.find("id").text
        titulo_bloque = bloque.find("titulo").text

        SI id_bloque empieza con "lp" o "ls":
            ubicacion.libro = titulo_bloque
            ubicacion.titulo = None  # Reset niveles inferiores
            ubicacion.capitulo = None
            ubicacion.seccion = None
        SINO SI id_bloque empieza con "ti":
            ubicacion.titulo = titulo_bloque
            ubicacion.capitulo = None
            ubicacion.seccion = None
        SINO SI id_bloque empieza con "ci" o "cv":
            ubicacion.capitulo = titulo_bloque
            ubicacion.seccion = None
        SINO SI id_bloque empieza con "s" y NO empieza con artículo:
            ubicacion.seccion = titulo_bloque

    RETORNAR ubicacion
```

---

## Tests POST (Criterios de Aceptación)

### Tests Unitarios

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| U1.1 | Artículo 1 de Ley Concursal | `BOE-A-2020-4859`, `"1"` | `articulo="1"`, `modificado=True`, `fecha_actualizacion="20220906"` |
| U1.2 | Artículo 386 ubicación correcta | `BOE-A-2020-4859`, `"386"` | `ubicacion.libro="LIBRO TERCERO"` |
| U1.3 | Artículo 224 bis existe | `BOE-A-2020-4859`, `"224 bis"` | `articulo="224 bis"`, `block_id` válido |
| U1.4 | Artículo inexistente | `BOE-A-2020-4859`, `"9999"` | `error=True`, `codigo="ARTICULO_NO_ENCONTRADO"` |
| U1.5 | Identifier inválido | `"INVALIDO"`, `"1"` | `error=True`, `codigo="VALIDATION_ERROR"` |
| U1.6 | Artículo inválido | `BOE-A-2020-4859`, `"abc"` | `error=True`, `codigo="VALIDATION_ERROR"` |
| U1.7 | Con texto | `BOE-A-2020-4859`, `"1"`, `incluir_texto=True` | `texto` no es None |
| U1.8 | Sin texto (default) | `BOE-A-2020-4859`, `"1"` | `texto` es None |

### Tests de Integración (E2E)

| ID | Descripción | Verificación |
|----|-------------|--------------|
| E1.1 | Llamada real a API BOE | Respuesta exitosa con datos reales |
| E1.2 | Timeout de API manejado | Error API_ERROR retornado |
| E1.3 | Ley grande (752 arts) procesada | Respuesta en < 5 segundos |

### Tests de Seguridad

| ID | Descripción | Input | Output |
|----|-------------|-------|--------|
| S1.1 | Path traversal en identifier | `"../../../etc/passwd"`, `"1"` | ValidationError |
| S1.2 | Inyección en articulo | `"1; DROP TABLE"` | ValidationError |
| S1.3 | Null byte en articulo | `"1\x00"` | ValidationError |

---

# HERRAMIENTA 2: `search_in_law`

## R - Responsabilidad

Buscar artículos dentro de una ley que coincidan con criterios específicos:
- Por lista de números de artículo
- Por texto en el título
- Por estado de modificación
- Por rango de fechas de modificación

### Tests PRE (Fase R)

| ID | Test | Input | Output Esperado |
|----|------|-------|-----------------|
| R2.1 | Buscar artículos modificados | `solo_modificados=True` | Lista de artículos con `modificado=True` |
| R2.2 | Buscar por lista de artículos | `articulos=["1","2","386"]` | Info de esos 3 artículos |
| R2.3 | Buscar por texto en título | `query="legitimación"` | Artículos con "legitimación" en título |
| R2.4 | Buscar modificados desde fecha | `modificados_desde="20220101"` | Artículos modificados desde esa fecha |
| R2.5 | Sin criterios | (ninguno) | Error: debe proporcionar criterio |
| R2.6 | Paginación funciona | `limit=10`, `offset=0` | 10 primeros resultados |

---

## P - Parámetros

| Parámetro | Tipo | Requerido | Default | Validador | Descripción |
|-----------|------|-----------|---------|-----------|-------------|
| `identifier` | str | Sí | - | `validate_boe_identifier()` | ID BOE de la ley |
| `query` | str | No | None | `validate_query_value()` | Texto a buscar en títulos |
| `articulos` | list[str] | No | None | `validate_articulo()` cada uno | Lista de números de artículos |
| `solo_modificados` | bool | No | False | built-in | Solo artículos modificados |
| `modificados_desde` | str | No | None | `validate_fecha()` | Fecha mínima modificación |
| `modificados_hasta` | str | No | None | `validate_fecha()` | Fecha máxima modificación |
| `limit` | int | No | 50 | 1-200 | Máximo resultados |
| `offset` | int | No | 0 | >= 0 | Índice inicial |

**Validación especial:** Al menos uno de `query`, `articulos`, `solo_modificados`, `modificados_desde` debe estar presente.

---

## V - Valor de Retorno

### Estructura de éxito

```python
{
    "identifier": str,
    "criterios": {
        "query": str | None,
        "articulos": list[str] | None,
        "solo_modificados": bool,
        "modificados_desde": str | None,
        "modificados_hasta": str | None
    },
    "total_encontrados": int,
    "offset": int,
    "limit": int,
    "hay_mas": bool,
    "resultados": [
        {
            "articulo": str,
            "block_id": str,
            "titulo": str,
            "fecha_actualizacion": str,
            "modificado": bool
        }
    ]
}
```

---

## E - Errores

| Código | Condición | Mensaje |
|--------|-----------|---------|
| `VALIDATION_ERROR` | Parámetros inválidos | Detalle del validador |
| `SIN_CRITERIOS` | Ningún criterio de búsqueda | `Debe proporcionar al menos un criterio: query, articulos, solo_modificados o modificados_desde` |
| `LEY_NO_ENCONTRADA` | Identifier no existe | `No se pudo recuperar la ley {identifier}` |
| `RANGO_FECHAS_INVALIDO` | desde > hasta | `modificados_desde no puede ser posterior a modificados_hasta` |

---

## A - Algoritmo

```
FUNCIÓN search_in_law(identifier, query, articulos, solo_modificados,
                      modificados_desde, modificados_hasta, limit, offset):

    # 1. VALIDACIÓN
    identifier = validate_boe_identifier(identifier)

    SI query: query = validate_query_value(query)
    SI articulos: articulos = [validate_articulo(a) PARA a EN articulos]
    SI modificados_desde: modificados_desde = validate_fecha(modificados_desde)
    SI modificados_hasta: modificados_hasta = validate_fecha(modificados_hasta)

    SI modificados_desde Y modificados_hasta Y modificados_desde > modificados_hasta:
        RETORNAR error RANGO_FECHAS_INVALIDO

    # Validar que hay al menos un criterio
    SI NO (query O articulos O solo_modificados O modificados_desde):
        RETORNAR error SIN_CRITERIOS

    # Validar límites
    limit = MIN(MAX(limit, 1), 200)
    offset = MAX(offset, 0)

    # 2. OBTENER ÍNDICE
    indice_xml = await get_law_section(identifier, "indice")
    SI indice_xml es None:
        RETORNAR error LEY_NO_ENCONTRADA

    # 3. PARSEAR Y FILTRAR
    root = ET.fromstring(indice_xml)
    bloques = root.findall(".//bloque")

    # Obtener fecha original
    fecha_ley_original = MIN(b.find("fecha_actualizacion").text PARA b EN bloques)

    # Filtrar solo artículos
    articulos_bloques = [b PARA b EN bloques SI b.find("titulo").text empieza con "Artículo"]

    # 4. APLICAR FILTROS
    resultados = []

    PARA bloque EN articulos_bloques:
        titulo = bloque.find("titulo").text
        fecha_act = bloque.find("fecha_actualizacion").text
        num_articulo = extraer_numero_articulo(titulo)
        es_modificado = fecha_act > fecha_ley_original

        # Filtro por lista de artículos
        SI articulos Y num_articulo NO EN articulos:
            CONTINUAR

        # Filtro por query
        SI query Y query.lower() NO EN titulo.lower():
            CONTINUAR

        # Filtro por modificados
        SI solo_modificados Y NO es_modificado:
            CONTINUAR

        # Filtro por fecha desde
        SI modificados_desde Y fecha_act < modificados_desde:
            CONTINUAR

        # Filtro por fecha hasta
        SI modificados_hasta Y fecha_act > modificados_hasta:
            CONTINUAR

        resultados.append({
            articulo: num_articulo,
            block_id: bloque.find("id").text,
            titulo: titulo,
            fecha_actualizacion: fecha_act,
            modificado: es_modificado
        })

    # 5. PAGINAR
    total = len(resultados)
    resultados_paginados = resultados[offset:offset+limit]
    hay_mas = (offset + limit) < total

    # 6. RETORNAR
    RETORNAR {
        identifier, criterios, total_encontrados: total,
        offset, limit, hay_mas, resultados: resultados_paginados
    }
```

---

## Tests POST (Criterios de Aceptación)

### Tests Unitarios

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| U2.1 | Buscar modificados | `solo_modificados=True` | `total_encontrados > 0`, todos con `modificado=True` |
| U2.2 | Buscar lista específica | `articulos=["1","2"]` | Exactamente 2 resultados |
| U2.3 | Buscar por query | `query="legitimación"` | Resultados contienen "legitimación" |
| U2.4 | Filtro fecha desde | `modificados_desde="20220101"` | Todos con fecha >= 20220101 |
| U2.5 | Filtro fecha hasta | `modificados_hasta="20210101"` | Todos con fecha <= 20210101 |
| U2.6 | Combinación filtros | `solo_modificados=True`, `query="concurso"` | Ambos criterios aplicados |
| U2.7 | Paginación offset | `limit=10`, `offset=10` | Resultados 11-20 |
| U2.8 | hay_mas correcto | `limit=10` con 50 resultados | `hay_mas=True` |
| U2.9 | Sin criterios | (ninguno) | Error SIN_CRITERIOS |
| U2.10 | Rango fechas inválido | `desde="20221231"`, `hasta="20220101"` | Error RANGO_FECHAS_INVALIDO |

---

# HERRAMIENTA 3: `get_law_structure_summary`

## R - Responsabilidad

Devolver un resumen compacto de la estructura jerárquica de una ley (Libros, Títulos, Capítulos), sin incluir artículos individuales.

### Tests PRE (Fase R)

| ID | Test | Input | Output Esperado |
|----|------|-------|-----------------|
| R3.1 | Estructura de Ley Concursal | `BOE-A-2020-4859` | Estructura con 3 libros |
| R3.2 | Nivel libros solo | `nivel="libros"` | Solo libros, sin títulos |
| R3.3 | Nivel títulos | `nivel="titulos"` | Libros + títulos |
| R3.4 | Nivel capítulos (default) | (sin nivel) | Libros + títulos + capítulos |
| R3.5 | Ley sin libros | Ley simple | Estructura adaptada |

---

## P - Parámetros

| Parámetro | Tipo | Requerido | Default | Validador | Descripción |
|-----------|------|-----------|---------|-----------|-------------|
| `identifier` | str | Sí | - | `validate_boe_identifier()` | ID BOE de la ley |
| `nivel` | Literal["libros", "titulos", "capitulos"] | No | "capitulos" | built-in | Profundidad máxima |

---

## V - Valor de Retorno

```python
{
    "identifier": str,
    "titulo": str,                    # Título de la ley
    "fecha_publicacion": str,         # Fecha original
    "total_articulos": int,           # Conteo de artículos
    "total_modificados": int,         # Artículos modificados
    "estructura": [
        {
            "id": str,
            "tipo": "libro" | "titulo" | "capitulo",
            "titulo": str,
            "num_articulos": int,
            "num_modificados": int,
            "hijos": [...]            # Recursivo según nivel
        }
    ]
}
```

---

## E - Errores

| Código | Condición | Mensaje |
|--------|-----------|---------|
| `VALIDATION_ERROR` | Parámetros inválidos | Detalle del validador |
| `LEY_NO_ENCONTRADA` | Identifier no existe | `No se pudo recuperar la ley {identifier}` |
| `NIVEL_INVALIDO` | nivel no es uno de los permitidos | `nivel debe ser: libros, titulos o capitulos` |

---

## A - Algoritmo

```
FUNCIÓN get_law_structure_summary(identifier, nivel="capitulos"):

    # 1. VALIDACIÓN
    identifier = validate_boe_identifier(identifier)
    SI nivel NO EN ["libros", "titulos", "capitulos"]:
        RETORNAR error NIVEL_INVALIDO

    # 2. OBTENER ÍNDICE
    indice_xml = await get_law_section(identifier, "indice")
    SI indice_xml es None:
        RETORNAR error LEY_NO_ENCONTRADA

    # 3. PARSEAR BLOQUES
    root = ET.fromstring(indice_xml)
    bloques = root.findall(".//bloque")

    # 4. CLASIFICAR BLOQUES
    fecha_original = MIN(b.fecha_actualizacion PARA b EN bloques)

    estructura = []
    libro_actual = None
    titulo_actual = None
    capitulo_actual = None

    PARA bloque EN bloques:
        id = bloque.find("id").text
        titulo = bloque.find("titulo").text
        fecha = bloque.find("fecha_actualizacion").text

        SI es_libro(id):  # lp, ls
            libro_actual = crear_nodo("libro", id, titulo)
            estructura.append(libro_actual)
            titulo_actual = None
            capitulo_actual = None

        SINO SI es_titulo(id) Y nivel EN ["titulos", "capitulos"]:  # ti
            titulo_actual = crear_nodo("titulo", id, titulo)
            SI libro_actual:
                libro_actual.hijos.append(titulo_actual)
            SINO:
                estructura.append(titulo_actual)
            capitulo_actual = None

        SINO SI es_capitulo(id) Y nivel == "capitulos":  # ci, cv
            capitulo_actual = crear_nodo("capitulo", id, titulo)
            SI titulo_actual:
                titulo_actual.hijos.append(capitulo_actual)
            SINO SI libro_actual:
                libro_actual.hijos.append(capitulo_actual)
            SINO:
                estructura.append(capitulo_actual)

        SINO SI es_articulo(id):  # a
            es_modificado = fecha > fecha_original
            incrementar_contadores(libro_actual, titulo_actual, capitulo_actual, es_modificado)

    # 5. CALCULAR TOTALES
    total_articulos = contar_articulos(bloques)
    total_modificados = contar_modificados(bloques, fecha_original)

    # 6. OBTENER TÍTULO DE LA LEY
    titulo_ley = extraer_titulo_ley(bloques)  # Bloque con id="te"

    RETORNAR {
        identifier, titulo: titulo_ley, fecha_publicacion: fecha_original,
        total_articulos, total_modificados, estructura
    }
```

---

## Tests POST (Criterios de Aceptación)

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| U3.1 | Estructura Ley Concursal | `BOE-A-2020-4859` | 3 libros en estructura |
| U3.2 | Conteo artículos correcto | `BOE-A-2020-4859` | `total_articulos` ~ 750 |
| U3.3 | Nivel libros | `nivel="libros"` | Sin hijos en libros |
| U3.4 | Nivel titulos | `nivel="titulos"` | Libros con títulos, sin capítulos |
| U3.5 | num_articulos por libro | default | Cada libro tiene `num_articulos > 0` |
| U3.6 | num_modificados calculado | default | `total_modificados > 0` |

---

# HERRAMIENTA 4: `get_law_index`

## R - Responsabilidad

Obtener el índice de una ley con soporte para paginación y filtrado por tipo de bloque.

### Tests PRE (Fase R)

| ID | Test | Input | Output Esperado |
|----|------|-------|-----------------|
| R4.1 | Índice paginado | `limit=100`, `offset=0` | 100 primeros bloques |
| R4.2 | Solo artículos | `tipo_bloque="articulos"` | Solo bloques de artículos |
| R4.3 | Solo estructura | `tipo_bloque="estructura"` | Libros, títulos, capítulos |
| R4.4 | Solo disposiciones | `tipo_bloque="disposiciones"` | da, dt, dd, df |
| R4.5 | Paginación offset | `offset=100` | Bloques 101-200 |

---

## P - Parámetros

| Parámetro | Tipo | Requerido | Default | Validador | Descripción |
|-----------|------|-----------|---------|-----------|-------------|
| `identifier` | str | Sí | - | `validate_boe_identifier()` | ID BOE |
| `tipo_bloque` | Literal["todos", "estructura", "articulos", "disposiciones"] | No | "todos" | built-in | Filtro |
| `limit` | int | No | 100 | 1-500 | Máximo resultados |
| `offset` | int | No | 0 | >= 0 | Índice inicial |

---

## V - Valor de Retorno

```python
{
    "identifier": str,
    "tipo_bloque": str,
    "total_bloques": int,
    "offset": int,
    "limit": int,
    "hay_mas": bool,
    "bloques": [
        {
            "id": str,
            "titulo": str,
            "fecha_actualizacion": str,
            "url": str
        }
    ]
}
```

---

## Tests POST (Criterios de Aceptación)

| ID | Descripción | Input | Output Esperado |
|----|-------------|-------|-----------------|
| U4.1 | Paginación correcta | `limit=50` | Exactamente 50 bloques |
| U4.2 | hay_mas correcto | `limit=50` en ley grande | `hay_mas=True` |
| U4.3 | Solo artículos | `tipo_bloque="articulos"` | Todos empiezan con "Artículo" |
| U4.4 | Solo estructura | `tipo_bloque="estructura"` | Solo LIBRO, TÍTULO, CAPÍTULO |
| U4.5 | Total correcto | cualquier filtro | `total_bloques` es conteo real |

---

# PLAN DE IMPLEMENTACIÓN

## Fase 1: Infraestructura (Día 1)

1. Crear `src/boe_mcp/validators/articles.py` con `validate_articulo()`
2. Actualizar `src/boe_mcp/validators/__init__.py`
3. Crear tests `tests/test_validators_articles.py`
4. Ejecutar tests de validadores

## Fase 2: get_article_info (Día 1-2)

1. Implementar función en `server.py`
2. Crear tests unitarios
3. Crear tests E2E
4. Ejecutar todos los tests

## Fase 3: search_in_law (Día 2)

1. Implementar función en `server.py`
2. Crear tests unitarios
3. Ejecutar tests

## Fase 4: get_law_structure_summary (Día 3)

1. Implementar función en `server.py`
2. Crear tests unitarios
3. Ejecutar tests

## Fase 5: get_law_index (Día 3)

1. Implementar función en `server.py`
2. Crear tests unitarios
3. Ejecutar tests

## Fase 6: Integración y Documentación (Día 4)

1. Tests E2E completos
2. Actualizar README
3. Actualizar CLAUDE.md
4. Crear PR

---

# CHECKLIST DE VALIDACIÓN FINAL

- [ ] Todos los tests unitarios pasan
- [ ] Todos los tests E2E pasan
- [ ] Todos los tests de seguridad pasan
- [ ] Cobertura de código > 80%
- [ ] Sin errores de linting (ruff)
- [ ] Sin errores de tipos (mypy)
- [ ] Documentación actualizada
- [ ] PR creado y revisado

---

# ANEXO: Patrones de Block ID Observados

Del análisis del XML de BOE-A-2020-4859:

| Prefijo | Tipo | Ejemplos |
|---------|------|----------|
| `no` | Nota | `no` |
| `pr` | Preámbulo | `pr` |
| `au` | Artículo único | `au` |
| `te` | Texto (título ley) | `te` |
| `lp`, `ls` | Libro | `lp`, `ls` |
| `ti`, `ti-N` | Título | `ti`, `ti-2`, `ti-3` |
| `ci`, `ci-N`, `cv`, `cv-N` | Capítulo | `ci`, `ci-2`, `cv`, `cv-3` |
| `s`, `sN`, `sN-N` | Sección/Subsección | `s1`, `s2-3`, `s4-16` |
| `a`, `aN`, `aN-N` | Artículo | `a1`, `a2`, `a1-2`, `a3-112` |
| `da`, `da-N` | Disp. Adicional | `da`, `da-2` |
| `dt` | Disp. Transitoria | `dt` |
| `dd` | Disp. Derogatoria | `dd` |
| `df`, `df-N` | Disp. Final | `df`, `df-2` |
| `fi` | Firma | `fi` |

**Nota:** Los patrones `aN-N` (ej: `a1-2` para Artículo 10, `a3-112` para Artículo 37 bis) requieren actualizar el validador `validate_block_id()` existente.
