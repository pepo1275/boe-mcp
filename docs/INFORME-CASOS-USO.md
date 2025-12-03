# Informe de Casos de Uso - Smart Navigation v2.0

**Ley de referencia:** BOE-A-2020-4859 (Texto Refundido de la Ley Concursal)

**Fecha de generación:** 2025-12-03 04:17:26

---

## Resumen Ejecutivo

Este informe valida los 4 herramientas de Smart Navigation v2.0:
1. `get_article_info` - Información de artículo específico
2. `search_in_law` - Búsqueda dentro de una ley
3. `get_law_structure_summary` - Resumen de estructura jerárquica
4. `get_law_index` - Índice de bloques de la ley

---

## 1. CASOS SIMPLES

### 1.1 get_article_info - Consultas básicas

#### S1.1 ¿Existe el artículo 1 en la Ley Concursal?
**Respuesta:** ✅ Sí, existe
- Artículo: 1
- Block ID: a1
- Título: Artículo 1

#### S1.2 ¿Cuál es el block_id del artículo 386?
**Respuesta:** `a3-98`

#### S1.3 ¿Fue modificado el artículo 1?
**Respuesta:** ✅ Sí
- Fecha actualización: 20220906
- Fecha ley original: 20200507

#### S1.4 ¿Fue modificado el artículo 386?
**Respuesta:** ❌ No
- Fecha actualización: 20200507

#### S1.5 ¿Existe el artículo 9999?
**Respuesta:** ❌ No existe
- Código error: `ARTICULO_NO_ENCONTRADO`
- Mensaje: No se encontró el artículo 9999 en BOE-A-2020-4859

#### S1.6 ¿Existe el artículo '224 bis'?
**Respuesta:** ✅ Sí, existe
- Artículo: 224 bis
- Block ID: a2-112
- Modificado: Sí

#### S1.7 ¿Cuál es el texto del artículo 1?
**Respuesta:** (primeros 500 caracteres)
```
200
    ok
  
  
    
      
        Artículo 1. Presupuesto subjetivo.
        1. La declaración de concurso procederá respecto de cualquier deudor, sea persona natural o jurídica.
        2. Las entidades que integran la organización territorial del Estado, los organismos públicos y demás entes de derecho público no podrán ser declarados en concurso.
      
      
        Artículo 1. Presupuesto subjetivo.
        1. La declaración de concurso procederá respecto de cualquier deudor, sea person...
```

### 1.2 search_in_law - Búsquedas básicas

#### S2.1 ¿Cuántos artículos modificados tiene la ley?
**Respuesta:** **409** artículos modificados

#### S2.2 Dame los artículos 1, 2 y 386
**Respuesta:** Encontrados 3 artículos

| Artículo | Título | Modificado | Fecha |
|----------|--------|------------|-------|
| 1 | Artículo 1 | ✅ | 20220906 |
| 2 | Artículo 2 | ✅ | 20220906 |
| 386 | Artículo 386 | ❌ | 20200507 |

#### S2.3 ¿Hay algún 'artículo único'?
**Respuesta:** Sí, hay **1** artículo(s) único(s)
- Artículo único

#### S2.4 Dame 5 artículos modificados
**Respuesta:** (mostrando 5 de 409)

| Artículo | Fecha Modificación |
|----------|-------------------|
| 1 | 20220906 |
| 2 | 20220906 |
| 6 | 20220906 |
| 7 | 20220906 |
| 10 | 20220906 |

### 1.3 get_law_structure_summary - Estructura básica

#### S3.1 ¿Cuántos libros tiene la Ley Concursal?
**Respuesta:** **2** libros

- LIBRO PRIMERO: 615 artículos (243 modificados)
- LIBRO SEGUNDO: 198 artículos (166 modificados)

#### S3.2 ¿Cuántos artículos tiene en total?
**Respuesta:** **813** artículos
- Modificados: 409
- Porcentaje modificado: 50.3%

#### S3.3 ¿Cuál es el título de la ley?
**Respuesta:** TEXTO REFUNDIDO DE LA LEY CONCURSAL

### 1.4 get_law_index - Índice básico

#### S4.1 Dame los primeros 10 bloques
**Respuesta:** (mostrando 10 de 1159)

| ID | Título |
|----|--------|
| no |  |
| pr | [preambulo] |
| au | Artículo único |
| da | Disposición adicional primera |
| da-2 | Disposición adicional segunda |
| da-3 | Disposición adicional tercera |
| da-4 | Disposición adicional cuarta |
| dt | Disposición transitoria única |
| dd | Disposición derogatoria única |
| df | Disposición final primera |

#### S4.2 ¿Cuántos artículos tiene la ley?
**Respuesta:** **813** artículos

