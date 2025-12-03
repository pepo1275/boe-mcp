# Casos de Uso - Smart Navigation v2.0

## Ley de Referencia
**BOE-A-2020-4859** - Texto Refundido de la Ley Concursal (752+ artículos)

---

## 1. CASOS SIMPLES (Una herramienta, parámetros básicos)

### 1.1 get_article_info - Consultas básicas

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| S1.1 | ¿Existe el artículo 1 en la Ley Concursal? | `get_article_info("BOE-A-2020-4859", "1")` | articulo="1", error=None |
| S1.2 | ¿Cuál es el block_id del artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | block_id="a3-98" |
| S1.3 | ¿Fue modificado el artículo 1? | `get_article_info("BOE-A-2020-4859", "1")` | modificado=True |
| S1.4 | ¿Fue modificado el artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | modificado=False |
| S1.5 | ¿Existe el artículo 9999? | `get_article_info("BOE-A-2020-4859", "9999")` | error=True, codigo="ARTICULO_NO_ENCONTRADO" |
| S1.6 | ¿Existe el artículo "224 bis"? | `get_article_info("BOE-A-2020-4859", "224 bis")` | articulo="224 bis", error=None |
| S1.7 | ¿Cuál es el texto del artículo 1? | `get_article_info("BOE-A-2020-4859", "1", incluir_texto=True)` | texto contiene "presupuesto subjetivo" |

### 1.2 search_in_law - Búsquedas básicas

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| S2.1 | ¿Cuántos artículos modificados tiene la ley? | `search_in_law("BOE-A-2020-4859", solo_modificados=True)` | total_encontrados=409 |
| S2.2 | Dame los artículos 1, 2 y 386 | `search_in_law("BOE-A-2020-4859", articulos=["1", "2", "386"])` | total_encontrados=3 |
| S2.3 | ¿Hay algún "artículo único"? | `search_in_law("BOE-A-2020-4859", query="único")` | total_encontrados>=1 |
| S2.4 | Dame 5 artículos modificados | `search_in_law("BOE-A-2020-4859", solo_modificados=True, limit=5)` | len(resultados)=5 |

### 1.3 get_law_structure_summary - Estructura básica

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| S3.1 | ¿Cuántos libros tiene la Ley Concursal? | `get_law_structure_summary("BOE-A-2020-4859", nivel="libros")` | len(estructura)=2 |
| S3.2 | ¿Cuántos artículos tiene en total? | `get_law_structure_summary("BOE-A-2020-4859")` | total_articulos=813 |
| S3.3 | ¿Cuál es el título de la ley? | `get_law_structure_summary("BOE-A-2020-4859")` | titulo contiene "CONCURSAL" |

### 1.4 get_law_index - Índice básico

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| S4.1 | Dame los primeros 10 bloques | `get_law_index("BOE-A-2020-4859", limit=10)` | len(bloques)=10 |
| S4.2 | ¿Cuántos artículos tiene la ley? | `get_law_index("BOE-A-2020-4859", tipo_bloque="articulos")` | total_bloques=813 |
| S4.3 | ¿Cuántas disposiciones tiene? | `get_law_index("BOE-A-2020-4859", tipo_bloque="disposiciones")` | total_bloques>0 |

---

## 2. CASOS INTERMEDIOS (Una herramienta, parámetros combinados)

### 2.1 get_article_info - Consultas con ubicación

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| M1.1 | ¿En qué libro está el artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | ubicacion.libro="LIBRO PRIMERO" |
| M1.2 | ¿En qué título está el artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | ubicacion.titulo="TÍTULO IV" |
| M1.3 | ¿En qué capítulo está el artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | ubicacion.capitulo="CAPÍTULO V" |
| M1.4 | ¿En qué sección está el artículo 386? | `get_article_info("BOE-A-2020-4859", "386")` | ubicacion.seccion="Sección 2" |
| M1.5 | ¿Cuándo fue modificado el artículo 224 bis? | `get_article_info("BOE-A-2020-4859", "224 bis")` | fecha_actualizacion="20220906" |

### 2.2 search_in_law - Búsquedas con filtros combinados

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| M2.1 | ¿Qué artículos se modificaron en 2022? | `search_in_law("BOE-A-2020-4859", modificados_desde="20220101", modificados_hasta="20221231")` | Todos con fecha en 2022 |
| M2.2 | Dame la página 2 de artículos modificados (5 por página) | `search_in_law("BOE-A-2020-4859", solo_modificados=True, limit=5, offset=5)` | Artículos diferentes a página 1 |
| M2.3 | ¿Cuántos artículos modificados hay después de 2021? | `search_in_law("BOE-A-2020-4859", modificados_desde="20210101")` | total_encontrados>0 |

