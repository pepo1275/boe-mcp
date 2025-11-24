# Evaluación Test 2.1: Filtros Temporales

## Criterios de Éxito

| Criterio | Esperado | Resultado | Estado |
|----------|----------|-----------|--------|
| Parámetros aceptados | from_date/to_date | ✅ Sí | ✅ |
| Formato fecha | AAAAMMDD | ✅ Correcto | ✅ |
| Resultados filtrados | Dentro del rango | ⚠️ Parcial | ⚠️ |
| Sin errores | Sin excepciones | ✅ Sin errores | ✅ |

## Hallazgo Importante

**Los filtros from_date y to_date aplican sobre `fecha_actualizacion`**, no sobre `fecha_publicacion` ni `fecha_disposicion`.

Esto significa:
- Una norma de 1991 puede aparecer en búsqueda de enero 2024 si fue actualizada en esa fecha
- Para buscar normas por fecha de publicación original, hay que usar otros mecanismos

## Pruebas Realizadas

### Prueba 1: Enero 2024 + "ley"
- **Parámetros:** from=20240101, to=20240131, query="ley"
- **Resultado:** 1 norma - BOA-d-1991-90001 (Decreto de 1991, actualizado 2024-01-18)

### Prueba 2: Diciembre 2023 + "orgánica"
- **Parámetros:** from=20231201, to=20231231, query="orgánica"
- **Resultado:** 0 normas (ninguna actualización en ese período)

### Prueba 3: Q1 2024 sin query
- **Parámetros:** from=20240101, to=20240331, limit=15
- **Resultado:** 5 normas con actualizaciones en ese período
- Fechas de publicación originales: 1990, 1991, 2012, 2015, 2017

## Score Detallado

| Dimensión | Peso | Puntuación | Comentario |
|-----------|------|------------|------------|
| Funcionalidad | 40% | 4/5 | Funciona, pero semántica no intuitiva |
| Rendimiento | 20% | 5/5 | Rápido (~2s) |
| Usabilidad | 20% | 3/5 | Confuso que filtre por actualización |
| Completitud | 20% | 4/5 | Falta filtro por fecha publicación |

**Score Final: 4.0/5**

## Recomendación

Documentar claramente que from_date/to_date filtran por fecha de actualización de la consolidación, no por fecha de publicación original de la norma.
