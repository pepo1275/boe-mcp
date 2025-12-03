# RPVEA 2.0 Framework para BOE-MCP
## Research → Prepare → Validate → Execute → Assess

**Versión:** 2.0
**Fecha:** 2025-12-03
**Adaptado de:** RPVEA Framework 1.1 (MCP-BOE-Consolidada)
**Proyecto:** boe-mcp

---

## PROPÓSITO

Este framework adapta la metodología RPVEA para el desarrollo de nuevas herramientas en boe-mcp. La regla fundamental:

> **"5 minutos en R (Research) ahorran 30 minutos en E (Execute)"**

**Diferencia clave con testing:** Este RPVEA está orientado a **desarrollo de nuevas funcionalidades**, no solo testing. Incorpora las lecciones aprendidas de implementaciones anteriores (Smart Navigation v2.0, validators v1.3.0).

---

## TIPOS DE DESARROLLO: CONFORMIDAD vs MEJORA

### Desarrollo de Conformidad (Tipo C)
**Pregunta:** ¿Exponemos correctamente la API del BOE?

- Pasar parámetros sin modificación
- Parsear respuesta sin pérdida de datos
- Propagar errores adecuadamente

### Desarrollo de Mejora (Tipo M)
**Pregunta:** ¿Añadimos valor sobre la API raw?

- Filtrar/paginar respuestas grandes
- Extraer metadatos útiles
- Estructurar datos para LLMs

**Smart Summary es Tipo M:** Mejoramos sobre `get_boe_summary` que devuelve 300KB+ raw.

---

## FASES RPVEA 2.0

### FASE R: RESEARCH (Investigación) - 15-30 min

**Objetivo:** Entender completamente antes de actuar.

#### Checklist R-BOE-MCP:

##### R1. Documentación API BOE
- [ ] Endpoint a utilizar
- [ ] Estructura de request
- [ ] Estructura de response (JSON/XML)
- [ ] Tamaño típico de respuesta
- [ ] Casos edge (sin datos, errores)

##### R2. Código existente en boe-mcp
- [ ] ¿Existe funcionalidad similar?
- [ ] ¿Qué validadores puedo reutilizar?
- [ ] ¿Qué patrones de respuesta usar?
- [ ] ¿Tests existentes como referencia?

##### R3. Problema a resolver
- [ ] ¿Cuál es el problema actual?
- [ ] ¿Qué impacto tiene? (tamaño, tokens, UX)
- [ ] ¿Qué solución proponemos?

#### Código reutilizable conocido (v1.4.0):

| Componente | Ubicación | Uso |
|------------|-----------|-----|
| `validate_fecha()` | `validators/dates.py` | Fechas AAAAMMDD |
| `validate_boe_identifier()` | `validators/identifiers.py` | BOE-A-YYYY-NNNNN |
| `validate_block_id()` | `validators/identifiers.py` | IDs de bloques |
| `validate_query_value()` | `validators/queries.py` | Texto de búsqueda |
| `validate_articulo()` | `validators/articles.py` | Números de artículo |
| `ValidationError` | `validators/base.py` | Excepción estándar |
| `make_boe_request()` | `server.py` | Peticiones JSON |
| `make_boe_raw_request()` | `server.py` | Peticiones XML |

#### Patrones de respuesta establecidos:

**Éxito:**
```python
{
    "campo1": valor,
    "campo2": valor,
    # Sin campo "error"
}
```

**Error:**
```python
{
    "error": True,
    "codigo": "CODIGO_ERROR",
    "mensaje": "Descripción legible",
    "detalles": {...} | None
}
```

**Paginación:**
```python
{
    "total_items": int,
    "offset": int,
    "limit": int,
    "hay_mas": bool,
    "items": [...]
}
```

#### Deliverables R:
- [ ] Documentación del endpoint objetivo
- [ ] Lista de código reutilizable identificado
- [ ] Problema y solución documentados

---

### FASE P: PREPARE (Preparación) - 10-15 min

**Objetivo:** Diseñar antes de implementar.

#### Checklist P-BOE-MCP:

