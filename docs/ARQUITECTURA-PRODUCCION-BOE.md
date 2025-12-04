# Arquitectura de Producción BOE-MCP

## Estado del Documento

| Campo | Valor |
|-------|-------|
| Versión | 1.0 |
| Fecha | 2025-12-04 |
| Estado | Investigación/Propuesta |
| Rama | feature/smart-navigation-v2 |

## 1. Contexto y Problema

### 1.1 Situación Actual

BOE-MCP es un servidor MCP que expone herramientas para consultar el BOE. El problema identificado es el **consumo excesivo de tokens** cuando se usa en conversaciones con LLMs.

#### Mediciones de Respuesta (Tool Results)

| Herramienta | Tamaño Respuesta | Observaciones |
|-------------|------------------|---------------|
| `get_boe_summary` (original) | ~149.5 KB | Bloquea ventana de contexto |
| `get_boe_summary_metadata` | ~450 bytes | 330x más pequeño |
| `get_boe_summary_section` | ~2.7 KB | 55x más pequeño |
| `get_boe_document_info` | ~225 bytes | 660x más pequeño |

### 1.2 Impacto en Producción

Los `tool_results` en las APIs de LLM **cuentan como input tokens**, consumiendo la ventana de contexto disponible.

## 2. Investigación de Límites de APIs

### 2.1 Claude API (Anthropic)

**Fuente**: https://docs.anthropic.com/en/docs/build-with-claude/context-windows

| Modelo | Contexto | Output Máximo |
|--------|----------|---------------|
| Claude Sonnet 4 | 200K tokens | 16K tokens |
| Claude Opus 4 | 200K tokens | 32K tokens |
| Claude 3.5 Sonnet | 200K tokens | 8K tokens |

**Consideraciones clave**:
- Los `tool_results` cuentan como input tokens
- Extended thinking puede consumir tokens adicionales
- No hay "streaming" para reducir consumo en MCP

### 2.2 Gemini API (Google)

**Fuente**: https://ai.google.dev/gemini-api/docs

| Modelo | Contexto | Notas |
|--------|----------|-------|
| Gemini 2.0 Flash | 1M tokens | Modelo más reciente disponible |
| Gemini 1.5 Pro | 2M tokens | Mayor contexto disponible |

**Notas**:
- Google anunció "Gemini 3" pero no está disponible públicamente aún
- Gemini 2.0 incluye soporte nativo MCP desde diciembre 2024
- Mayor contexto = más margen pero mismo problema fundamental

### 2.3 Conclusión de Investigación

El problema de consumo de tokens existe en todas las APIs. La solución no es buscar más contexto, sino **reducir el tamaño de las respuestas**.

## 3. Arquitectura de Producción Propuesta

### 3.1 Diagrama Conceptual

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENTE DE CHAT                             │
│  (Web App con autenticación, gestión de sesiones, UI)           │
└─────────────────────────────┬───────────────────────────────────┘
                              │ API REST / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP ORCHESTRATOR                              │
│  - Gestión de herramientas MCP                                  │
│  - Ruteo inteligente de consultas                               │
│  - Caché de resultados                                          │
│  - Rate limiting                                                │
└─────────┬───────────────────────────────────────────┬───────────┘
          │                                           │
          ▼                                           ▼
┌─────────────────────┐                 ┌─────────────────────────┐
│   BOE DOWNLOADER    │                 │    LOCAL DATABASE       │
│  - Descarga BOE     │    ETL          │  - Neo4j (grafos)       │
│  - Caché local      │ ───────────────▶│  - Elasticsearch (FTS)  │
│  - Actualización    │                 │  - Índices legales      │
│    programada       │                 │  - Relaciones entre     │
└─────────────────────┘                 │    normas               │
                                        └─────────────────────────┘
```

### 3.2 Componentes

#### 3.2.1 Cliente de Chat
- **Función**: Interface de usuario con autenticación
- **Tecnología sugerida**: Next.js, React, o similar
- **Responsabilidades**:
  - Gestión de sesiones de usuario
  - Historial de conversaciones
  - UI para interacción con LLM

#### 3.2.2 MCP Orchestrator
- **Función**: Backend que coordina MCP y LLM
- **Responsabilidades**:
  - Recibe queries del cliente
  - Decide si usar BOE API directa o BBDD local
  - Caché de resultados frecuentes
  - Rate limiting y control de costes

#### 3.2.3 BOE Downloader
- **Función**: Descarga y mantiene copia local del BOE
- **Características**:
  - Descarga incremental diaria
  - Almacenamiento estructurado
  - Versionado de documentos

#### 3.2.4 ETL (Extract, Transform, Load)
- **Función**: Procesa documentos BOE para BBDD local
- **Transformaciones**:
  - Extracción de metadatos
  - Parsing de estructura legal
  - Identificación de relaciones entre normas
  - Indexación full-text

#### 3.2.5 Local Database
- **Neo4j**: Para relaciones entre normas (modifica, deroga, etc.)
- **Elasticsearch**: Para búsqueda full-text eficiente
- **Beneficio**: Búsquedas locales = respuestas pequeñas = menos tokens

### 3.3 Flujo de Operación

```
1. Usuario pregunta: "¿Qué dice el artículo 15 de la LOPD?"

2. MCP Orchestrator:
   - Identifica: necesita buscar LOPD
   - Consulta BBDD local (no BOE API)
   - Respuesta: ~500 bytes (solo artículo 15)

3. LLM procesa respuesta pequeña

4. Resultado: Conversación fluida sin agotar contexto
```

### 3.4 Ventajas

| Aspecto | BOE API Directa | Arquitectura Local |
|---------|-----------------|-------------------|
| Latencia | ~500ms-2s | ~50ms |
| Tamaño respuesta | 10KB-150KB | 200B-2KB |
| Disponibilidad | Depende de BOE | 99.9% local |
| Coste tokens | Alto | Bajo |
| Actualización | Tiempo real | Diaria (configurable) |

## 4. Tareas Pendientes

### 4.1 Mejoras Inmediatas (v1.5.x)

- [ ] Reducir defaults de `limit` en herramientas (20→10, 100→20)
- [ ] Implementar herramientas BORME equivalentes a Smart Summary
- [ ] Decidir estrategia de guías de uso MCP (instructions vs resources)
- [ ] Considerar truncado automático de respuestas largas

### 4.2 Arquitectura de Producción (v2.x)

- [ ] Diseñar schema Neo4j para legislación
- [ ] Implementar BOE Downloader
- [ ] Crear pipeline ETL
- [ ] Desarrollar MCP Orchestrator
- [ ] Integrar con cliente de chat

### 4.3 Investigación Adicional

- [ ] Evaluar costes de Neo4j AuraDB vs self-hosted
- [ ] Analizar Elasticsearch vs Meilisearch vs Typesense
- [ ] Estudiar streaming de respuestas MCP (si existe)
- [ ] Investigar compresión de tool_results

## 5. Referencias

### 5.1 Documentación Oficial

- [Claude API - Context Windows](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)
- [Claude API - Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [MCP Specification](https://modelcontextprotocol.io/)

### 5.2 Documentación del Proyecto

- [PLAN-SMART-SUMMARY.md](./PLAN-SMART-SUMMARY.md) - Implementación Smart Summary
- [GUIA-USO-HERRAMIENTAS.md](./GUIA-USO-HERRAMIENTAS.md) - Guía de uso
- [LIMITACIONES-CONOCIDAS.md](./LIMITACIONES-CONOCIDAS.md) - Limitaciones

## 6. Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2025-12-04 | 1.0 | Documento inicial con investigación y propuesta |
