# Evaluación Test 2.3: Búsqueda en Título vs Texto Completo

## Criterios de Éxito

| Criterio | Esperado | Resultado | Estado |
|----------|----------|-----------|--------|
| search_in_title_only=true | Resultados específicos | ✅ 4 normas IA | ✅ |
| search_in_title_only=false | Resultados más amplios | ✅ 5 normas distintas | ✅ |
| Resultados diferentes | Distintos conjuntos | ✅ Conjuntos diferentes | ✅ |
| Sin errores | Sin excepciones | ✅ Sin errores | ✅ |

## Resultados

### Búsqueda en TÍTULO ("inteligencia artificial")
| Identificador | Título | Relevancia |
|---------------|--------|------------|
| BOE-A-2023-18911 | Estatuto Agencia Supervisión IA | Alta - directo |
| BOE-A-2023-8795 | Decreto-ley impulso IA Extremadura | Alta - directo |
| BOE-A-2023-16284 | Resolución firma electrónica | Media - Secretaría IA |
| BOE-A-2021-13749 | Norma Técnica Interoperabilidad | Media - Secretaría IA |

### Búsqueda en TEXTO COMPLETO ("inteligencia artificial")
| Identificador | Título | Relevancia IA |
|---------------|--------|---------------|
| BOE-A-2015-11430 | Estatuto Trabajadores | Baja - menciona en texto |
| BOE-A-2023-23537 | Reestructuración ministerios | Media - menciona secretaría |
| BOE-A-2022-23048 | PAC pagos directos | Baja - menciona en contexto |
| BOE-A-2024-7035 | Subvenciones formación agro | Baja - menciona en texto |
| BOE-A-2022-23047 | Sistema gestión PAC | Baja - menciona en texto |

## Observaciones

1. **Título only**: Normas cuyo tema principal es IA
2. **Texto completo**: Normas que mencionan IA en cualquier parte del contenido
3. **Utilidad clara**: Para investigación específica usar título, para análisis transversal usar texto completo

## Query Construido

- Título: `titulo:(inteligencia artificial) and vigencia_agotada:"N"`
- Texto: `(titulo:(inteligencia artificial) or texto:(inteligencia artificial)) and vigencia_agotada:"N"`

## Score Detallado

| Dimensión | Peso | Puntuación | Comentario |
|-----------|------|------------|------------|
| Funcionalidad | 40% | 5/5 | Funciona perfectamente |
| Rendimiento | 20% | 5/5 | Rápido (~2.2s) |
| Usabilidad | 20% | 5/5 | Parámetro intuitivo |
| Completitud | 20% | 5/5 | Ambos modos disponibles |

**Score Final: 5.0/5**
