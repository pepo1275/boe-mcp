# NIVEL 1: FUNCIONALIDAD BÁSICA

**Objetivo:** Verificar instalación y operaciones fundamentales del servidor boe-mcp  
**Tests totales:** 4  
**Duración estimada:** 10 minutos  

---

## 📊 Estado del Nivel

| Test | Nombre | Estado | Score | Duración |
|------|--------|--------|-------|----------|
| 1.1 | Verificar herramientas | ⏳ Pendiente | - | - |
| 1.2 | Búsqueda simple | ⏳ Pendiente | - | - |
| 1.3 | Obtener metadatos | ⏳ Pendiente | - | - |
| 1.4 | Sumario BOE | ⏳ Pendiente | - | - |

**Progreso:** 0/4 (0%)  
**Score promedio:** -/5  
**Tiempo total:** 0 minutos  

---

## 🎯 Tests Incluidos

### Test 1.1: Verificar Disponibilidad de Herramientas

**Objetivo:** Confirmar que el servidor está operativo y listar herramientas

**Herramienta MCP:** `boe-mcp` (listar herramientas disponibles)

**Parámetros:** Ninguno

**Expectativa:**
- ✅ Servidor responde sin errores
- ✅ Lista ~14 herramientas disponibles
- ✅ Nombres coherentes con documentación

**Criterios de éxito:**
- Respuesta exitosa del servidor
- Al menos 10 herramientas listadas
- Formato de respuesta válido

---

### Test 1.2: Búsqueda Simple por Texto

**Objetivo:** Búsqueda básica de una ley conocida sin filtros avanzados

**Herramienta MCP:** `boe-mcp:search_laws_list`

**Parámetros:**
```json
{
  "query_value": "Ley 40/2015",
  "limit": 5
}
```

**Expectativa:**
- ✅ Encuentra la Ley 40/2015 (Régimen Jurídico del Sector Público)
- ✅ Resultado relevante en primeras posiciones
- ✅ Metadatos básicos correctos (título, fecha, BOE-A)

**Criterios de éxito:**
- Al menos 1 resultado relevante
- Identificador BOE-A-2015-10566 presente
- Tiempo de respuesta < 5 segundos

---

### Test 1.3: Obtener Metadatos de una Norma

**Objetivo:** Recuperar información básica de una ley específica

**Herramienta MCP:** `boe-mcp:get_law_section`

**Parámetros:**
```json
{
  "identifier": "BOE-A-2015-10566",
  "section": "metadatos"
}
```

**Expectativa:**
- ✅ Título completo de la norma
- ✅ Fecha de publicación
- ✅ Departamento emisor
- ✅ Rango normativo
- ✅ Estado de vigencia

**Criterios de éxito:**
- Respuesta con estructura JSON/XML válida
- Al menos 5 campos de metadatos
- Datos coherentes con BOE oficial

---

### Test 1.4: Sumario BOE de Fecha Reciente

**Objetivo:** Verificar acceso a publicaciones diarias del BOE

**Herramienta MCP:** `boe-mcp:get_boe_summary`

**Parámetros:**
```json
{
  "fecha": "20241122"
}
```

**Expectativa:**
- ✅ Lista de documentos publicados ese día
- ✅ Estructura por secciones (Disposiciones Generales, etc.)
- ✅ Enlaces/identificadores de documentos

**Criterios de éxito:**
- Respuesta con al menos 1 documento
- Secciones identificadas claramente
- Formato estructurado (XML/JSON)

---

## 📈 Métricas de Éxito del Nivel

### Funcionalidad (40%)
- [ ] Todas las herramientas responden
- [ ] Búsqueda básica funciona
- [ ] Metadatos accesibles
- [ ] Sumarios descargables

### Rendimiento (20%)
- [ ] Búsquedas < 5 segundos
- [ ] Metadatos < 3 segundos
- [ ] Sumarios < 3 segundos

### Usabilidad (20%)
- [ ] Nombres de herramientas claros
- [ ] Parámetros intuitivos
- [ ] Respuestas bien estructuradas

### Completitud (20%)
- [ ] Datos completos en respuestas
- [ ] Sin errores críticos
- [ ] Formatos válidos (JSON/XML)

---

## 🎯 Objetivo del Score

- **Mínimo aceptable:** 3.0/5 (60%)
- **Objetivo:** 4.0/5 (80%)
- **Excelente:** 4.5+/5 (90%+)

---

## 📁 Estructura de Archivos

Cada test genera su propio directorio con documentación completa:

```
Test_1.1_Verificar_Herramientas/
├── 00_metadata.json              # Metadatos del test
├── 01_request.json               # Parámetros enviados
├── 02_response_raw.json          # Respuesta cruda
├── 03_response_parsed.md         # Respuesta parseada
└── 04_evaluation.md              # Evaluación detallada
```

---

## 🔄 Próximos Pasos

1. ✅ README creado
2. ⏳ Ejecutar Test 1.1
3. ⏳ Ejecutar Test 1.2
4. ⏳ Ejecutar Test 1.3
5. ⏳ Ejecutar Test 1.4
6. ⏳ Generar INFORME_NIVEL_1.md
7. ⏳ Actualizar MASTER_INDEX.md
8. ⏳ Crear CHECKPOINT_NIVEL_1.md

---

## 🔗 Enlaces

- [Volver al Master Index](../00_MASTER_INDEX.md)
- [Ver Plan de Pruebas](../01_PLAN_PRUEBAS.md)
- [Informe del Nivel 1](INFORME_NIVEL_1.md) *(se generará al completar)*

---

*Última actualización: 2025-11-23T12:44:04Z*
