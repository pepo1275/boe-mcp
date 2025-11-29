# Evaluación Test 2.4: Filtrar Solo Consolidadas

## Criterios de Éxito

| Criterio | Esperado | Resultado | Estado |
|----------|----------|-----------|--------|
| Parámetro aceptado | solo_consolidada | ✅ Sí | ✅ |
| Filtro aplicado | estado_consolidacion@codigo:3 | ✅ Correcto | ✅ |
| Resultados válidos | Solo estado=Finalizado | ✅ Todos Finalizado | ✅ |
| Sin errores | Sin excepciones | ✅ Sin errores | ✅ |

## Estados de Consolidación Disponibles

| Código | Descripción |
|--------|-------------|
| 3 | Finalizado |
| 4 | Desactualizado |

## Observación Importante

En la práctica, la mayoría de normas en la base de datos ya tienen `estado_consolidacion: Finalizado`, por lo que el filtro `solo_consolidada=true` no suele cambiar significativamente los resultados.

Esto se debe a que:
1. Las normas entran al sistema consolidado una vez finalizadas
2. El estado "Desactualizado" es poco común
3. La API de legislación consolidada solo incluye normas procesadas

## Query Construido

- `solo_consolidada=true`: Añade `estado_consolidacion@codigo:3` al query
- `solo_consolidada=false`: No añade filtro de estado

## Utilidad

El filtro es útil principalmente para:
- Excluir normas que podrían estar desactualizadas
- Garantizar que se trabaja con versiones consolidadas completas
- Casos específicos donde el estado es relevante

## Score Detallado

| Dimensión | Peso | Puntuación | Comentario |
|-----------|------|------------|------------|
| Funcionalidad | 40% | 5/5 | Funciona correctamente |
| Rendimiento | 20% | 5/5 | Rápido (~2s) |
| Usabilidad | 20% | 4/5 | Efecto práctico limitado |
| Completitud | 20% | 4/5 | Pocos estados disponibles |

**Score Final: 4.5/5**
