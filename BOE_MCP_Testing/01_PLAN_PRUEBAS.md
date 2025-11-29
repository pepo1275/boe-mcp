# 📋 PLAN DE PRUEBAS COMPLETO - BOE-MCP

**Versión:** 1.0  
**Fecha:** 2025-11-23  
**Ubicación:** `/Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/`  

---

## 🎯 OBJETIVO

Realizar una evaluación exhaustiva del servidor MCP **boe-mcp** mediante un banco de pruebas estructurado que progrese desde funcionalidades básicas hasta casos de uso avanzados, con documentación completa para garantizar trazabilidad y reproducibilidad.

---

## 📊 ALCANCE

### Tests Totales: 32
- **Nivel 1:** 4 tests (Funcionalidad Básica)
- **Nivel 2:** 5 tests (Búsqueda y Filtrado)
- **Nivel 3:** 5 tests (Navegación y Estructura)
- **Nivel 4:** 6 tests (Análisis y Relaciones)
- **Nivel 5:** 6 tests (Casos de Uso Reales)
- **Nivel 6:** 6 tests (Estrés y Límites)

### Estrategias de Ejecución:
1. **Evaluación Rápida** (30 min): Nivel 1 completo + samples
2. **Evaluación Completa** (3 horas): Todos los niveles
3. **Casos de Uso** (1 hora): Solo Nivel 5

---

## 🗂️ ESTRUCTURA DE DOCUMENTACIÓN

```
BOE_MCP_Testing/
├── 00_MASTER_INDEX.md           # Este archivo - índice maestro
├── 01_PLAN_PRUEBAS.md           # Plan detallado (este documento)
├── Nivel_X_[Nombre]/
│   ├── README_Nivel_X.md
│   ├── Test_X.Y_[Nombre]/
│   │   ├── 00_metadata.json
│   │   ├── 01_request.json
│   │   ├── 02_response_raw.json
│   │   ├── 03_response_parsed.md
│   │   ├── 04_evaluation.md
│   │   └── 05_screenshots/
│   └── INFORME_NIVEL_X.md
├── Datos_Capturados/
│   ├── BOE_Sumarios/
│   ├── Normas_Completas/
│   ├── Metadatos_Cache/
│   └── Tablas_Auxiliares/
├── Scripts_Utilidad/
│   ├── generate_report.py
│   ├── compare_mcps.py
│   └── validate_responses.py
├── Informes_Estrategias/
│   ├── Estrategia_1_Evaluacion_Rapida.md
│   ├── Estrategia_2_Evaluacion_Completa.md
│   └── Estrategia_3_Casos_Uso.md
├── .checkpoints/
│   ├── CHECKPOINT_LATEST.md
│   ├── CHECKPOINT_NIVEL_1.md
│   ├── CHECKPOINT_NIVEL_2.md
│   └── [...]
└── INFORME_FINAL_COMPLETO.md
```

---

## 📝 ARCHIVOS POR TEST

Cada test genera 5 archivos principales:

### 1. `00_metadata.json`
```json
{
  "test_id": "X.Y",
  "test_name": "Nombre descriptivo",
  "nivel": X,
  "categoria": "Categoría del nivel",
  "objetivo": "Objetivo específico del test",
  "herramienta_mcp": "boe-mcp:tool_name",
  "timestamp_inicio": "ISO 8601",
  "timestamp_fin": "ISO 8601",
  "duracion_ms": 1234,
  "device_id": "device_identifier",
  "ejecutor": "Claude Sonnet 4.5",
  "estado": "exitoso|parcial|fallido",
  "score": 1-5,
  "notas": "Observaciones relevantes"
}
```

### 2. `01_request.json`
```json
{
  "mcp_server": "boe-mcp",
  "tool_name": "nombre_herramienta",
  "parameters": {
    // parámetros específicos
  },
  "timestamp": "ISO 8601"
}
```

### 3. `02_response_raw.json`
```json
{
  "mcp_response": {
    // respuesta cruda del MCP
  },
  "http_status": 200,
  "response_time_ms": 1234,
  "response_size_bytes": 56789
}
```

### 4. `03_response_parsed.md`
- Resumen ejecutivo
- Datos relevantes extraídos
- Archivos generados
- Formato legible