##### P1. Definición de herramienta
- [ ] Nombre de la función
- [ ] Propósito (1 línea)
- [ ] Parámetros con tipos y validadores
- [ ] Estructura de respuesta éxito
- [ ] Estructura de respuesta error
- [ ] Códigos de error específicos

##### P2. Validador nuevo (si aplica)
- [ ] Nombre del validador
- [ ] Valores válidos
- [ ] Casos de normalización
- [ ] Tests del validador

##### P3. Tests a crear
- [ ] Tests E2E principales
- [ ] Tests de seguridad
- [ ] Tests de edge cases

#### Template de definición de herramienta:

```markdown
## HERRAMIENTA: `nombre_funcion`

### Propósito
[1 línea describiendo qué hace]

### Parámetros
| Param | Tipo | Requerido | Default | Validador |
|-------|------|-----------|---------|-----------|
| param1 | str | Sí | - | validate_xxx() |

### Respuesta éxito
```python
{
    "campo": tipo
}
```

### Respuesta error
| Código | Condición | Mensaje |
|--------|-----------|---------|
| VALIDATION_ERROR | Param inválido | Detalle |

### Tests E2E
| ID | Descripción | Input | Output esperado |
|----|-------------|-------|-----------------|
| E1 | Caso normal | {...} | {...} |
```

#### Deliverables P:
- [ ] Definición completa de herramienta(s)
- [ ] Validador nuevo definido (si aplica)
- [ ] Lista de tests a crear

---

### FASE V: VALIDATE (Validación Pre-código) - 15-30 min

**Objetivo:** Triple validación antes de escribir código.

#### V1: Validación de API (Endpoint directo)
**¿Qué valida?** Que la API BOE responde como esperamos.

```bash
# Probar endpoint directamente
curl "https://www.boe.es/datosabiertos/api/boe/sumario/20241202" | head -c 1000
```

**Resultado:** ✅ API responde / ❌ Error de API

#### V2: Validación de Estructura
**¿Qué valida?** Que entendemos la estructura de datos.

- Parsear respuesta real
- Identificar campos necesarios
- Detectar variaciones (arrays vs objetos)

**Resultado:** ✅ Estructura clara / ❌ Estructura confusa

#### V3: Validación de Viabilidad
**¿Qué valida?** Que la solución propuesta es factible.

- ¿Podemos extraer los datos necesarios?
- ¿El tamaño de respuesta será manejable?
- ¿La paginación funcionará?

**Resultado:** ✅ Viable / ❌ Requiere rediseño

#### Matriz de decisión:
| V1 | V2 | V3 | Acción |
|----|----|----|--------|
| ✅ | ✅ | ✅ | Proceder a E |
| ✅ | ✅ | ❌ | Rediseñar solución |
| ✅ | ❌ | - | Más research en estructura |
| ❌ | - | - | Verificar endpoint/fecha |

#### Deliverables V:
- [ ] Resultado V1, V2, V3 documentado
- [ ] Ejemplo de respuesta real guardado
- [ ] Decisión de proceder o rediseñar

---

### FASE E: EXECUTE (Implementación) - Variable

**Objetivo:** Implementar siguiendo el diseño.

#### Checklist E-BOE-MCP:

##### E1. Validador (si aplica)
- [ ] Crear archivo `validators/xxx.py`
- [ ] Implementar función de validación
- [ ] Añadir a `validators/__init__.py`
- [ ] Tests unitarios del validador

##### E2. Herramienta MCP
- [ ] Implementar función en `server.py`
- [ ] Seguir patrón: validación → request → proceso → respuesta
- [ ] Docstring completo (propósito, args, returns, examples)
- [ ] Manejo de errores estandarizado

##### E3. Tests E2E
- [ ] Crear `tests/test_e2e_xxx.py`
- [ ] Implementar tests definidos en P
- [ ] Ejecutar y verificar que pasan

#### Patrón de implementación estándar:

