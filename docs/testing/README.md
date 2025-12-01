# Documentación de Pruebas BOE-MCP v1.2.0

Este directorio contiene los resultados de las pruebas realizadas para validar la versión 1.2.0 del servidor MCP para el BOE.

## Resumen de Pruebas Ejecutadas

| Fecha | Test ID | Descripción | Resultado | Documento |
|-------|---------|-------------|-----------|-----------|
| 2025-12-01 | TC-CC-11.4 | Análisis de límites API/MCP | ✅ Completado | [limits_analysis](./TC-CC-11.4_limits_analysis.md) |
| 2025-12-01 | TC-REG-01/02 | Pruebas de regresión | ✅ 6/6 PASS | [regression_analysis](./TC-REG-01-02_regression_analysis.md) |

## Hallazgos Principales

### 1. Límites y Contexto de Agentes (TC-CC-11.4)

**Problema identificado:** El tamaño de respuesta del MCP puede agotar el contexto de agentes LLM.

| Limit | Tamaño | Tokens est. | % Contexto 200K | Recomendación |
|------:|-------:|------------:|----------------:|---------------|
| 50 | 64 KB | ~16K | 8% | ✅ Default óptimo |
| 100 | 131 KB | ~33K | 16% | ✅ Uso normal |
| 200 | 259 KB | ~65K | 32% | ⚠️ Máximo recomendado |
| 500 | 640 KB | ~160K | 80% | ⛔ Agota contexto |

**Recomendaciones:**
- Mantener `limit=50` como default
- Implementar límite máximo de 500 con advertencia si >200
- Documentar patrón de paginación para usuarios

### 2. Compatibilidad hacia Atrás (TC-REG-01/02)

**Resultado:** 100% compatible con v1.0.0 y v1.1.0

- Búsquedas básicas funcionan sin cambios
- `from_date`/`to_date` siguen funcionando
- Parámetros v1.1.0 (`rango_codigo`, etc.) operativos
- Combinación de parámetros multi-versión sin conflictos

**Clarificación importante:**
- `from_date`: Filtra por fecha de **actualización en BD**
- `fecha_publicacion_desde` (v1.2.0): Filtra por fecha de **publicación en BOE**

## Scripts de Prueba

| Script | Descripción | Uso |
|--------|-------------|-----|
| `tests/test_limits_v120.py` | Prueba límites API | `uv run python tests/test_limits_v120.py` |
| `tests/test_regression_v120.py` | Pruebas regresión | `uv run python tests/test_regression_v120.py` |

## Resultados Raw (JSON)

- `tests/results_limits_v120.json`
- `tests/results_regression_v120.json`

## Mejoras Propuestas para MCP

Basado en las pruebas, se proponen las siguientes mejoras:

### Prioridad Alta
1. [ ] Implementar límite máximo configurable (500 hard, 200 soft)
2. [ ] Añadir advertencia en respuesta si limit > 200
3. [ ] Documentar diferencia `from_date` vs `fecha_publicacion_desde`

### Prioridad Media
4. [ ] Añadir metadata de paginación en respuesta
5. [ ] Incluir tabla de tiempos esperados en README
6. [ ] Ejemplos de uso con paginación

### Prioridad Baja
7. [ ] Considerar flag `--max-limit` para clientes
8. [ ] Tests automatizados en CI/CD

---

*Documentación generada: 2025-12-01*
*Versión testeada: v1.2.0 (branch develop)*