### 5. `04_evaluation.md`
- Criterios de éxito (✅/⚠️/❌)
- Score detallado con peso
- Comparación con expectativas
- Observaciones técnicas

---

## 🔄 SISTEMA DE CHECKPOINTS

### Propósito
Permitir continuidad entre sesiones de Claude Desktop y Claude Code sin pérdida de contexto.

### Ubicación
`.checkpoints/CHECKPOINT_[IDENTIFICADOR].md`

### Contenido de cada Checkpoint
```markdown
# CHECKPOINT: [Identificador]

**Timestamp:** 2025-11-23T12:44:04Z  
**Device:** macbook-air-de-pepo_macos_pepo_001  
**Última acción:** [Descripción]  

## 📊 Estado Actual
- Tests ejecutados: X/32
- Último test completado: X.Y
- Score acumulado: X.X/5

## 🎯 Próxima Acción
[Descripción precisa de qué hacer]

## 📁 Archivos Relevantes
- [Lista de archivos creados desde último checkpoint]

## 🔄 Para Continuar (Claude Desktop)
```
Lee este checkpoint y ejecuta: [comando específico]
```

## 🔄 Para Continuar (Claude Code)
```bash
cat /Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/.checkpoints/CHECKPOINT_LATEST.md
# Luego ejecutar: [comando específico]
```

## 📝 Contexto Completo
[Resumen de lo realizado hasta ahora]

## ⚠️ Pendientes
- [ ] Acción pendiente 1
- [ ] Acción pendiente 2
```

### Frecuencia de Checkpoints
- Después de cada test completado → `.checkpoints/CHECKPOINT_TEST_X_Y.md`
- Al completar cada nivel → `.checkpoints/CHECKPOINT_NIVEL_X.md`
- Al cambiar de estrategia → `.checkpoints/CHECKPOINT_ESTRATEGIA_X.md`
- Siempre actualizar → `.checkpoints/CHECKPOINT_LATEST.md`

---

## 📊 SISTEMA DE SCORING

### Por Test (1-5 puntos)
- **5/5** - Excelente: Supera expectativas
- **4/5** - Bueno: Cumple expectativas
- **3/5** - Aceptable: Cumple mínimo
- **2/5** - Deficiente: No cumple esperado
- **1/5** - Muy deficiente: Casi inutilizable

### Criterios por Dimensión

**Funcionalidad (40%)**
- Herramienta responde sin errores
- Datos coherentes con API BOE
- Manejo correcto de edge cases

**Rendimiento (20%)**
- Tiempo de respuesta adecuado
- Uso eficiente de recursos
- Escalabilidad

**Usabilidad (20%)**
- Nombres intuitivos
- Parámetros bien documentados
- Mensajes de error claros

**Completitud (20%)**
- Cobertura de funcionalidad
- Formatos soportados
- Features disponibles

---

## 🎯 NIVELES DETALLADOS

### NIVEL 1: FUNCIONALIDAD BÁSICA (4 tests)
**Objetivo:** Verificar instalación y operaciones fundamentales

1. **Test 1.1:** Verificar herramientas disponibles
2. **Test 1.2:** Búsqueda simple por texto
3. **Test 1.3:** Obtener metadatos de norma
4. **Test 1.4:** Sumario BOE fecha reciente

**Duración estimada:** 10 minutos

### NIVEL 2: BÚSQUEDA Y FILTRADO (5 tests)
**Objetivo:** Evaluar capacidades de consulta y filtrado

1. **Test 2.1:** Filtros temporales (from_date, to_date)
2. **Test 2.2:** Filtro por ámbito (Estatal/Autonómico)
3. **Test 2.3:** Búsqueda en título vs texto completo
4. **Test 2.4:** Filtrar solo consolidadas
5. **Test 2.5:** Operadores lógicos (must/should/must_not)

**Duración estimada:** 20 minutos

### NIVEL 3: NAVEGACIÓN Y ESTRUCTURA (5 tests)
**Objetivo:** Explorar documentos y su estructura interna

1. **Test 3.1:** Obtener índice de norma
2. **Test 3.2:** Leer bloque específico (artículo)
3. **Test 3.3:** Obtener disposiciones adicionales
4. **Test 3.4:** Texto completo consolidado
5. **Test 3.5:** Comparar formatos XML vs JSON