```python
@mcp.tool()
async def nombre_herramienta(
    param1: str,
    param2: int = 20
) -> dict:
    """
    Descripción breve.

    Descripción detallada del propósito y casos de uso.

    Args:
        param1: Descripción con ejemplo
        param2: Descripción con default

    Returns:
        Diccionario con:
        - campo1: descripción
        - campo2: descripción

        En caso de error:
        - error: True
        - codigo: "CODIGO"
        - mensaje: descripción

    Examples:
        >>> nombre_herramienta("valor")
        {"campo1": "resultado"}
    """
    # 1. VALIDACIÓN
    try:
        param1 = validate_xxx(param1)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # 2. REQUEST A API
    endpoint = f"/datosabiertos/api/xxx/{param1}"
    data = await make_boe_request(endpoint)

    if not data:
        return {
            "error": True,
            "codigo": "XXX_NO_DISPONIBLE",
            "mensaje": f"No se pudo obtener xxx para {param1}",
            "detalles": None
        }

    # 3. PROCESAR DATOS
    resultado = procesar_datos(data)

    # 4. RETORNAR
    return resultado
```

#### Deliverables E:
- [ ] Validador implementado y testeado
- [ ] Herramienta implementada
- [ ] Tests E2E pasando

---

### FASE A: ASSESS (Evaluación) - 10-15 min

**Objetivo:** Evaluar resultado y documentar.

#### Checklist A-BOE-MCP:

##### A1. Verificación funcional
- [ ] ¿Todos los tests pasan?
- [ ] ¿La herramienta resuelve el problema original?
- [ ] ¿El tamaño de respuesta es manejable?

##### A2. Verificación de calidad
- [ ] ¿Ruff lint pasa?
- [ ] ¿Docstrings completos?
- [ ] ¿Errores bien manejados?

##### A3. Documentación
- [ ] Actualizar CHANGELOG
- [ ] Actualizar plan si hay cambios
- [ ] Documentar lecciones aprendidas

##### A4. Informe de casos de uso (opcional)
- [ ] Generar script de informe
- [ ] Ejecutar contra API real
- [ ] Guardar informe en docs/

#### Template de evaluación:

```markdown
## ASSESS: [nombre_herramienta]

### Resultado: PASS / PARTIAL / FAIL

### Métricas
- Tests E2E: X/Y pasando
- Tamaño respuesta típica: ~X KB
- Latencia típica: ~X ms

### Lecciones aprendidas
1. [Lección 1]
2. [Lección 2]

### Mejoras futuras identificadas
1. [Mejora 1]
```

#### Deliverables A:
- [ ] Evaluación documentada
- [ ] CHANGELOG actualizado
- [ ] Lecciones documentadas

---

## REGLAS CRÍTICAS RPVEA 2.0

### NUNCA:
1. ❌ Implementar sin completar R y P
2. ❌ Escribir código sin validación V
3. ❌ Asumir estructura de API sin verificar
4. ❌ Ignorar código reutilizable existente
5. ❌ Saltarse la fase A

### SIEMPRE:
1. ✅ Investigar API y código existente primero
2. ✅ Diseñar herramienta antes de implementar
3. ✅ Validar con API real antes de código
4. ✅ Reutilizar validadores y patrones
5. ✅ Documentar lecciones aprendidas

### SI ENCUENTRAS UN PROBLEMA:
1. **STOP** - No continuar sin resolver
2. **DOCUMENT** - Registrar el problema
3. **ASSESS** - ¿Es bloqueante?
4. **DECIDE** - ¿Rediseñar o workaround?
5. **TRACK** - Añadir a limitaciones conocidas si aplica

---

## QUICK START

Para implementar una nueva herramienta:

```
1. R (15 min): Leer API + código existente + definir problema
2. P (10 min): Diseñar herramienta + tests
3. V (15 min): Probar API real + validar viabilidad
4. E (variable): Implementar validador + herramienta + tests
5. A (10 min): Evaluar + documentar
```

---

## REFERENCIAS

- Framework original: `/Users/pepo/Dev/MCP-BOE-consolidada/testing_mcp_boe_consolidada/00_estructura/RPVEA_BOE_FRAMEWORK.md`
- Smart Navigation v2.0: `docs/PLAN-RPVEA-2.0-smart-navigation-v2.md`
- Validadores v1.3.0: `src/boe_mcp/validators/`
- Tests E2E ejemplo: `tests/test_e2e_smart_navigation.py`

---

**FIN DEL FRAMEWORK RPVEA 2.0 BOE-MCP**

*"Research First, Code Second"*
*"Reutilizar > Reinventar"*
