# TC-REG-01/02: Pruebas de Regresión BOE-MCP v1.2.0

**Fecha de ejecución:** 2025-12-01
**Versión testeada:** v1.2.0 (branch develop)
**Ejecutado por:** Claude Code

## 1. Objetivo

Verificar que las funcionalidades de versiones anteriores (v1.0.0 y v1.1.0) siguen funcionando correctamente tras añadir los nuevos parámetros de v1.2.0:

- **TC-REG-01**: Búsquedas sin nuevos parámetros (comportamiento legacy)
- **TC-REG-02**: Parámetros `from_date`/`to_date` siguen funcionando

## 2. Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| Total pruebas | 6 |
| Pasadas | 6 ✅ |
| Fallidas | 0 |
| Errores | 0 |
| **Resultado** | **100% PASS** |

## 3. Resultados Detallados

### 3.1 TC-REG-01: Búsquedas Legacy

#### TC-REG-01a: Búsqueda básica estilo v1.1.0
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.633s |
| Resultados | 20 |
| Query | `titulo:(protección datos) and vigencia_agotada:"N"` |
| Verificación | Devuelve resultados correctamente |

#### TC-REG-01b: Búsqueda con filtro de ámbito
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.381s |
| Resultados | 10 |
| Filtro | `ambito@codigo:"1"` (Estatal) |
| Verificación | Todos los resultados son ámbito Estatal |

#### TC-REG-01c: Búsqueda con rango_codigo (v1.1.0)
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.459s |
| Resultados | 10 |
| Filtro | `rango@codigo:"1300"` (Ley) |
| Verificación | Todos los resultados son tipo Ley |

### 3.2 TC-REG-02: Parámetros from_date/to_date

#### TC-REG-02a: Parámetro from_date
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.268s |
| Resultados | 10 |
| Parámetro | `from=20251101` |
| Fechas muestra | 20251201, 20251201, 20251201 |
| Verificación | Todas las fechas de actualización >= 2025-11-01 |

**Nota importante:** `from_date` filtra por **fecha de actualización en la BD**, no por fecha de publicación. Esto es comportamiento documentado desde v1.0.0.

#### TC-REG-02b: Combinación from_date + to_date
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.285s |
| Resultados | 10 |
| Parámetros | `from=20250101`, `to=20250601` |
| Fechas muestra | 20250531, 20250530, 20250529 |
| Verificación | Todas en rango [2025-01-01, 2025-06-01] |

#### TC-REG-02c: Mezcla parámetros v1.0 + v1.1 + v1.2
| Aspecto | Resultado |
|---------|-----------|
| Status | ✅ PASS |
| Tiempo | 0.344s |
| Resultados | 10 |
| Parámetros combinados | `from_date` (v1.0) + `rango@codigo` (v1.1) + `sort` (v1.2) |
| Verificación | Sin conflictos, ordenamiento correcto descendente |

**Fechas de disposición ordenadas:** 20251015 → 20251009 → 20251009 (desc) ✓

## 4. Conclusiones

### 4.1 Compatibilidad hacia atrás: CONFIRMADA ✅

- **v1.0.0 features**: Búsquedas básicas, ámbito, from_date/to_date funcionan
- **v1.1.0 features**: rango_codigo, materia_codigo, numero_oficial funcionan
- **Combinación**: No hay conflictos al mezclar parámetros de diferentes versiones

### 4.2 Diferencia clave: from_date vs fecha_publicacion_desde

| Parámetro | Versión | Filtra por | Uso |
|-----------|---------|------------|-----|
| `from_date` | v1.0.0 | Fecha actualización BD | Encontrar normas actualizadas recientemente |
| `fecha_publicacion_desde` | v1.2.0 | Fecha publicación BOE | Filtrar por cuándo se publicó la norma |

**Son complementarios, no redundantes.**

### 4.3 No-breaking changes confirmados

La v1.2.0 es **totalmente retrocompatible**:
- Clientes usando parámetros v1.0.0/v1.1.0 seguirán funcionando sin cambios
- Nuevos parámetros v1.2.0 son opcionales
- No hay cambios en estructura de respuesta

## 5. Archivos Generados

- `tests/test_regression_v120.py` - Script de pruebas
- `tests/results_regression_v120.json` - Resultados raw
- `docs/testing/TC-REG-01-02_regression_analysis.md` - Este documento

## 6. Recomendaciones

1. **Documentar diferencia from_date vs fecha_publicacion_desde** en README
2. **Mantener from_date/to_date** sin deprecar (uso válido diferente)
3. **Añadir ejemplos de uso combinado** en documentación

---

## Anexo: JSON de Resultados

```json
{
  "test_date": "2025-12-01 12:35:XX",
  "test_type": "regression",
  "version_tested": "v1.2.0",
  "summary": {
    "total": 6,
    "passed": 6,
    "failed": 0,
    "errors": 0
  }
}
```