### 2.3 get_law_structure_summary - Estructura con niveles

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| M3.1 | ¿Cuántos artículos tiene el LIBRO PRIMERO? | `get_law_structure_summary("BOE-A-2020-4859", nivel="libros")` | estructura[0].num_articulos=615 |
| M3.2 | ¿Cuántos artículos modificados tiene el LIBRO SEGUNDO? | `get_law_structure_summary("BOE-A-2020-4859", nivel="libros")` | estructura[1].num_modificados=166 |
| M3.3 | ¿Cuántos títulos tiene la ley? | `get_law_structure_summary("BOE-A-2020-4859", nivel="titulos")` | Contar hijos de todos los libros |

### 2.4 get_law_index - Índice con filtros y paginación

| ID | Pregunta | Llamada | Resultado Esperado |
|----|----------|---------|-------------------|
| M4.1 | Dame los artículos del 100 al 110 | `get_law_index("BOE-A-2020-4859", tipo_bloque="articulos", limit=10, offset=99)` | 10 artículos desde el 100 |
| M4.2 | ¿Hay más de 500 bloques estructurales? | `get_law_index("BOE-A-2020-4859", tipo_bloque="estructura")` | total_bloques, hay_mas |
| M4.3 | Dame las disposiciones adicionales | `get_law_index("BOE-A-2020-4859", tipo_bloque="disposiciones")` | Bloques con id empezando por da/dt/dd/df |

---

## 3. CASOS AVANZADOS (Múltiples herramientas, lógica compleja)

### 3.1 Análisis de modificaciones

| ID | Pregunta | Herramientas | Lógica |
|----|----------|--------------|--------|
| A1.1 | ¿Qué porcentaje de artículos han sido modificados? | `get_law_structure_summary` | (total_modificados / total_articulos) * 100 |
| A1.2 | ¿El artículo 386 está en una sección con muchos artículos modificados? | `get_article_info` + `search_in_law` | Obtener ubicación, buscar artículos en esa sección |
| A1.3 | ¿Qué libro tiene más modificaciones proporcionalmente? | `get_law_structure_summary` | Comparar num_modificados/num_articulos por libro |

### 3.2 Navegación jerárquica

| ID | Pregunta | Herramientas | Lógica |
|----|----------|--------------|--------|
| A2.1 | Dame todos los artículos del TÍTULO IV | `get_law_index` + filtrar por ubicación | Obtener índice, filtrar por título |
| A2.2 | ¿Cuántos capítulos tiene el TÍTULO IV del LIBRO PRIMERO? | `get_law_structure_summary(nivel="capitulos")` | Navegar estructura jerárquica |
| A2.3 | ¿Qué artículos están en el mismo capítulo que el 386? | `get_article_info` + `get_law_index` | Obtener ubicación, filtrar índice |

### 3.3 Comparaciones y validaciones

| ID | Pregunta | Herramientas | Lógica |
|----|----------|--------------|--------|
| A3.1 | ¿El total de artículos coincide entre herramientas? | `get_law_structure_summary` + `get_law_index` | Comparar total_articulos vs total_bloques(tipo=articulos) |
| A3.2 | ¿Todos los artículos modificados tienen fecha posterior a 20200507? | `search_in_law` | Verificar fecha_actualizacion > fecha_ley_original |
| A3.3 | ¿La suma de artículos por libro = total? | `get_law_structure_summary` | sum(libro.num_articulos) == total_articulos |

---

## 4. CASOS DE ERROR Y EDGE CASES

### 4.1 Validación de entrada

| ID | Caso | Llamada | Resultado Esperado |
|----|------|---------|-------------------|
| E1.1 | Identificador inválido | `get_article_info("INVALIDO", "1")` | error=True, codigo="VALIDATION_ERROR" |
| E1.2 | Ley inexistente | `get_article_info("BOE-A-0000-0000", "1")` | error=True, codigo="LEY_NO_ENCONTRADA" |
| E1.3 | Artículo con caracteres inválidos | `get_article_info("BOE-A-2020-4859", "1; DROP")` | error=True, codigo="VALIDATION_ERROR" |
| E1.4 | XSS en query | `search_in_law("BOE-A-2020-4859", query="<script>")` | error=True, codigo="VALIDATION_ERROR" |
| E1.5 | Path traversal | `get_article_info("../etc/passwd", "1")` | error=True, codigo="VALIDATION_ERROR" |
| E1.6 | Búsqueda sin criterios | `search_in_law("BOE-A-2020-4859")` | error=True, codigo="SIN_CRITERIOS" |
| E1.7 | Rango de fechas invertido | `search_in_law("BOE-A-2020-4859", modificados_desde="20221231", modificados_hasta="20220101")` | error=True, codigo="RANGO_FECHAS_INVALIDO" |

