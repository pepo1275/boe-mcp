# HALLAZGO #001: Sumarios BOE Extensos

**Fecha descubrimiento:** 2025-11-23
**Descubierto durante:** Test 1.4 - Sumario BOE
**Severidad:** Media-Alta (afecta usabilidad en producción)

---

## Descripción del Problema

Al solicitar el sumario del BOE para una fecha con mucho contenido (ej: 22/11/2024, día laboral típico), la respuesta de la API es **extremadamente grande** (cientos de documentos), causando:

1. **Truncamiento por límite de tokens** - La respuesta fue cortada a 25,000 tokens
2. **XML potencialmente corrupto** - El truncamiento puede dejar el XML inválido
3. **Consumo excesivo de contexto LLM** - Ineficiente para uso con Claude/GPT
4. **Imposibilidad de procesar datos completos** - Pérdida de información

## Evidencia

```
Fecha solicitada: 20241122
Contenido: ~150+ documentos en múltiples secciones
Resultado: Respuesta truncada, datos incompletos
```

## Análisis del Código Actual

El servidor MCP (`server.py`, líneas 276-292) no implementa ningún control de tamaño:

```python
@mcp.tool()
async def get_boe_summary(params: boe_summaryParams) -> Union[dict, str]:
    fecha = params.fecha
    endpoint = f"/datosabiertos/api/boe/sumario/{fecha}"
    data = await make_boe_request(endpoint)
    # ...
    return data  # ← Devuelve TODO el sumario sin límite ni filtros
```

## Impacto

| Escenario | Documentos | Tamaño Aprox. | Problema |
|-----------|------------|---------------|----------|
| Domingo/Festivo | 0-10 | <5KB | ✅ OK |
| Día laboral normal | 50-100 | 25-50KB | ⚠️ Grande |
| Lunes típico | 100-200 | 50-100KB | ❌ Muy grande |
| Día con RDs masivos | 300+ | 150KB+ | ❌ Inmanejable |

## Opciones de Solución

### Opción A: Modificar el MCP Server (Filtros Inteligentes)

Añadir parámetros de filtrado a `get_boe_summary`:

```python
@mcp.tool()
async def get_boe_summary(
    fecha: str,
    seccion: str | None = None,      # Filtrar: "I", "II", "III", etc.
    departamento: str | None = None,  # Filtrar por departamento emisor
    limit: int = 20,                   # Máximo de items
    solo_metadata: bool = True         # Solo títulos, sin contenido
) -> dict:
```

**Pros:**
- Solución integrada en el MCP
- Fácil de usar para el LLM
- Un solo punto de mantenimiento

**Contras:**
- Requiere modificar el servidor
- La API del BOE puede no soportar todos los filtros server-side
- Filtrado client-side sigue descargando todo

### Opción B: Script de Descarga Separado

Crear un script ETL independiente que:
1. Descarga sumarios completos vía API directa
2. Almacena en base de datos local (SQLite/JSON)
3. El MCP consulta la BD local con filtros

```
BOE API → Script ETL → BD Local → MCP Server → LLM
```

**Pros:**
- Separación de responsabilidades
- Datos siempre disponibles offline
- Filtrado eficiente sobre datos locales

**Contras:**
- Más componentes que mantener
- Requiere ejecución periódica (cron)
- Mayor complejidad de despliegue

### Opción C: Híbrido - Dos Herramientas MCP

```python
# Para consultas rápidas (uso con LLM)
@mcp.tool()
async def get_boe_summary_lite(fecha: str, seccion: str = None, limit: int = 10):
    """Resumen ligero: conteos y títulos principales"""

# Para descarga completa (procesamiento batch)
@mcp.tool()
async def download_boe_full(fecha: str, output_path: str):
    """Descarga completa a archivo local"""
```

**Pros:**
- Flexibilidad según caso de uso
- El LLM puede elegir la herramienta apropiada

**Contras:**
- Más herramientas que documentar
- Decisión de cuál usar puede ser confusa

## Recomendación

**Corto plazo:**
- Usar fechas con poco contenido para testing
- Documentar la limitación

**Medio plazo:**
- Implementar **Opción A** (filtros en MCP) como mejora mínima viable
- Evaluar si la API del BOE soporta filtrado server-side

**Largo plazo:**
- Considerar **Opción B** (script separado + BD local) para casos de uso de análisis masivo

## Decisión Pendiente

Antes de implementar, evaluar:
1. ¿La API del BOE permite filtrar sumarios por sección/departamento?
2. ¿El caso de uso principal requiere sumarios completos o solo consultas puntuales?
3. ¿Se necesita histórico de sumarios o solo consultas en tiempo real?

---

**Estado:** Documentado, pendiente de decisión de implementación
**Siguiente acción:** Continuar tests con fechas de bajo contenido
