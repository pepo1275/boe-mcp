# TC-CC-11.4: Análisis de Límites BOE-MCP v1.2.0

**Fecha de ejecución:** 2025-12-01
**Versión testeada:** v1.2.0 (branch develop)
**Ejecutado por:** Claude Code

## 1. Objetivo

Determinar los límites prácticos del parámetro `limit` en `search_laws_list` considerando:

1. **Límites de la API BOE** - Capacidad real del backend
2. **Impacto en agentes LLM** - Consumo de contexto al procesar respuestas
3. **Recomendaciones de uso** - Guía para usuarios y clientes
4. **Mejoras a implementar** - Cambios sugeridos en el MCP

## 2. Metodología

### 2.1 Script de prueba
- Ubicación: `tests/test_limits_v120.py`
- Pruebas directas contra API BOE (sin overhead MCP)
- Dos escenarios: query simple y con filtro de fechas v1.2.0

### 2.2 Límites testeados
```
[10, 50, 100, 200, 500, 1000, 2000, 5000]
```

### 2.3 Métricas capturadas
- Tiempo de respuesta (segundos)
- Cantidad de resultados devueltos
- Tamaño de respuesta (KB)
- Estado (OK/ERROR/TIMEOUT)

## 3. Resultados

### 3.1 Tabla de Rendimiento API BOE

| Limit | Resultados | Tiempo (s) | Tamaño (KB) | KB/resultado |
|------:|-----------:|-----------:|------------:|-------------:|
| 10 | 10 | 0.26 | 12.0 | 1.20 |
| 50 | 50 | 0.37 | 64.1 | 1.28 |
| 100 | 100 | 0.43 | 130.6 | 1.31 |
| 200 | 200 | 0.40 | 259.4 | 1.30 |
| 500 | 500 | 0.53 | 640.4 | 1.28 |
| 1000 | 1000 | 0.63 | 1,252.1 | 1.25 |
| 2000 | 2000 | 5.74 | 2,472.4 | 1.24 |
| 5000 | 4820* | 11.10 | 5,874.0 | 1.22 |

*\*4820 = total de normas vigentes con "ley" en título (límite del dataset)*

### 3.2 Con Filtro de Fechas (v1.2.0)

| Limit | Tiempo (s) | Tamaño (KB) | Observación |
|------:|-----------:|------------:|-------------|
| 10 | 0.26 | 12.4 | Igual rendimiento |
| 50 | 0.53 | 64.1 | +43% tiempo vs simple |
| 100 | 0.63 | 131.6 | Aceptable |
| 500 | 1.38 | 667.0 | +159% tiempo vs simple |
| 1000 | 2.24 | 1,321.0 | +256% tiempo vs simple |
| 5000 | 11.40 | 6,357.7 | Tiempo excesivo |

### 3.3 Hallazgos Clave

1. **Comportamiento lineal hasta limit=1000**
   - ~1.3 KB por resultado (consistente)
   - ~0.6ms por resultado

2. **Salto no lineal en limit>1000**
   - 1000→2000: tiempo x9 (0.63s → 5.74s)
   - Sugiere cambio de estrategia en backend BOE

3. **API BOE robusta**
   - Sin errores hasta 5000
   - Sin rate limiting detectado
   - Timeout de 30s del servidor suficiente hasta 5000

4. **Filtros de fecha añaden overhead**
   - +40-160% tiempo adicional según volumen
   - Pero permiten acotar resultados (trade-off útil)

## 4. Impacto en Agentes LLM

### 4.1 El Problema del Contexto

Cuando un agente LLM (Claude, GPT, etc.) usa el MCP:

```
Usuario → Agente → MCP → API BOE → MCP → Agente → Usuario
                                    ↓
                            Respuesta JSON
                            procesada por agente
                            (CONSUME CONTEXTO)
```

**Cada resultado consume ~1.3KB de contexto del agente.**

### 4.2 Estimación de Consumo de Tokens

| Limit | Tamaño JSON | Tokens estimados* | % Contexto Claude** |
|------:|------------:|------------------:|--------------------:|
| 10 | 12 KB | ~3,000 | 1.5% |
| 50 | 64 KB | ~16,000 | 8% |
| 100 | 131 KB | ~33,000 | 16% |
| 200 | 259 KB | ~65,000 | 32% |
| 500 | 640 KB | ~160,000 | 80% |
| 1000 | 1,252 KB | ~313,000 | 156% ⛔ |

