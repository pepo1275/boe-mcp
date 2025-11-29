# Test 1.1 - Respuesta Parseada

## Resumen Ejecutivo

✅ **5 herramientas MCP identificadas** en el servidor boe-mcp

## Herramientas Disponibles

| # | Herramienta | Línea | Descripción |
|---|-------------|-------|-------------|
| 1 | `search_laws_list` | 78 | Búsqueda avanzada de normas del BOE con filtros por fecha, ámbito, vigencia, etc. |
| 2 | `get_law_section` | 219 | Recupera partes específicas de una norma (completa, metadatos, análisis, texto, índice, bloque) |
| 3 | `get_boe_summary` | 276 | Obtiene el sumario del BOE para una fecha específica (AAAAMMDD) |
| 4 | `get_borme_summary` | 306 | Obtiene el sumario del BORME para una fecha específica (AAAAMMDD) |
| 5 | `get_auxiliary_table` | 334 | Consulta tablas auxiliares (materias, ámbitos, departamentos, rangos, etc.) |

## Detalles Técnicos

- **Framework MCP:** FastMCP
- **Nombre del servidor:** `boe-mcp`
- **Tipo de funciones:** Todas asíncronas (async)
- **API Backend:** BOE Datos Abiertos (`https://www.boe.es/datosabiertos/api/`)

## Parámetros Destacados por Herramienta

### 1. search_laws_list
- `from_date`, `to_date`: Rango de fechas
- `query_value`: Texto de búsqueda
- `solo_vigente`: Filtrar solo normas vigentes
- `ambito`: Estatal, Autonómico, Europeo
- `must`, `should`, `must_not`: Operadores lógicos

### 2. get_law_section
- `identifier`: ID de la norma (ej. BOE-A-2023-893)
- `section`: completa, metadatos, análisis, metadata-eli, texto, índice, bloque
- `format`: xml o json

### 3. get_boe_summary / get_borme_summary
- `fecha`: Fecha en formato AAAAMMDD

### 4. get_auxiliary_table
- `table_name`: materias, ambitos, estados-consolidacion, departamentos, rangos, relaciones-anteriores, relaciones-posteriores

## Archivos Generados

- `00_metadata.json` - Metadatos del test
- `01_request.json` - Comando ejecutado
- `02_response_raw.json` - Respuesta estructurada
- `03_response_parsed.md` - Este documento
- `04_evaluation.md` - Evaluación del test