**Duración estimada:** 25 minutos

### NIVEL 4: ANÁLISIS Y RELACIONES (6 tests)
**Objetivo:** Analizar conexiones y metadatos avanzados

1. **Test 4.1:** Metadatos de análisis
2. **Test 4.2:** Metadatos ELI
3. **Test 4.3:** Tabla auxiliar - Materias
4. **Test 4.4:** Tabla auxiliar - Departamentos
5. **Test 4.5:** Tabla auxiliar - Rangos
6. **Test 4.6:** Relaciones entre normas

**Duración estimada:** 30 minutos

### NIVEL 5: CASOS DE USO REALES (6 tests)
**Objetivo:** Aplicaciones prácticas del sistema

1. **Caso 5.1:** Investigador - Timeline legislativo
2. **Caso 5.2:** Abogado - Validación vigencia
3. **Caso 5.3:** Consultor - Impacto reforma
4. **Caso 5.4:** Periodista - Monitoreo diario
5. **Caso 5.5:** Desarrollador - Sistema RAG
6. **Caso 5.6:** Funcionario - Comparativa autonómica

**Duración estimada:** 60 minutos

### NIVEL 6: ESTRÉS Y LÍMITES (6 tests)
**Objetivo:** Probar robustez y límites del sistema

1. **Test 6.1:** Búsqueda masiva - Paginación
2. **Test 6.2:** Consultas simultáneas
3. **Test 6.3:** Documento extremadamente grande
4. **Test 6.4:** Consulta BORME (si disponible)
5. **Test 6.5:** Caracteres especiales
6. **Test 6.6:** Norma sin consolidar

**Duración estimada:** 30 minutos

---

## 📈 MÉTRICAS DE ÉXITO

### Global
- ✅ **85%+ tests exitosos** (27/32)
- ✅ **Score global ≥ 4.0/5**
- ✅ **Tiempo total < 3.5 horas**

### Por Nivel
- ✅ Al menos 75% tests exitosos por nivel
- ✅ Score promedio ≥ 3.5/5 por nivel
- ✅ Documentación completa generada

### Cobertura
- ✅ Todos los endpoints API BOE probados
- ✅ Tablas auxiliares completas
- ✅ Formatos XML y JSON verificados

---

## 🛠️ SCRIPTS DE UTILIDAD

### `generate_report.py`
Consolida todos los `metadata.json` y `evaluation.md` para generar informes automáticos.

### `compare_mcps.py`
Compara resultados de boe-mcp con MCP-BOE-consolidada (para futura evaluación comparativa).

### `validate_responses.py`
Valida estructura y coherencia de respuestas JSON/XML contra esquema esperado.

---

## 📅 CRONOGRAMA

### Fase 1: Setup (Completado)
- ✅ Estructura de directorios
- ✅ Documentación base
- ✅ Sistema de checkpoints

### Fase 2: Nivel 1 (En progreso)
- ⏳ Test 1.1 - 1.4
- ⏳ Informe Nivel 1

### Fase 3: Estrategia 1 (Pendiente)
- ⏳ Samples Nivel 2-5
- ⏳ Informe Estrategia 1

### Fase 4: Evaluación Completa (Opcional)
- ⏳ Niveles 2-6 completos
- ⏳ Informe Final

---

## 🔄 COMANDOS DE CONTINUIDAD

### Desde Claude Desktop
```
Lee el archivo: /Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/.checkpoints/CHECKPOINT_LATEST.md
Luego continúa con la próxima acción indicada
```

### Desde Claude Code
```bash
# Ver estado actual
cat /Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/00_MASTER_INDEX.md

# Ver último checkpoint
cat /Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/.checkpoints/CHECKPOINT_LATEST.md

# Ver estructura
tree -L 2 /Users/pepo/Dev/boe-mcp/BOE_MCP_Testing/
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Checkpoints frecuentes:** Después de cada test y cada nivel
2. **Respaldos automáticos:** Todos los datos capturados se guardan
3. **Continuidad garantizada:** Sistema diseñado para alternar entre Claude Desktop y Code
4. **Trazabilidad completa:** Cada decisión y resultado documentado
5. **Reproducibilidad:** Cualquier test puede repetirse con mismos parámetros

---

*Documento vivo - Se actualiza conforme progresa la evaluación*
