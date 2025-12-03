# Investigación: Cómo Exponer Guías de Uso en MCP

**Fecha:** 2025-12-03
**Contexto:** Necesitamos que los LLMs sepan qué herramienta usar para cada caso de uso sin tener que redescubrirlo en cada sesión.
**Documento creado:** `docs/GUIA-USO-HERRAMIENTAS.md`

---

## 1. Problema a Resolver

Tenemos una guía de uso (`GUIA-USO-HERRAMIENTAS.md`) que documenta:
- Qué herramienta usar para cada caso
- Flujos de trabajo recomendados
- Anti-patrones a evitar
- Matriz de decisión rápida

**Pregunta:** ¿Cómo hacer que esta información esté disponible para los LLMs que usan el MCP?

---

## 2. Investigación Realizada

### 2.1 Fuentes Consultadas

| Fuente | URL | Contenido relevante |
|--------|-----|---------------------|
| Especificación MCP | https://modelcontextprotocol.io/specification/2025-06-18 | Definición de primitivos |
| MCP Best Practices | https://modelcontextprotocol.info/docs/best-practices/ | Arquitectura y diseño |
| MCP Server Dev Guide | https://github.com/cyanheads/model-context-protocol-resources | Guía desarrollo |
| FastMCP Server Docs | https://gofastmcp.com/servers/server | Campo `instructions` |
| MCP Prompts Docs | https://modelcontextprotocol.io/docs/concepts/prompts | Uso de prompts |
| MCP Resources Docs | https://modelcontextprotocol.io/docs/concepts/resources | Uso de resources |
| CodeSignal MCP Guide | https://codesignal.com/learn/courses/developing-and-integrating-a-mcp-server-in-python/ | Ejemplos prácticos |

### 2.2 Los 3 Primitivos MCP

Según la especificación oficial:

| Primitivo | Propósito | Quién controla | Analogía |
|-----------|-----------|----------------|----------|
| **Tools** | Ejecutar acciones | LLM decide cuándo llamar | POST/PUT endpoints |
| **Resources** | Proveer contexto/datos | Aplicación decide qué exponer | GET endpoints |
| **Prompts** | Plantillas de conversación | Usuario selecciona explícitamente | Formularios predefinidos |

**Cita de la spec:**
> "Resources allow servers to share data that provides context to language models, such as files, database schemas, or application-specific information."

> "Prompts are pre-defined prompt templates or workflows for users."

---

## 3. Opciones Identificadas

### Opción 1: Campo `instructions` del servidor

**Qué es:** Parámetro del constructor de FastMCP que se envía al cliente durante la inicialización.

**Implementación:**
```python
mcp = FastMCP(
    name="boe-mcp",
    instructions="""
    BOE-MCP: Servidor para consultar el Boletín Oficial del Estado.

    DECISIÓN RÁPIDA DE HERRAMIENTAS:

    Para sumarios BOE:
    - Vista general del día → get_boe_summary_metadata
    - Documentos de una sección → get_boe_summary_section
    - Detalles de un documento → get_boe_document_info
    - NO usar get_boe_summary (devuelve 300KB+)

    Para legislación consolidada:
    - Buscar leyes → search_laws_list
    - Estructura de ley → get_law_structure_summary
    - Texto de artículo → get_article_info
    - Buscar en ley → search_in_law
    """
)
```

**Ventajas:**
- Siempre visible para el LLM desde el inicio
- No requiere acción del usuario
- Conciso y directo

**Desventajas:**
- Limitado en tamaño (no para documentación extensa)
- No se puede actualizar sin reiniciar servidor

**Cuándo usar:** Matriz de decisión rápida, reglas críticas.

---

### Opción 2: Resource MCP

**Qué es:** Exponer datos como "recurso" que el LLM puede leer bajo demanda.

**Implementación:**
```python
@mcp.resource("guide://herramientas")
def get_usage_guide() -> str:
    """Guía completa de uso de herramientas BOE-MCP"""
    with open("docs/GUIA-USO-HERRAMIENTAS.md") as f:
        return f.read()

# O versión inline:
@mcp.resource("guide://decision-matrix")
def get_decision_matrix() -> str:
    """Matriz de decisión rápida para selección de herramientas"""
    return """
    | Necesito... | Herramienta |
    |-------------|-------------|
    | Vista general del BOE del día | get_boe_summary_metadata |
    | Documentos de una sección | get_boe_summary_section |
    ...
    """
```

**Ventajas:**
- Puede ser extenso (documentación completa)
- Carga bajo demanda (no consume contexto siempre)
- Puede leer archivos externos

**Desventajas:**
- El LLM debe saber que existe y solicitarlo
- No es automático

**Cuándo usar:** Documentación detallada, guías completas, ejemplos extensos.

---

### Opción 3: Prompts MCP

**Qué es:** Plantillas de conversación predefinidas que el usuario selecciona.

