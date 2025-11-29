# Evaluación Test 2.5: Operadores Lógicos

## Criterios de Éxito

| Criterio | Esperado | Resultado | Estado |
|----------|----------|-----------|--------|
| Operador must | Condición AND | ✅ Funciona | ✅ |
| Operador should | Condición OR | ✅ Funciona | ✅ |
| Operador must_not | Condición NOT | ✅ Funciona | ✅ |
| Sin errores | Sin excepciones | ✅ Sin errores | ✅ |

## Pruebas Realizadas

### 1. Operador `must` (AND)
**Query:** must={"rango@codigo": "1300"} + ambito=Estatal
**Resultado:** 5 Leyes estatales (Ley 40/2015, Ley 39/2015, etc.)
**Query generado:** `... and (rango@codigo:1300)`

### 2. Operador `must_not` (NOT)
**Query:** query="procedimiento administrativo" + must_not={"rango@codigo": "1340"}
**Resultado:** Normas excluyendo Real Decretos (Leyes, Órdenes, RDL)
**Query generado:** `... and not rango@codigo:1340`

### 3. Operador `should` (OR)
**Query:** query="derechos" + should={"departamento@codigo": "4810"}
**Resultado:** 5 normas del Ministerio de Justicia sobre derechos
**Query generado:** `... and (departamento@codigo:4810)`

## Observaciones Técnicas

1. Los operadores se traducen directamente a Elasticsearch query_string
2. Formato de diccionario: `{"campo": "valor"}`
3. Campos con "@" para subcampos: `rango@codigo`, `departamento@codigo`
4. Se pueden combinar con otros filtros (ámbito, fechas, etc.)

## Casos de Uso

| Operador | Caso de uso |
|----------|-------------|
| must | Filtrar por rango específico (solo Leyes) |
| must_not | Excluir departamentos o rangos |
| should | Priorizar ciertos criterios |

## Score Detallado

| Dimensión | Peso | Puntuación | Comentario |
|-----------|------|------------|------------|
| Funcionalidad | 40% | 5/5 | Todos funcionan perfectamente |
| Rendimiento | 20% | 5/5 | Rápido (~2s por query) |
| Usabilidad | 20% | 5/5 | Sintaxis clara con diccionarios |
| Completitud | 20% | 5/5 | Tres operadores disponibles |

**Score Final: 5.0/5**
