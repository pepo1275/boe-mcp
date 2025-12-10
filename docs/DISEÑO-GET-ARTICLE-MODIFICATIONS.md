# Diseño: get_article_modifications

**Versión:** 1.0
**Fecha:** 2025-12-10
**Estado:** Propuesta aprobada

---

## 1. Problema a Resolver

### 1.1 Caso de Uso Principal

> "Necesito saber si el artículo 28 de la Ley 39/2015 ha sido modificado, porque afecta a un procedimiento que gestiono y necesito saber si sigue vigente o debo actualizar el procedimiento."

### 1.2 Caso de Uso Secundario: Monitorización

> "Quiero un cron diario que me avise si alguna de las leyes/artículos que me afectan ha sido modificada."

**Enfoque inverso (recomendado):**
En lugar de revisar cada publicación del BOE diario buscando modificaciones, consultamos directamente el estado actual del artículo vigilado y comparamos con la última fecha conocida.

---

## 2. Diseño de la Herramienta

### 2.1 Signatura

```python
def get_article_modifications(
    identifier: str,
    articulo: str
) -> dict
```

### 2.2 Parámetros

| Parámetro | Tipo | Requerido | Descripción | Ejemplo |
|-----------|------|-----------|-------------|---------|
| `identifier` | str | Sí | Identificador BOE de la ley | `"BOE-A-2015-10565"` |
| `articulo` | str | Sí | Número del artículo (sin prefijo) | `"28"` |

### 2.3 Respuesta: Artículo Modificado

```json
{
  "modificado": true,
  "articulo": "28",
  "ley_id": "BOE-A-2015-10565",
  "titulo_articulo": "Documentos aportados por los interesados",
  "fecha_version_original": "20151002",
  "fecha_version_actual": "20181206",
  "total_versiones": 2,
  "modificaciones": [
    {
      "version": 2,
      "norma_modificadora": "BOE-A-2018-16673",
      "fecha_publicacion": "20181206",
      "fecha_vigencia": "20181207",
      "descripcion": "Se modifica el apartado 2 y 3 por la disposición final 12"
    }
  ]
}
```

**Tamaño estimado:** ~400-600 bytes

### 2.4 Respuesta: Artículo NO Modificado

```json
{
  "modificado": false,
  "articulo": "21",
  "ley_id": "BOE-A-2015-10565",
  "titulo_articulo": "Obligación de resolver",
  "fecha_version_original": "20151002",
  "fecha_version_actual": "20151002",
  "total_versiones": 1,
  "modificaciones": []
}
```

**Tamaño estimado:** ~250 bytes

### 2.5 Respuesta: Error

```json
{
  "error": true,
  "codigo": "ARTICULO_NO_ENCONTRADO",
  "mensaje": "El artículo 383 no existe en la ley BOE-A-2015-10565"
}
```

---

## 3. Implementación Técnica

### 3.1 Flujo Interno

```
1. Construir block_id: "a" + articulo → "a28"

2. Llamar API BOE:
   GET /legislacion-consolidada/id/{identifier}/texto/bloque/{block_id}

3. Parsear XML:
   - Extraer todos los elementos <version>
   - Para cada versión: id_norma, fecha_publicacion, fecha_vigencia
   - Extraer <blockquote class="nota_pie"> para descripción

4. Construir respuesta JSON compacta
```

### 3.2 Parsing del XML

Estructura XML de entrada (ejemplo artículo 77):

```xml
<bloque id="a77" tipo="precepto" titulo="Artículo 77">
  <version id_norma="BOE-A-2015-10565" fecha_publicacion="20151002" fecha_vigencia="20161002">
    <!-- texto original -->
  </version>
  <version id_norma="BOE-A-2022-11589" fecha_publicacion="20220713" fecha_vigencia="20220714">
    <!-- texto modificado -->
    <blockquote>
      <p class="nota_pie">Se añade el apartado 3 bis por la disposición final 4 de la Ley 15/2022</p>
    </blockquote>
  </version>
</bloque>
```

### 3.3 Lógica de Extracción

```python
# Pseudocódigo
versiones = xml.findall(".//version")
modificado = len(versiones) > 1

version_original = versiones[0]
version_actual = versiones[-1]  # Última versión = vigente

modificaciones = []
for i, version in enumerate(versiones[1:], start=2):
    nota = version.find(".//p[@class='nota_pie']")
    modificaciones.append({
        "version": i,
        "norma_modificadora": version.get("id_norma"),
        "fecha_publicacion": version.get("fecha_publicacion"),
        "fecha_vigencia": version.get("fecha_vigencia"),
        "descripcion": nota.text if nota else None
    })
```

---

## 4. Optimización de Contexto

### 4.1 Principios de Diseño

| Principio | Implementación |
|-----------|----------------|
| **Respuesta mínima** | Solo metadatos, NO texto del artículo |
| **Sin redundancia** | No repetir información deducible |
| **Estructura plana** | Evitar anidación profunda |
| **Campos opcionales** | Solo incluir si tienen valor |

### 4.2 Comparativa de Tamaños

| Herramienta | Tamaño típico | Tamaño máximo |
|-------------|---------------|---------------|
| `get_law_section(bloque)` | ~3-5 KB | ~20 KB |
| `get_article_info` | ~400 bytes | ~2 KB |
| **`get_article_modifications`** | **~300 bytes** | **~800 bytes** |

### 4.3 Lo que NO incluye la respuesta