#### S4.3 ¿Cuántas disposiciones tiene?
**Respuesta:** **10** disposiciones

Ejemplos:
- Disposición adicional primera
- Disposición adicional segunda
- Disposición adicional tercera
- Disposición adicional cuarta
- Disposición transitoria única

---

## 2. CASOS INTERMEDIOS

### 2.1 get_article_info - Consultas con ubicación

#### M1.1-M1.4 ¿En qué parte de la estructura está el artículo 386?
**Respuesta:** Ubicación jerárquica del artículo 386:
- **Libro:** LIBRO PRIMERO
- **Título:** TÍTULO IV
- **Capítulo:** CAPÍTULO V
- **Sección:** Sección 2

#### M1.5 ¿Cuándo fue modificado el artículo 224 bis?
**Respuesta:** 2022-09-06

### 2.2 search_in_law - Búsquedas con filtros combinados

#### M2.1 ¿Qué artículos se modificaron en 2022?
**Respuesta:** **401** artículos modificados en 2022

Primeros 10:
| Artículo | Fecha |
|----------|-------|
| 1 | 20220906 |
| 2 | 20220906 |
| 6 | 20220906 |
| 7 | 20220906 |
| 10 | 20220906 |
| 11 | 20220906 |
| 14 | 20220906 |
| 20 | 20220906 |
| 23 | 20220906 |
| 24 | 20220906 |

#### M2.2 Dame la página 2 de artículos modificados (5 por página)
**Respuesta:**

**Página 1:**
- Artículo 1
- Artículo 2
- Artículo 6
- Artículo 7
- Artículo 10

**Página 2:**
- Artículo 11
- Artículo 14
- Artículo 20
- Artículo 23
- Artículo 24

### 2.3 get_law_structure_summary - Estructura con niveles

#### M3.1-M3.2 Estadísticas por libro
**Respuesta:**

| Libro | Artículos | Modificados | % Modificado |
|-------|-----------|-------------|--------------|
| LIBRO PRIMERO | 615 | 243 | 39.5% |
| LIBRO SEGUNDO | 198 | 166 | 83.8% |

#### M3.3 ¿Cuántos títulos tiene la ley?
**Respuesta:** **19** títulos distribuidos en 2 libros

---

## 3. CASOS AVANZADOS

### 3.1 Análisis de modificaciones

#### A1.1 ¿Qué porcentaje de artículos han sido modificados?
**Respuesta:** **50.3%** de la ley ha sido modificada
- Total artículos: 813
- Artículos modificados: 409

#### A1.3 ¿Qué libro tiene más modificaciones proporcionalmente?
**Respuesta:** **LIBRO SEGUNDO**
- 166 de 198 artículos (83.8%)

### 3.2 Validaciones cruzadas

#### A3.1 ¿El total de artículos coincide entre herramientas?
**Respuesta:** ✅ Sí coinciden (diferencia: 0)
- get_law_structure_summary: 813
- get_law_index: 813

#### A3.3 ¿La suma de artículos por libro = total?
**Respuesta:** ✅ Sí, suma exacta = 813

---

## 4. CASOS DE ERROR Y VALIDACIÓN

### 4.1 Validación de entrada

| ID | Caso | Resultado | Código Error |
|----|------|-----------|--------------|
| E1.1 | Identificador inválido | ✅ Bloqueado | `VALIDATION_ERROR` |
| E1.2 | Ley inexistente | ✅ Bloqueado | `LEY_NO_ENCONTRADA` |
| E1.3 | SQL injection en artículo | ✅ Bloqueado | `VALIDATION_ERROR` |
| E1.4 | XSS en query | ✅ Bloqueado | `VALIDATION_ERROR` |
| E1.5 | Path traversal | ✅ Bloqueado | `VALIDATION_ERROR` |
| E1.6 | Búsqueda sin criterios | ✅ Bloqueado | `SIN_CRITERIOS` |
| E1.7 | Rango fechas invertido | ✅ Bloqueado | `RANGO_FECHAS_INVALIDO` |

### 4.2 Límites y paginación

#### E2.1 Offset mayor que total
**Respuesta:** Devuelve lista vacía = True, hay_mas = False

#### E2.2 Limit=0
**Respuesta:** Se ajusta y devuelve 1 bloque(s)

#### E2.3 Limit muy alto (9999)
**Respuesta:** Se ajusta a máximo 500 bloques

---

## Conclusiones

✅ **Todas las herramientas funcionan correctamente**

- Las consultas de artículos devuelven información completa
- Las búsquedas filtran correctamente por modificaciones y fechas
- La estructura jerárquica es consistente
- Las validaciones de seguridad bloquean entradas maliciosas
- Los límites se ajustan automáticamente
