# Test Comparativo de Versiones BOE-MCP

## Configuración

Para comparar versiones, configura ambos MCPs en `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "boe-mcp-v1.0.0": {
      "command": "/ruta/a/v1.0.0/.venv/bin/python",
      "args": ["-m", "boe_mcp.server"],
      "env": {"PYTHONPATH": "/ruta/a/v1.0.0/src"}
    },
    "boe-mcp-v1.1.0": {
      "command": "/ruta/a/v1.1.0/.venv/bin/python",
      "args": ["-m", "boe_mcp.server"],
      "env": {"PYTHONPATH": "/ruta/a/v1.1.0/src"}
    }
  }
}
```

---

## Pruebas v1.1.0 - Nuevos Parámetros

### TC01: rango_codigo (Filtro por tipo de norma)

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con rango_codigo="1300" y limit=3
```

**Esperado v1.1.0:** 3 resultados, todos con `rango.codigo = "1300"` (Ley)
**Esperado v1.0.0:** Error o parámetro ignorado

**Códigos de rango útiles:**
- 1290 = Ley Orgánica
- 1300 = Ley
- 1320 = Real Decreto-ley
- 1340 = Real Decreto
- 1350 = Orden

---

### TC02: numero_oficial (Búsqueda exacta)

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con numero_oficial="39/2015"
```

**Esperado v1.1.0:** Ley 39/2015 (BOE-A-2015-10565) - Procedimiento Administrativo
**Esperado v1.0.0:** Error o parámetro ignorado

**Otros números útiles:**
- "40/2015" = Ley Régimen Jurídico Sector Público
- "3/2018" = LO Protección de Datos (LOPDGDD)

---

### TC03: materia_codigo (Filtro por temática)

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con materia_codigo="2557" y limit=3
```

**Esperado v1.1.0:** Normas relacionadas con la materia 2557
**Esperado v1.0.0:** Error o parámetro ignorado

---

### TC04: Combinación de filtros

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con rango_codigo="1290", ambito="Estatal" y limit=3
```

**Esperado v1.1.0:** Solo Leyes Orgánicas estatales
**Esperado v1.0.0:** Solo filtra por ambito (si lo soporta)

---

## Pruebas de Limitaciones Conocidas

### TC05: sort_by (NO FUNCIONA)

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con rango_codigo="1300", limit=3 y sort_by ordenando por fecha_disposicion descendente
```

**Esperado:** Error "mal." - La API del BOE no soporta ordenamiento en queries

---

### TC06: from_date con query (COMPORTAMIENTO INESPERADO)

**Prompt:**
```
usa boe-mcp-v1.1.0: search_laws_list con rango_codigo="1300", from_date="20240101" y limit=3
```

**Esperado:** Leyes desde 2024
**Comportamiento actual:** Puede devolver leyes de cualquier fecha (bug pendiente)

---

## Pruebas Funcionales Básicas (ambas versiones)

### TC07: Búsqueda por texto

**Prompt:**
```
usa boe-mcp: search_laws_list con query_value="protección datos" y limit=5
```

**Esperado:** Normas que contengan "protección datos" en título

---

### TC08: Filtro por ámbito

**Prompt:**
```
usa boe-mcp: search_laws_list con ambito="Autonómico" y limit=5
```

**Esperado:** Solo normas autonómicas

---

### TC09: Combinación texto + ámbito

**Prompt:**
```
usa boe-mcp: search_laws_list con query_value="medio ambiente", ambito="Estatal" y limit=3
```

**Esperado:** Normas estatales sobre medio ambiente

---

## Gaps Identificados para v1.2.0

| Gap | Descripción | Prioridad |
|-----|-------------|-----------|
| sort_by | No funciona - API devuelve error | Alta |
| from_date/to_date | No filtra correctamente con query | Alta |
| departamento_codigo | No implementado | Media |
| fecha_disposicion range | Filtrar por rango de fechas en query | Media |

---

## Cómo Reportar Resultados

Al ejecutar cada test, anota:

1. **Versión MCP:** v1.0.0 / v1.1.0
2. **Query generada:** (ver en params de respuesta)
3. **Resultado:** OK / ERROR / INESPERADO
4. **Observaciones:** Cualquier comportamiento extraño