*\*Estimación: ~250 tokens/KB de JSON estructurado*
*\*\*Basado en contexto de 200K tokens*

### 4.3 Conclusión Crítica

> **Con limit=500 ya se consume ~80% del contexto disponible del agente.**
>
> Límites mayores a 200-300 son **contraproducentes** porque:
> - Agotan el contexto del agente
> - Impiden seguimiento de conversación
> - Pueden causar truncamiento de respuestas
> - El agente no puede procesar toda la información

## 5. Recomendaciones

### 5.1 Para Usuarios del MCP

| Caso de Uso | Límite Recomendado | Justificación |
|-------------|-------------------:|---------------|
| Búsqueda exploratoria | 10-20 | Ver primeros resultados relevantes |
| Búsqueda normal | 50 (default) | Balance óptimo |
| Listado completo tema específico | 100 | Máximo práctico con agente |
| Exportación/análisis | 200 | Usar con filtros restrictivos |
| **Nunca usar** | >500 | Agota contexto del agente |

### 5.2 Patrones de Uso Recomendados

#### ✅ Correcto: Filtrar antes de ampliar
```
1. Buscar con limit=20 para explorar
2. Añadir filtros (fecha, rango, materia)
3. Subir a limit=50-100 si necesario
```

#### ✅ Correcto: Paginación manual
```
1. Primera búsqueda: limit=50, offset=0
2. Si necesita más: limit=50, offset=50
3. Procesar en lotes pequeños
```

#### ⛔ Incorrecto: Pedir todo de una vez
```
# NO HACER:
search_laws_list(query="ley", limit=1000)
# Resultado: agota contexto, respuesta truncada
```

### 5.3 Para Implementar en MCP

#### Cambio 1: Límite máximo configurable (RECOMENDADO)
```python
# En server.py
MAX_LIMIT_DEFAULT = 200  # Protección contra agotamiento de contexto
MAX_LIMIT_HARD = 500     # Límite absoluto

async def search_laws_list(
    limit: int | None = 50,
    ...
) -> Union[dict, str]:
    # Aplicar límite
    effective_limit = min(limit or 50, MAX_LIMIT_HARD)
    if limit and limit > MAX_LIMIT_DEFAULT:
        # Advertencia en respuesta
        warning = f"⚠️ Límite ajustado de {limit} a {effective_limit}"
```

#### Cambio 2: Metadata de paginación en respuesta
```python
# Añadir a la respuesta:
{
    "metadata": {
        "limit_requested": 500,
        "limit_applied": 200,
        "results_returned": 200,
        "has_more": true,
        "next_offset": 200,
        "warning": "Límite reducido para optimizar contexto del agente"
    },
    "data": [...]
}
```

#### Cambio 3: Documentación en docstring
```python
"""
Args:
    limit: Máximo de resultados (default=50, máximo recomendado=200).
           NOTA: Límites >200 pueden agotar el contexto del agente LLM.
           Para grandes volúmenes, usar paginación con offset.
"""
```

## 6. Decisiones Pendientes

| Decisión | Opciones | Recomendación |
|----------|----------|---------------|
| ¿Imponer límite duro? | Sí (500) / No | **Sí, con advertencia** |
| ¿Límite configurable por cliente? | Sí / No | Sí, via parámetro |
| ¿Incluir metadata de paginación? | Sí / No | **Sí** |
| ¿Advertencia en respuesta? | Sí / No | Sí, si limit > 200 |

## 7. Archivos Generados

- `tests/test_limits_v120.py` - Script de pruebas
- `tests/results_limits_v120.json` - Resultados raw
- `docs/testing/TC-CC-11.4_limits_analysis.md` - Este documento

## 8. Próximos Pasos

1. [ ] Revisar con equipo las decisiones pendientes
2. [ ] Implementar cambios acordados en MCP
3. [ ] Actualizar README con guía de límites
4. [ ] Considerar pruebas de carga sostenida

---

## Anexo: Datos Raw

### A.1 Query Simple
```json
{
  "limit": 5000,
  "status": "OK",
  "results": 4820,
  "time_s": 11.102,
  "size_kb": 5874.0
}
```

### A.2 Análisis Automático
```json
{
  "max_working_limit": 5000,
  "recommended_limit": 1000,
  "avg_time_per_result": 0.0022,
  "breaking_point": null,
  "notes": [
    "Limit 2000: >5s de respuesta",
    "Limit 5000: >5s de respuesta",
    "⚠️ Limit 5000: tiempo excesivo (11.1s)"
  ]
}
```
