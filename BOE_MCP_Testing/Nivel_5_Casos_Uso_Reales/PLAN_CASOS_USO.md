# Plan: Nivel 5 - Casos de Uso Reales

**Fecha:** 2025-11-26
**Objetivo:** Validar el MCP boe-mcp en escenarios de uso real

---

## 📋 Casos de Uso Seleccionados (3)

### Caso 5.1: Investigador Jurídico - Timeline Legislativo
**Perfil:** Investigador necesita rastrear evolución de legislación sobre un tema

**Escenario:**
1. Buscar todas las normas sobre "protección de datos" desde 2018
2. Filtrar solo Leyes Orgánicas
3. Obtener texto consolidado de la principal
4. Identificar modificaciones posteriores

**Herramientas MCP usadas:**
- `search_laws_list` (con filtros temporales y texto)
- `get_law_section` (texto consolidado)
- Análisis de resultados

**Criterios de éxito:**
- ✅ Búsqueda temporal funciona
- ✅ Filtrado por rango funciona
- ✅ Texto consolidado accesible
- ✅ Resultados relevantes y completos

**Duración estimada:** 15-20 minutos

---

### Caso 5.2: Abogado - Validación de Vigencia
**Perfil:** Abogado necesita verificar si una norma específica está vigente y consolidada

**Escenario:**
1. Buscar norma específica por ID BOE (ej: BOE-A-2015-10566)
2. Obtener metadatos completos
3. Verificar estado de consolidación
4. Obtener sumario BOE del día de publicación

**Herramientas MCP usadas:**
- `search_laws_list` (búsqueda específica)
- `get_law_section` (metadatos)
- `get_boe_summary` (fecha publicación)

**Criterios de éxito:**
- ✅ Búsqueda por ID precisa
- ✅ Metadatos incluyen estado consolidación
- ✅ Fecha de publicación verificable
- ✅ Información clara sobre vigencia

**Duración estimada:** 10-15 minutos

---

### Caso 5.3: Desarrollador - Sistema RAG Legal
**Perfil:** Desarrollador construyendo sistema RAG para consultas legales

**Escenario:**
1. Búsqueda por materia específica (ej: "tributario")
2. Recuperar múltiples normas relacionadas
3. Obtener estructura (índice) de cada norma
4. Extraer bloques específicos (artículos clave)

**Herramientas MCP usadas:**
- `search_laws_list` (con matter_code)
- `get_law_section` (índice + bloques)
- `get_auxiliary_table` (códigos materias)

**Criterios de éxito:**
- ✅ Búsqueda por materia funciona
- ✅ Múltiples resultados manejables
- ✅ Índice estructurado disponible
- ✅ Extracción granular de contenido

**Duración estimada:** 15-20 minutos

---

## 📊 Resumen

| Caso | Perfil | Complejidad | Duración | Herramientas |
|------|--------|-------------|----------|--------------|
| 5.1 | Investigador | Media | 15-20 min | 2 tools |
| 5.2 | Abogado | Baja-Media | 10-15 min | 3 tools |
| 5.3 | Desarrollador | Alta | 15-20 min | 3 tools |

**Duración total estimada:** 40-55 minutos

---

## 🎯 Valor de estos casos

1. **Caso 5.1** - Valida flujo temporal y filtrado avanzado
2. **Caso 5.2** - Valida precisión y metadatos de confianza
3. **Caso 5.3** - Valida integración en sistemas automatizados

Estos 3 casos cubren los principales perfiles de usuario y flujos de trabajo del MCP.

---

**Próximo paso:** Ejecutar Caso 5.1 - Investigador Jurídico