**Implementación:**
```python
@mcp.prompt("explorar-boe-diario")
def daily_boe_prompt() -> str:
    """Flujo guiado para explorar el BOE de un día"""
    return """
    Para explorar el BOE del día, sigue estos pasos:

    1. Primero obtén el resumen con get_boe_summary_metadata(fecha)
       - Esto te dará las 8 secciones y cuántos documentos hay en cada una

    2. Pregunta al usuario qué sección le interesa

    3. Usa get_boe_summary_section(fecha, seccion, limit=10) para ver los documentos

    4. Si el usuario quiere detalles de un documento específico:
       get_boe_document_info(identificador)
    """

@mcp.prompt("buscar-ley")
def search_law_prompt() -> str:
    """Flujo guiado para buscar y explorar una ley"""
    return """
    Para buscar una ley específica:

    1. Usa search_laws_list con los filtros apropiados:
       - numero_oficial="39/2015" para buscar por número
       - query_value="protección datos" para buscar por tema
       - solo_vigente=True para filtrar solo vigentes

    2. Una vez identificada la ley, usa get_law_structure_summary(identifier)
       para ver su estructura

    3. Para un artículo específico: get_article_info(identifier, articulo)
    """
```

**Ventajas:**
- Flujos de trabajo predefinidos
- El usuario tiene control explícito
- Ideal para tareas complejas multi-paso

**Desventajas:**
- Requiere que el usuario lo seleccione activamente
- No es automático para el LLM
- Depende del cliente MCP soportar prompts

**Cuándo usar:** Flujos de trabajo guiados, tutoriales interactivos.

---

### Opción 4: Docstrings mejorados (ya implementado)

**Qué es:** Documentación detallada en cada herramienta.

**Implementación actual:**
```python
@mcp.tool()
async def get_boe_summary_metadata(fecha: str) -> dict:
    """
    Obtener resumen compacto del sumario BOE con conteo por sección.

    Esta herramienta proporciona una vista general del BOE de un día específico,
    mostrando cuántos documentos hay en cada sección. Es la herramienta recomendada
    como primer paso para explorar el BOE del día.

    NOTA: Para obtener los documentos de una sección específica, usar
    get_boe_summary_section después de esta herramienta.
    ...
    """
```

**Ventajas:**
- Ya lo tenemos
- Contexto específico por herramienta
- El LLM lo ve al listar herramientas

**Desventajas:**
- Fragmentado (no hay visión global)
- No explica flujos entre herramientas

**Cuándo usar:** Siempre, como complemento.

---

## 4. Comparativa de Opciones

| Aspecto | instructions | Resource | Prompt | Docstrings |
|---------|-------------|----------|--------|------------|
| **Visibilidad** | Siempre | Bajo demanda | Usuario selecciona | Al listar tools |
| **Tamaño** | Corto (~500 chars) | Ilimitado | Medio | Medio |
| **Automatismo** | Automático | LLM debe pedir | Usuario activa | Automático |
| **Actualización** | Reinicio server | Puede leer archivo | Reinicio server | Reinicio server |
| **Soporte clientes** | Universal | Variable | Variable | Universal |

---

## 5. Recomendación Propuesta

**Estrategia combinada:**

1. **`instructions`** (obligatorio):
   - Matriz de decisión rápida (15-20 líneas)
   - Reglas críticas (ej: "NO usar get_boe_summary")
   - Se ve siempre

2. **`resource`** (recomendado):
   - Guía completa (`GUIA-USO-HERRAMIENTAS.md`)
   - El LLM puede consultarla si necesita más contexto
   - URI: `guide://herramientas`

3. **Docstrings** (mantener):
   - Ya implementados
   - Contexto específico por herramienta

4. **Prompts** (opcional, fase posterior):
   - Para flujos complejos si se identifica necesidad
   - Requiere más testing con diferentes clientes

---

## 6. Plan de Implementación

### Fase 1: instructions (inmediato)
- [ ] Actualizar constructor de FastMCP con instructions
- [ ] Incluir matriz de decisión rápida
- [ ] Probar con Claude Desktop

### Fase 2: Resource (siguiente)
- [ ] Añadir resource `guide://herramientas`
- [ ] Verificar que el archivo se lee correctamente
- [ ] Probar si LLM lo solicita cuando necesita contexto

### Fase 3: Evaluación
- [ ] Documentar comportamiento observado
- [ ] Comparar efectividad de cada opción
- [ ] Ajustar según resultados

---

## 7. Preguntas Abiertas

1. ¿Los clientes MCP (Claude Desktop, etc.) muestran los resources al LLM automáticamente o requiere configuración?

2. ¿El tamaño de `instructions` tiene un límite práctico? ¿Cuánto es "demasiado"?

3. ¿Los prompts MCP funcionan bien con Claude Desktop o solo con algunos clientes?

4. ¿Sería útil tener un resource dinámico que muestre solo las herramientas relevantes según el contexto?

---

## 8. Referencias

- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18)
- [FastMCP Server Documentation](https://gofastmcp.com/servers/server)
- [MCP Best Practices](https://modelcontextprotocol.info/docs/best-practices/)
- [MCP Resources Concept](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Prompts Concept](https://modelcontextprotocol.io/docs/concepts/prompts)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)

---

**Estado:** Investigación completada. Pendiente decisión sobre implementación.
