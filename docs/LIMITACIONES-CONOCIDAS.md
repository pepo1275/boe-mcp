# Limitaciones Conocidas - BOE-MCP

## LIM-001: Estructura jerárquica incompleta en la API del BOE

**Fecha identificación:** 2025-12-03
**Versión afectada:** v1.4.0-beta.1
**Severidad:** Media
**Herramientas afectadas:** `get_article_info`, `get_law_structure_summary`

### Descripción del problema

La API de datos abiertos del BOE devuelve la estructura jerárquica de las leyes (libros, títulos, capítulos, secciones) de forma **incompleta y con inconsistencias**:

1. **Títulos sin nombres descriptivos**: La API devuelve solo "TÍTULO IV" en lugar de "TÍTULO VII - Del convenio"
2. **IDs secuenciales no correspondientes**: Los IDs internos (`ti-4`, `ti-5`) son secuenciales pero no coinciden con la numeración real de los títulos
3. **Saltos en la numeración**: La secuencia salta de "TÍTULO IV" directamente a "TÍTULO IX", omitiendo V, VI, VII, VIII

### Ejemplo del bug

**Caso real - Artículo 382 de la Ley Concursal (BOE-A-2020-4859):**

| Campo | Respuesta API | PDF Real |
|-------|---------------|----------|
| Libro | LIBRO PRIMERO | LIBRO PRIMERO ✓ |
| Título | TÍTULO IV | **TÍTULO VII - Del convenio** ❌ |
| Capítulo | CAPÍTULO V | CAPÍTULO V ✓ |
| Sección | Sección 2 | Sección 2.ª ✓ |

### Evidencia técnica

Respuesta de `get_law_index` (tipo_bloque="estructura"):

```json
[
  {"id": "ti", "titulo": "TÍTULO I"},
  {"id": "ti-2", "titulo": "TÍTULO II"},
  {"id": "ti-3", "titulo": "TÍTULO III"},
  {"id": "ti-4", "titulo": "TÍTULO IV"},
  // SALTO: Faltan TÍTULO V, VI, VII, VIII
  {"id": "ti-5", "titulo": "TÍTULO IX"}
]
```

### Causa raíz

El problema está en la **API del BOE**, no en el parsing de boe-mcp. La API:
- No incluye los nombres descriptivos de los títulos
- Usa IDs secuenciales internos que no corresponden a la numeración legal real
- No expone la jerarquía completa de forma consistente

### Impacto

- La ubicación jerárquica devuelta por `get_article_info` puede ser **incorrecta**
- `get_law_structure_summary` puede mostrar títulos con numeración errónea
- Los usuarios no pueden confiar 100% en la ubicación para navegación precisa

---

## Soluciones propuestas

### SOL-001: Documentación y advertencia (Implementación inmediata)

**Complejidad:** Baja
**Tiempo estimado:** 1 hora

Añadir advertencia en la respuesta de las herramientas afectadas:

```python
{
    "ubicacion": {
        "libro": "LIBRO PRIMERO",
        "titulo": "TÍTULO IV",  # ⚠️ Puede no coincidir con numeración real
        "capitulo": "CAPÍTULO V",
        "seccion": "Sección 2",
        "_advertencia": "La numeración de títulos puede no coincidir con el documento oficial debido a limitaciones de la API del BOE"
    }
}
```

**Pros:**
- Implementación rápida
- Informa al usuario de la limitación

**Contras:**
- No resuelve el problema, solo lo documenta

---

### SOL-002: Extracción de nombres desde bloques de título

**Complejidad:** Media
**Tiempo estimado:** 4-6 horas

Hacer una llamada adicional al bloque del título para extraer el nombre completo:

```python
# Ejemplo: obtener texto del bloque ti-4
bloque_titulo = await get_law_section(identifier, "bloque", block_id="ti-4")
# Extraer nombre completo del XML: "TÍTULO VII\nDel convenio"
```

**Implementación:**
1. Cuando se detecta un título, hacer GET al bloque específico
2. Parsear el contenido para extraer nombre descriptivo
3. Cachear resultados para evitar llamadas repetidas

**Pros:**
- Obtiene nombres descriptivos reales
- Mejora significativa en precisión

**Contras:**
- Más llamadas a la API (latencia)
- Requiere parsing adicional del contenido XML
- La numeración romana seguiría siendo la de la API

---

### SOL-003: Tabla de mapeo manual para leyes frecuentes

**Complejidad:** Media-Alta
**Tiempo estimado:** 8-12 horas (inicial) + mantenimiento

Crear un archivo de mapeo para leyes de uso frecuente:

```python
# mappings/BOE-A-2020-4859.json
{
    "titulo_mappings": {
        "ti-4": {"numero_api": "IV", "numero_real": "VII", "nombre": "Del convenio"},
        "ti-5": {"numero_api": "IX", "numero_real": "IX", "nombre": "De la conclusión..."}
    }
}
```

**Pros:**
- Precisión total para leyes mapeadas
- Sin llamadas adicionales a la API

**Contras:**
- Requiere mantenimiento manual
- Solo funciona para leyes previamente mapeadas
- No escala bien

---

### SOL-004: Inferencia por análisis de artículos

**Complejidad:** Alta
**Tiempo estimado:** 12-20 horas

Analizar el texto de los artículos para inferir la estructura real:

1. Buscar patrones como "conforme al Título VII" en el texto
2. Usar el rango de artículos para deducir límites de títulos
3. Comparar con el índice oficial del PDF (si está disponible)

**Pros:**
- Solución más robusta a largo plazo
- Podría funcionar para cualquier ley

**Contras:**
- Implementación compleja
- Alto riesgo de errores en casos edge
- Requiere mucho testing

---

### SOL-005: Reportar bug a datos abiertos del BOE

**Complejidad:** Baja (acción)
**Tiempo estimado:** 1 hora

Contactar con el equipo de datos abiertos del BOE para reportar la inconsistencia:
- Email: datosabiertos@boe.es
- Incluir ejemplos concretos y evidencia técnica

**Pros:**
- Podría resolverse en origen
- Beneficia a toda la comunidad

**Contras:**
- Sin garantía de respuesta o solución
- Tiempo de resolución desconocido

---

## Recomendación

**Corto plazo (v1.4.0):**
1. Implementar **SOL-001** (advertencia en respuestas)
2. Ejecutar **SOL-005** (reportar al BOE)

**Medio plazo (v1.5.0):**
1. Implementar **SOL-002** (extracción de nombres desde bloques)
2. Evaluar resultados y decidir si SOL-003 es necesaria

---

## Referencias

- API BOE: https://www.boe.es/datosabiertos/api/
- Ley Concursal PDF: https://www.boe.es/buscar/pdf/2020/BOE-A-2020-4859-consolidado.pdf
- Issue interno: Bug detectado durante testing de Smart Navigation v2.0