- ❌ Texto completo del artículo (usar `get_article_info` si se necesita)
- ❌ Texto de versiones anteriores
- ❌ Metadatos de la ley completa
- ❌ Análisis de relaciones

---

## 5. Casos de Uso Detallados

### 5.1 Verificación Puntual

```
Usuario: "¿Ha cambiado el artículo 28 de la Ley 39/2015?"

→ get_article_modifications("BOE-A-2015-10565", "28")

Respuesta al usuario:
"Sí, el artículo 28 fue modificado por la LO 3/2018 de Protección de Datos
el 6 de diciembre de 2018. Se modificaron los apartados 2 y 3."
```

### 5.2 Monitorización con Cron (Enfoque Inverso)

```python
# cron_monitor.py - Ejecutar diariamente

ARTICULOS_VIGILADOS = [
    ("BOE-A-2015-10565", "28"),  # Art. 28 Ley 39/2015
    ("BOE-A-2015-10566", "47"),  # Art. 47 Ley 40/2015
]

# Almacenamiento persistente de últimas fechas conocidas
ultimas_fechas = cargar_estado()

for ley_id, articulo in ARTICULOS_VIGILADOS:
    resultado = get_article_modifications(ley_id, articulo)

    clave = f"{ley_id}:{articulo}"
    fecha_conocida = ultimas_fechas.get(clave, "00000000")

    if resultado["fecha_version_actual"] > fecha_conocida:
        enviar_alerta(f"¡CAMBIO DETECTADO en {clave}!")
        ultimas_fechas[clave] = resultado["fecha_version_actual"]

guardar_estado(ultimas_fechas)
```

### 5.3 Auditoría de Procedimiento

```
Usuario: "Voy a revisar un procedimiento que usa los artículos 21, 28 y 53
de la Ley 39/2015. ¿Alguno ha cambiado desde 2020?"

→ get_article_modifications("BOE-A-2015-10565", "21")
→ get_article_modifications("BOE-A-2015-10565", "28")
→ get_article_modifications("BOE-A-2015-10565", "53")

Respuesta:
- Art. 21: Sin cambios (versión original 2015)
- Art. 28: Modificado en 2018 (LO 3/2018) ⚠️
- Art. 53: Sin cambios (versión original 2015)
```

---

## 6. Manejo de Errores

### 6.1 Códigos de Error

| Código | Causa | Mensaje ejemplo |
|--------|-------|-----------------|
| `ARTICULO_NO_ENCONTRADO` | Número de artículo no existe | "El artículo 383 no existe en BOE-A-2015-10565" |
| `LEY_NO_ENCONTRADA` | Identificador inválido | "No se encontró la ley BOE-A-2099-99999" |
| `FORMATO_ARTICULO_INVALIDO` | Artículo no es número | "El artículo debe ser un número: '28', no 'veintiocho'" |
| `API_ERROR` | Error del BOE | "Error al consultar la API del BOE" |

### 6.2 Validaciones

```python
# Validar formato de artículo
if not articulo.isdigit():
    return error("FORMATO_ARTICULO_INVALIDO", ...)

# Validar formato de identificador
if not re.match(r"BOE-[A-Z]-\d{4}-\d+", identifier):
    return error("IDENTIFICADOR_INVALIDO", ...)
```

---

## 7. Integración con Herramientas Existentes

### 7.1 Flujo Completo de Investigación

```
1. Buscar ley:
   search_laws_list(query="39/2015", rango_codigo="1300")
   → BOE-A-2015-10565

2. Ver estructura:
   get_law_structure_summary("BOE-A-2015-10565")
   → 133 artículos, 6 títulos

3. Verificar modificaciones de artículo específico:
   get_article_modifications("BOE-A-2015-10565", "28")
   → Modificado por LO 3/2018

4. Si necesita el texto actual:
   get_article_info("BOE-A-2015-10565", "28")
   → Texto completo vigente
```

### 7.2 Matriz de Herramientas

| Necesito... | Herramienta |
|-------------|-------------|
| ¿Ha sido modificado el artículo X? | `get_article_modifications` |
| ¿Qué dice el artículo X actualmente? | `get_article_info` |
| ¿Qué artículos tiene la ley? | `get_law_structure_summary` |
| ¿Qué leyes han modificado esta ley? | `get_law_section(analisis)` |

---

## 8. Futuras Extensiones

### 8.1 check_law_modifications (v2)

Resumen de todos los artículos modificados de una ley:

```python
check_law_modifications(identifier: str) -> dict
```

### 8.2 monitor_articles (v3)

Verificar múltiples artículos en una sola llamada:

```python
monitor_articles(
    articulos: list[tuple[str, str]],  # [(ley, art), ...]
    desde_fecha: str
) -> dict
```

---

## 9. Checklist de Implementación

- [ ] Crear función en `server.py`
- [ ] Parsear XML de respuesta del bloque
- [ ] Extraer versiones y notas
- [ ] Construir respuesta JSON compacta
- [ ] Manejar errores (artículo no existe, etc.)
- [ ] Añadir tests
- [ ] Actualizar documentación de herramientas

---

## 10. Referencias

- [GUIA-USO-HERRAMIENTAS.md](./GUIA-USO-HERRAMIENTAS.md) - Guía general
- [CATALOGO-HERRAMIENTAS-BOE-MCP.md](./CATALOGO-HERRAMIENTAS-BOE-MCP.md) - Catálogo completo
- [API BOE - Legislación Consolidada](https://www.boe.es/datosabiertos/api/)
