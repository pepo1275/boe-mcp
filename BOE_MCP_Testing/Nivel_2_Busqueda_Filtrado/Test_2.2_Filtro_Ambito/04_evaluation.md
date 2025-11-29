# Evaluación Test 2.2: Filtro por Ámbito

## Criterios de Éxito

| Criterio | Esperado | Resultado | Estado |
|----------|----------|-----------|--------|
| Filtro Estatal | Normas estatales | ✅ 5 normas BOE | ✅ |
| Filtro Autonómico | Normas CCAA | ✅ 2 normas | ✅ |
| Sin solapamiento | Resultados distintos | ✅ Distintos | ✅ |
| Sin errores | Sin excepciones | ✅ Sin errores | ✅ |

## Resultados

### Ámbito Estatal (query: "protección datos")
| Identificador | Rango | Departamento |
|---------------|-------|--------------|
| BOE-A-2021-18486 | Orden | Min. Universidades |
| BOE-A-2021-18134 | Instrucción | AEPD |
| BOE-A-2021-9175 | Real Decreto | Presidencia |
| BOE-A-2021-8806 | Ley Orgánica | Jefatura Estado |
| BOE-A-2019-3423 | Circular | AEPD |

### Ámbito Autonómico (query: "protección datos")
| Identificador | Rango | CCAA |
|---------------|-------|------|
| BOE-A-2024-900 | Ley | País Vasco |
| BOE-A-2010-16136 | Ley | Cataluña |

## Observaciones

- El filtro funciona correctamente usando códigos internos (1=Estatal, 2=Autonómico)
- Los valores se traducen al parámetro de la API (`ambito@codigo:"1"`)
- Diferencia clara y consistente entre ámbitos

## Score Detallado

| Dimensión | Peso | Puntuación | Comentario |
|-----------|------|------------|------------|
| Funcionalidad | 40% | 5/5 | Funciona perfectamente |
| Rendimiento | 20% | 5/5 | Rápido (~1.8s) |
| Usabilidad | 20% | 5/5 | Valores claros (Estatal/Autonómico) |
| Completitud | 20% | 5/5 | Cubre los ámbitos principales |

**Score Final: 5.0/5**