### 4.2 Límites y paginación

| ID | Caso | Llamada | Resultado Esperado |
|----|------|---------|-------------------|
| E2.1 | Offset mayor que total | `get_law_index("BOE-A-2020-4859", offset=10000)` | bloques=[], hay_mas=False |
| E2.2 | Limit=0 (se ajusta a 1) | `get_law_index("BOE-A-2020-4859", limit=0)` | len(bloques)=1 |
| E2.3 | Limit muy alto (se ajusta) | `get_law_index("BOE-A-2020-4859", limit=9999)` | len(bloques)<=500 |

### 4.3 Casos especiales de artículos

| ID | Caso | Llamada | Resultado Esperado |
|----|------|---------|-------------------|
| E3.1 | Artículo único | `get_article_info("BOE-A-2020-4859", "único")` | articulo="único" |
| E3.2 | Artículo con bis | `get_article_info("BOE-A-2020-4859", "224 bis")` | articulo="224 bis" |
| E3.3 | Buscar "3" no devuelve "30", "31"... | `get_article_info("BOE-A-2020-4859", "3")` | articulo="3" exactamente |

---

## 5. PREGUNTAS DE NEGOCIO (Casos reales de uso por LLMs)

### 5.1 Para abogados/juristas

| ID | Pregunta | Cómo responderla |
|----|----------|------------------|
| N1.1 | "¿Qué dice el artículo 386 de la Ley Concursal?" | `get_article_info` con incluir_texto=True |
| N1.2 | "¿Ha cambiado el artículo sobre legitimación desde 2020?" | `get_article_info` verificar modificado y fecha |
| N1.3 | "Dame un resumen de la estructura de la ley" | `get_law_structure_summary` |
| N1.4 | "¿Qué artículos del Libro Segundo fueron modificados?" | `search_in_law` + filtrar por ubicación |

### 5.2 Para investigadores

| ID | Pregunta | Cómo responderla |
|----|----------|------------------|
| N2.1 | "¿Qué porcentaje de la ley ha sido reformado?" | `get_law_structure_summary` calcular porcentaje |
| N2.2 | "¿Cuándo fue la última reforma?" | `search_in_law` ordenar por fecha |
| N2.3 | "¿Qué secciones son más estables (menos modificaciones)?" | `get_law_structure_summary` comparar ratios |

### 5.3 Para desarrolladores/integradores

| ID | Pregunta | Cómo responderla |
|----|----------|------------------|
| N3.1 | "Necesito todos los block_id para cachear la ley" | `get_law_index` iterar con paginación |
| N3.2 | "¿Cuántas llamadas necesito para descargar toda la ley?" | `get_law_index` calcular total/limit |
| N3.3 | "Dame solo los metadatos, no el texto" | `get_article_info` con incluir_texto=False |

---

## 6. MATRIZ DE COBERTURA

| Funcionalidad | get_article_info | search_in_law | get_law_structure_summary | get_law_index |
|---------------|------------------|---------------|---------------------------|---------------|
| Buscar artículo específico | ✅ | ✅ | ❌ | ❌ |
| Obtener texto | ✅ | ❌ | ❌ | ❌ |
| Ver ubicación jerárquica | ✅ | ❌ | ✅ | ❌ |
| Ver si fue modificado | ✅ | ✅ | ✅ | ❌ |
| Filtrar por fecha | ❌ | ✅ | ❌ | ❌ |
| Buscar por texto | ❌ | ✅ | ❌ | ❌ |
| Ver estructura completa | ❌ | ❌ | ✅ | ✅ |
| Paginar resultados | ❌ | ✅ | ❌ | ✅ |
| Contar artículos | ❌ | ✅ | ✅ | ✅ |
| Filtrar por tipo bloque | ❌ | ❌ | ❌ | ✅ |

---

## Resumen de Tests a Generar

| Categoría | Cantidad | Prioridad |
|-----------|----------|-----------|
| Simples (S) | 18 | Alta |
| Intermedios (M) | 14 | Alta |
| Avanzados (A) | 9 | Media |
| Errores (E) | 12 | Alta |
| Negocio (N) | 10 | Media |
| **TOTAL** | **63** | |
