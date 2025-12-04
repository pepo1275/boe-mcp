import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Literal, Union, Annotated
import httpx
import logging
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# v1.3.0: Input validators for security
from boe_mcp.validators import (
    ValidationError,
    validate_boe_identifier,
    validate_block_id,
    validate_fecha,
    validate_date_range,
    validate_query_value,
    validate_codigo,
    validate_articulo,
    validate_seccion_boe,  # v1.5.0: Smart Summary
    SECCIONES_BOE_VALIDAS,  # v1.5.0: Smart Summary
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BOE-MCPServer")

mcp = FastMCP(
    "boe-mcp",
    instructions="MCP server for querying the Spanish Official State Gazette (BOE) API"
)

BOE_API_BASE = "https://www.boe.es"
USER_AGENT = "boe-mcp-client/1.0"

# v1.2.0: Constantes para autocompletado de rangos de fecha
# La API BOE requiere AMBOS límites (gte Y lte) para que el filtro range funcione
FECHA_MINIMA_DEFAULT = "19780101"  # Constitución Española - fecha mínima razonable

async def make_boe_request(
    endpoint: str,
    params: dict[str, Any] | None = None,
    accept: str = "application/json"
) -> dict[str, Any] | None:
    
    """
    Realiza una solicitud HTTP GET a la API del BOE.

    Args:
        endpoint: Ruta relativa del endpoint (ej. '/datosabiertos/api/...').
        params: Parámetros de consulta (query string).
        accept: Tipo de contenido esperado ('application/json' por defecto).

    Returns:
        Diccionario con los datos JSON de respuesta o None si ocurre un error.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": accept,
    }
    url = f"{BOE_API_BASE}{endpoint}"

    logger.info(f"Making request to BOE API: {url} with params: {params}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as http_err:
            print(f"[BOE] HTTP error: {http_err.response.status_code} - {http_err.response.text}")
        except Exception as e:
            print(f"[BOE] Error: {e}")

        return None

async def make_boe_raw_request(endpoint: str, accept: str = "application/xml") -> str | None:

    headers = {
        "User-Agent": "boe-mcp-client/1.0",
        "Accept": accept,
    }
    url = f"{BOE_API_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as http_err:
            print(f"[BOE] HTTP error {http_err.response.status_code}")
        except Exception as e:
            print(f"[BOE] Error: {e}")

        return None

# ----------- 1. LEGISLACIÓN CONSOLIDADA -------------------

@mcp.tool()
async def search_laws_list(

    from_date: str | None = None,
    to_date: str | None = None,
    offset: int | None = 0,
    limit: int | None = 50,

    query_value: str | None = None,

    search_in_title_only: bool = True,
    solo_vigente: bool = True,
    solo_consolidada: bool = False,

    ambito: Literal["Estatal", "Autonómico", "Europeo"] | None = None,

    # v1.1.0 - Nuevos parámetros de filtro directo
    rango_codigo: str | None = None,
    materia_codigo: str | None = None,
    numero_oficial: str | None = None,

    # v1.3.0 - Nuevos parámetros de filtro
    departamento_codigo: str | None = None,
    diario_numero: int | None = None,

    # v1.2.0 - Filtros de rango por fecha (requieren ambos límites, se autocompletan)
    fecha_publicacion_desde: str | None = None,
    fecha_publicacion_hasta: str | None = None,
    fecha_disposicion_desde: str | None = None,
    fecha_disposicion_hasta: str | None = None,

    # v1.2.0 - Ordenamiento simplificado
    ordenar_por: Literal["fecha_disposicion", "fecha_publicacion", "titulo"] | None = None,
    ordenar_direccion: Literal["asc", "desc"] = "desc",

    # Parámetros avanzados (mantener compatibilidad)
    must: dict[str, str] | None = None,
    should: dict[str, str] | None = None,
    must_not: dict[str, str] | None = None,
    range_filters: dict | None = None,
    sort_by: list[dict] | None = None,

) -> Union[dict, str]:

    """
    Búsqueda avanzada de normas del BOE.

    Args:
        -from_date: Filtra por fecha de ACTUALIZACIÓN en el sistema (AAAAMMDD).
            NOTA: Este parámetro NO filtra por fecha de publicación ni disposición.
            Es útil para encontrar normas recientemente actualizadas en la base de datos.
        -to_date: Fecha máxima de actualización (AAAAMMDD). Ver nota de from_date.
        -offset: Índice inicial. Es obligatorio incluírlo en la llamada a la función.
        -limit: Máximo de resultados (-1 para todos).

        -query_value: Texto libre. Usar preferentemente palabras, no frases.

        -search_in_title_only: True para buscar solo en el título (True por defecto).
        -solo_vigente: True para buscar solamente normas vigentes (True por defecto).
        -solo_consolidada: true para buscar solamente normas consolidadas (False por defecto).

        -ambito: Filtra por ámbito ('Estatal', 'Autonómico', 'Europeo').

        -rango_codigo: Código del rango normativo. Ejemplos: 1300=Ley, 1290=Ley Orgánica,
            1340=Real Decreto, 1320=Real Decreto-ley, 1350=Orden.
            Ver get_auxiliary_table("rangos") para lista completa.
        -materia_codigo: Código de materia temática para filtrar por tema.
            Ver get_auxiliary_table("materias") para lista completa (~3000 códigos).
        -numero_oficial: Número oficial de la norma (ej: "39/2015", "1/2023").
            Permite búsqueda exacta por número de ley/decreto.

        -departamento_codigo: Código del departamento emisor (ej: "5140" para Ministerio de Hacienda).
            Ver get_auxiliary_table("departamentos") para lista completa.
        -diario_numero: Número del BOE donde se publicó la norma.

        -fecha_publicacion_desde: Fecha mínima de publicación en BOE (AAAAMMDD).
            Si se especifica sin fecha_publicacion_hasta, se autocompleta hasta hoy.
        -fecha_publicacion_hasta: Fecha máxima de publicación en BOE (AAAAMMDD).
            Si se especifica sin fecha_publicacion_desde, se autocompleta desde 19780101.
        -fecha_disposicion_desde: Fecha mínima de la disposición/norma (AAAAMMDD).
            Si se especifica sin fecha_disposicion_hasta, se autocompleta hasta hoy.
        -fecha_disposicion_hasta: Fecha máxima de la disposición/norma (AAAAMMDD).
            Si se especifica sin fecha_disposicion_desde, se autocompleta desde 19780101.

        -ordenar_por: Campo por el que ordenar ('fecha_disposicion', 'fecha_publicacion', 'titulo').
        -ordenar_direccion: Dirección del ordenamiento ('asc' o 'desc', por defecto 'desc').

        -must: Condiciones adicionales que deben cumplirse (and). Parámetro avanzado.
        -should: Condiciones opcionales (or). Parámetro avanzado.
        -must_not: Condiciones excluidas (not). Parámetro avanzado.
        -range_filters: Filtros por fechas en formato raw. Parámetro avanzado.
            Prefiera usar fecha_publicacion_* y fecha_disposicion_* en su lugar.
        -sort_by: Ordenamiento personalizado en formato raw. Parámetro avanzado.
            Prefiera usar ordenar_por y ordenar_direccion en su lugar.
    """

    # v1.3.0: Input validation
    try:
        # Validate dates
        if from_date:
            from_date = validate_fecha(from_date)
        if to_date:
            to_date = validate_fecha(to_date)
        from_date, to_date = validate_date_range(from_date, to_date)

        if fecha_publicacion_desde:
            fecha_publicacion_desde = validate_fecha(fecha_publicacion_desde)
        if fecha_publicacion_hasta:
            fecha_publicacion_hasta = validate_fecha(fecha_publicacion_hasta)
        fecha_publicacion_desde, fecha_publicacion_hasta = validate_date_range(
            fecha_publicacion_desde, fecha_publicacion_hasta
        )

        if fecha_disposicion_desde:
            fecha_disposicion_desde = validate_fecha(fecha_disposicion_desde)
        if fecha_disposicion_hasta:
            fecha_disposicion_hasta = validate_fecha(fecha_disposicion_hasta)
        fecha_disposicion_desde, fecha_disposicion_hasta = validate_date_range(
            fecha_disposicion_desde, fecha_disposicion_hasta
        )

        # Validate query
        if query_value:
            query_value = validate_query_value(query_value)

        # Validate codes
        if rango_codigo:
            rango_codigo = validate_codigo(rango_codigo)
        if materia_codigo:
            materia_codigo = validate_codigo(materia_codigo)
        if departamento_codigo:
            departamento_codigo = validate_codigo(departamento_codigo)

    except ValidationError as e:
        return f"Error de validación: {e}"

    endpoint = "/datosabiertos/api/legislacion-consolidada"
    
    params: dict[str, Union[str, int, None]] = {}

    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if offset:
        params["offset"] = offset
    if limit:
        params["limit"] = limit

    # v1.3.0: Incluir todos los parámetros que requieren objeto query
    has_query_params = (
        query_value or ambito or must or should or must_not or range_filters or sort_by
        or rango_codigo or materia_codigo or numero_oficial
        or departamento_codigo or diario_numero  # v1.3.0
        or fecha_publicacion_desde or fecha_publicacion_hasta
        or fecha_disposicion_desde or fecha_disposicion_hasta
        or ordenar_por
    )

    if has_query_params:

        # Construcción del objeto query según especificación BOE con tipos explícitos
        query_obj_def: dict[str, Any] = {"query": {}}

        # v1.2.0: Fecha actual dinámica para autocompletado
        fecha_hoy = datetime.now().strftime("%Y%m%d")

        # ⏳ v1.2.0: Filtros de rango por fecha con autocompletado
        # IMPORTANTE: La API BOE requiere AMBOS límites (gte Y lte) para que funcione
        if fecha_publicacion_desde or fecha_publicacion_hasta:
            if "range" not in query_obj_def["query"]:
                query_obj_def["query"]["range"] = {}
            query_obj_def["query"]["range"]["fecha_publicacion"] = {
                "gte": fecha_publicacion_desde or FECHA_MINIMA_DEFAULT,
                "lte": fecha_publicacion_hasta or fecha_hoy
            }

        if fecha_disposicion_desde or fecha_disposicion_hasta:
            if "range" not in query_obj_def["query"]:
                query_obj_def["query"]["range"] = {}
            query_obj_def["query"]["range"]["fecha_disposicion"] = {
                "gte": fecha_disposicion_desde or FECHA_MINIMA_DEFAULT,
                "lte": fecha_disposicion_hasta or fecha_hoy
            }

        # ⏳ Rango por fechas (parámetro avanzado legacy)
        if range_filters:
            if "range" not in query_obj_def["query"]:
                query_obj_def["query"]["range"] = {}
            query_obj_def["query"]["range"].update(range_filters)

        # 📥 v1.2.0: Ordenamiento simplificado
        if ordenar_por:
            query_obj_def["sort"] = [{ordenar_por: ordenar_direccion}]
        elif sort_by:
            # Parámetro avanzado legacy
            query_obj_def["sort"] = sort_by

        # v1.3.0: Incluir nuevos filtros en la condición
        has_clauses = (
            query_value or ambito or must or should or must_not
            or rango_codigo or materia_codigo or numero_oficial
            or departamento_codigo or diario_numero  # v1.3.0
        )

        if has_clauses:
            # 1. Query String (condiciones principales)
            query_string = {}
            clauses = []

            # 🔍 Búsqueda textual
            if query_value:
                if search_in_title_only:
                    clauses.append(f"titulo:({query_value})")
                else:
                    clauses.append(f"(titulo:({query_value}) or texto:({query_value}))")

            # ✅ Vigencia
            if solo_vigente:
                clauses.append("vigencia_agotada:\"N\"")

            # 📄 Estado de consolidación
            estado_map = {
                "Consolidada": "3",
                "Parcial": "2",
                "No consolidada": "1"
            }
            if solo_consolidada:
                clauses.append(f"estado_consolidacion@codigo:{estado_map['Consolidada']}")

            # 🌐 Filtro de ámbito
            # Mapeo de códigos de ámbito para la API del BOE
            ambito_map = {
                "Estatal": "1",
                "Autonómico": "2",
                "Europeo": "3"
            }
            if ambito:
                clauses.append(f'ambito@codigo:"{ambito_map.get(ambito)}"')

            # 📋 v1.1.0: Filtro por rango normativo (Ley, RD, LO, etc.)
            if rango_codigo:
                clauses.append(f'rango@codigo:"{rango_codigo}"')

            # 🏷️ v1.1.0: Filtro por materia temática
            if materia_codigo:
                clauses.append(f'materia@codigo:"{materia_codigo}"')

            # 🔢 v1.1.0: Filtro por número oficial de norma
            if numero_oficial:
                clauses.append(f'numero_oficial:"{numero_oficial}"')

            # 🏛️ v1.3.0: Filtro por departamento emisor
            if departamento_codigo:
                clauses.append(f'departamento@codigo:"{departamento_codigo}"')

            # 📰 v1.3.0: Filtro por número de diario BOE
            if diario_numero:
                clauses.append(f'diario_numero:"{diario_numero}"')

            # 🧱 Condiciones adicionales
            for cond_type, operator in [("must", "and"), ("should", "or")]:
                if locals().get(cond_type):
                    cond_clause = f" {operator} ".join(
                        f"{k}:{v}" for k, v in locals()[cond_type].items()
                    )
                    clauses.append(f"({cond_clause})")

            # 🚫 Exclusiones
            if must_not:
                clauses.extend(f"not {k}:{v}" for k, v in must_not.items())

            if clauses:
                query_string["query"] = " and ".join(clauses)
                query_obj_def["query"]["query_string"] = query_string
            
        params["query"] = json.dumps(query_obj_def)

    data = await make_boe_request(endpoint, params=params)

    if not data:
        return f"mal. endpoint: {endpoint}- params: {params}."

    return {"endpoint": endpoint, "params": params, "data": data}

    '''
    resumen = data.get("titulo", "Sin título")
    estado = data.get("estado_consolidacion", "Desconocido")
    url_html = data.get("url_html", "")
    return f"📚 {resumen}\nEstado: {estado}\nURL: {url_html}"
    '''

@mcp.tool()
async def get_law_section(
    identifier: str,
    section: Literal[
        "completa", "metadatos", "analisis", "metadata-eli", "texto", "indice", "bloque"
    ],
    block_id: str | None,
    format: Literal["xml", "json"] = "xml"
) -> Union[str, bytes]:
    """
    Recupera una parte específica de una norma consolidada del BOE.

    Args:
        identifier: ID de la norma (ej. "BOE-A-2023-893").
        section: Parte de la norma a obtener:
            - "completa": Toda la norma
            - "metadatos": Solo metadatos
            - "analisis": Datos analíticos (materias, referencias)
            - "metadata-eli": Metadatos ELI
            - "texto": Texto completo consolidado
            - "indice": Índice de bloques
            - "bloque": Un bloque específico (requiere block_id)
        block_id: Solo requerido si section="bloque"
        format: Formato de respuesta (xml o json, si disponible)
    
    Returns:
        Contenido de la norma o parte solicitada (como string XML o JSON).
    """
    # v1.3.0: Input validation
    try:
        identifier = validate_boe_identifier(identifier)
        if block_id:
            block_id = validate_block_id(block_id)
    except ValidationError as e:
        return f"Error de validación: {e}"

    base = f"/datosabiertos/api/legislacion-consolidada/id/{identifier}"

    # Construir el endpoint correcto
    match section:
        case "completa":
            endpoint = base
        case "bloque":
            if not block_id:
                return "Para obtener un bloque, debes proporcionar block_id."
            endpoint = f"{base}/texto/bloque/{block_id}"
        case "indice":
            endpoint = f"{base}/texto/indice"
        case _:
            endpoint = f"{base}/{section}"

    accept = "application/xml" if format == "xml" else "application/json"

    data = await make_boe_raw_request(endpoint, accept=accept)

    if data is None:
        return f"No se pudo recuperar la sección '{section}' de la norma {identifier}."

    return data

# ----------- 1.5 NAVEGACIÓN INTELIGENTE v2.0 ---------------


def _reconstruir_ubicacion(bloques: list, indice_objetivo: int) -> dict:
    """
    Reconstruye la jerarquía de ubicación de un artículo.

    Recorre los bloques anteriores al artículo objetivo para encontrar
    la estructura jerárquica: libro → título → capítulo → sección.

    Args:
        bloques: Lista de elementos XML de bloques
        indice_objetivo: Índice del bloque objetivo en la lista

    Returns:
        Dict con keys: libro, titulo, capitulo, seccion (valores str o None)
    """
    ubicacion = {
        "libro": None,
        "titulo": None,
        "capitulo": None,
        "seccion": None
    }

    for i, bloque in enumerate(bloques):
        if i >= indice_objetivo:
            break

        id_elem = bloque.find("id")
        titulo_elem = bloque.find("titulo")

        if id_elem is None or titulo_elem is None:
            continue

        id_bloque = id_elem.text or ""
        titulo_bloque = titulo_elem.text or ""

        # Libro: lp (libro primero), ls (libro segundo)
        if id_bloque.startswith("lp") or id_bloque.startswith("ls"):
            ubicacion["libro"] = titulo_bloque
            ubicacion["titulo"] = None  # Reset niveles inferiores
            ubicacion["capitulo"] = None
            ubicacion["seccion"] = None
        # Título: ti, ti-2, ti-3
        elif id_bloque.startswith("ti"):
            ubicacion["titulo"] = titulo_bloque
            ubicacion["capitulo"] = None
            ubicacion["seccion"] = None
        # Capítulo: ci, cv (capítulo quinto), etc.
        elif id_bloque.startswith("ci") or id_bloque.startswith("cv"):
            ubicacion["capitulo"] = titulo_bloque
            ubicacion["seccion"] = None
        # Sección: s1, s2-3, s4-16 (no artículos que empiezan con 'a')
        elif id_bloque.startswith("s"):
            # Verificar que es sección (sN o sN-N) y no otra cosa
            if re.match(r'^s\d', id_bloque):
                ubicacion["seccion"] = titulo_bloque

    return ubicacion


def _extraer_texto_de_bloque_xml(bloque_xml: str) -> str:
    """
    Extrae el texto limpio de un bloque XML.

    Args:
        bloque_xml: String XML del bloque

    Returns:
        Texto del artículo sin tags XML
    """
    try:
        root = ET.fromstring(bloque_xml)
        # Buscar el elemento texto o extraer todo el texto
        texto_elem = root.find(".//texto")
        if texto_elem is not None:
            # Extraer todo el texto incluyendo hijos
            return "".join(texto_elem.itertext()).strip()
        # Fallback: extraer todo el texto del root
        return "".join(root.itertext()).strip()
    except ET.ParseError:
        return bloque_xml  # Devolver el XML original si falla


@mcp.tool()
async def get_article_info(
    identifier: str,
    articulo: str,
    incluir_texto: bool = False
) -> dict:
    """
    Obtiene información detallada de un artículo específico dentro de una ley.

    Esta herramienta permite consultar artículos individuales de leyes extensas
    sin necesidad de descargar el documento completo. Ideal para:
    - Verificar si un artículo fue modificado y cuándo
    - Obtener la ubicación jerárquica del artículo (libro, título, capítulo)
    - Acceder al texto del artículo de forma eficiente

    Args:
        identifier: ID BOE de la ley (ej. "BOE-A-2020-4859" para Ley Concursal)
        articulo: Número del artículo a consultar. Formatos válidos:
            - Número simple: "1", "386"
            - Con sufijo latino: "224 bis", "37 quater"
            - Artículo único: "único"
        incluir_texto: Si True, incluye el texto completo del artículo (default: False)

    Returns:
        Diccionario con información del artículo:
        - identifier: ID de la ley
        - articulo: Número consultado
        - block_id: ID del bloque en la API BOE
        - titulo_completo: Título del artículo (ej. "Artículo 386. Legitimación")
        - fecha_actualizacion: Fecha de última modificación (AAAAMMDD)
        - fecha_ley_original: Fecha de publicación original de la ley
        - modificado: True si el artículo fue modificado después de la publicación
        - ubicacion: Dict con libro, titulo, capitulo, seccion (o None)
        - url_bloque: URL directa al bloque en la API BOE
        - texto: Texto del artículo (solo si incluir_texto=True)

        En caso de error:
        - error: True
        - codigo: "VALIDATION_ERROR" | "LEY_NO_ENCONTRADA" | "ARTICULO_NO_ENCONTRADO" | "ERROR_PARSING"
        - mensaje: Descripción del error

    Examples:
        >>> get_article_info("BOE-A-2020-4859", "386")
        {"articulo": "386", "modificado": True, "ubicacion": {"libro": "LIBRO TERCERO", ...}}

        >>> get_article_info("BOE-A-2020-4859", "224 bis", incluir_texto=True)
        {"articulo": "224 bis", "texto": "El acreedor podrá...", ...}
    """
    # 1. VALIDACIÓN
    try:
        identifier = validate_boe_identifier(identifier)
        articulo = validate_articulo(articulo)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # 2. OBTENER ÍNDICE DE LA LEY
    base = f"/datosabiertos/api/legislacion-consolidada/id/{identifier}"
    indice_endpoint = f"{base}/texto/indice"

    indice_xml = await make_boe_raw_request(indice_endpoint, accept="application/xml")

    if indice_xml is None:
        return {
            "error": True,
            "codigo": "LEY_NO_ENCONTRADA",
            "mensaje": f"No se pudo recuperar la ley {identifier}",
            "detalles": {"identifier": identifier}
        }

    # 3. PARSEAR XML
    try:
        root = ET.fromstring(indice_xml)
        bloques = root.findall(".//bloque")
    except ET.ParseError as e:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "Error procesando respuesta de la API",
            "detalles": {"error_xml": str(e)}
        }

    if not bloques:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "La ley no contiene bloques de texto",
            "detalles": None
        }

    # 4. BUSCAR ARTÍCULO
    # Normalizar el patrón de búsqueda
    # Manejar "único" como caso especial
    if articulo.lower() == "único":
        patron_titulo = "artículo único"
    else:
        patron_titulo = f"artículo {articulo}"

    bloque_encontrado = None
    indice_encontrado = -1

    for i, bloque in enumerate(bloques):
        titulo_elem = bloque.find("titulo")
        if titulo_elem is None or titulo_elem.text is None:
            continue

        # Normalizar: convertir a minúsculas y reemplazar non-breaking space (\xa0) por espacio normal
        titulo = titulo_elem.text.lower().replace('\xa0', ' ')

        # Buscar coincidencia al inicio del título
        if titulo.startswith(patron_titulo):
            # Verificar que es el artículo exacto (no "Artículo 38" cuando buscamos "Artículo 3")
            # El título debe ser "Artículo N." o "Artículo N " o "Artículo N<fin>"
            siguiente_char_idx = len(patron_titulo)
            if siguiente_char_idx < len(titulo):
                siguiente_char = titulo[siguiente_char_idx]
                # El siguiente carácter debe ser punto, espacio o fin de línea
                if siguiente_char not in ". ":
                    continue

            bloque_encontrado = bloque
            indice_encontrado = i
            break

    if bloque_encontrado is None:
        return {
            "error": True,
            "codigo": "ARTICULO_NO_ENCONTRADO",
            "mensaje": f"No se encontró el artículo {articulo} en {identifier}",
            "detalles": {"identifier": identifier, "articulo": articulo}
        }

    # 5. EXTRAER DATOS DEL BLOQUE
    block_id_elem = bloque_encontrado.find("id")
    titulo_completo_elem = bloque_encontrado.find("titulo")
    fecha_actualizacion_elem = bloque_encontrado.find("fecha_actualizacion")
    url_elem = bloque_encontrado.find("url_bloque")

    block_id = block_id_elem.text if block_id_elem is not None else ""
    titulo_completo = titulo_completo_elem.text if titulo_completo_elem is not None else ""
    fecha_actualizacion = fecha_actualizacion_elem.text if fecha_actualizacion_elem is not None else ""
    url_bloque = url_elem.text if url_elem is not None else f"{BOE_API_BASE}{base}/texto/bloque/{block_id}"

    # 6. OBTENER FECHA ORIGINAL DE LA LEY
    # La fecha más antigua entre todos los bloques es la fecha original
    fechas = []
    for bloque in bloques:
        fecha_elem = bloque.find("fecha_actualizacion")
        if fecha_elem is not None and fecha_elem.text:
            fechas.append(fecha_elem.text)

    fecha_ley_original = min(fechas) if fechas else fecha_actualizacion

    # 7. DETERMINAR SI FUE MODIFICADO
    modificado = fecha_actualizacion > fecha_ley_original if fecha_actualizacion and fecha_ley_original else False

    # 8. RECONSTRUIR UBICACIÓN JERÁRQUICA
    ubicacion = _reconstruir_ubicacion(bloques, indice_encontrado)

    # 9. OBTENER TEXTO SI SE SOLICITA
    texto = None
    if incluir_texto and block_id:
        bloque_endpoint = f"{base}/texto/bloque/{block_id}"
        bloque_xml = await make_boe_raw_request(bloque_endpoint, accept="application/xml")
        if bloque_xml:
            texto = _extraer_texto_de_bloque_xml(bloque_xml)

    # 10. RETORNAR RESULTADO
    return {
        "identifier": identifier,
        "articulo": articulo,
        "block_id": block_id,
        "titulo_completo": titulo_completo,
        "fecha_actualizacion": fecha_actualizacion,
        "fecha_ley_original": fecha_ley_original,
        "modificado": modificado,
        "ubicacion": ubicacion,
        "url_bloque": url_bloque,
        "texto": texto
    }


def _es_libro(id_bloque: str) -> bool:
    """Check if block ID is a book (lp, ls, lp-2, etc.)."""
    return id_bloque.startswith("lp") or id_bloque.startswith("ls")


def _es_titulo(id_bloque: str) -> bool:
    """Check if block ID is a title (ti, ti-2, etc.)."""
    return id_bloque.startswith("ti")


def _es_capitulo(id_bloque: str) -> bool:
    """Check if block ID is a chapter (ci, cv, ci-2, etc.)."""
    return id_bloque.startswith("ci") or id_bloque.startswith("cv")


def _es_articulo(id_bloque: str) -> bool:
    """Check if block ID is an article (a1, a2, a3-72, etc.)."""
    return re.match(r'^a\d', id_bloque) is not None


def _extraer_numero_articulo(titulo: str) -> str:
    """
    Extrae el número de artículo de un título.

    Args:
        titulo: Título del artículo (ej. "Artículo 386. Legitimación")

    Returns:
        Número del artículo (ej. "386", "224 bis", "único")
    """
    titulo_lower = titulo.lower()

    # Caso especial: artículo único
    if "artículo único" in titulo_lower:
        return "único"

    # Patrón: "Artículo N" o "Artículo N sufijo"
    match = re.match(r'^artículo\s+(\d+(?:\s+(?:bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies))?)',
                     titulo_lower)
    if match:
        return match.group(1)

    return ""


@mcp.tool()
async def search_in_law(
    identifier: str,
    query: str | None = None,
    articulos: list[str] | None = None,
    solo_modificados: bool = False,
    modificados_desde: str | None = None,
    modificados_hasta: str | None = None,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """
    Busca artículos dentro de una ley que coincidan con criterios específicos.

    Permite filtrar artículos de una ley por múltiples criterios combinables:
    texto en título, lista de artículos específicos, estado de modificación
    y rango de fechas.

    Args:
        identifier: ID BOE de la ley (ej. "BOE-A-2020-4859")
        query: Texto a buscar en los títulos de los artículos (case-insensitive)
        articulos: Lista de números de artículos a buscar (ej. ["1", "2", "386"])
        solo_modificados: Si True, solo devuelve artículos que fueron modificados
        modificados_desde: Fecha mínima de modificación (AAAAMMDD)
        modificados_hasta: Fecha máxima de modificación (AAAAMMDD)
        limit: Máximo de resultados a devolver (1-200, default: 50)
        offset: Índice inicial para paginación (default: 0)

    Returns:
        Diccionario con:
        - identifier: ID de la ley
        - criterios: Dict con los criterios de búsqueda aplicados
        - total_encontrados: Número total de artículos que coinciden
        - offset: Índice inicial usado
        - limit: Límite usado
        - hay_mas: True si hay más resultados disponibles
        - resultados: Lista de artículos encontrados con:
            - articulo: Número del artículo
            - block_id: ID del bloque en la API
            - titulo: Título completo del artículo
            - fecha_actualizacion: Fecha de última modificación
            - modificado: True si fue modificado después de la publicación

        En caso de error:
        - error: True
        - codigo: "VALIDATION_ERROR" | "SIN_CRITERIOS" | "LEY_NO_ENCONTRADA" | "RANGO_FECHAS_INVALIDO"
        - mensaje: Descripción del error

    Examples:
        >>> search_in_law("BOE-A-2020-4859", solo_modificados=True)
        {"total_encontrados": 150, "resultados": [...]}

        >>> search_in_law("BOE-A-2020-4859", query="legitimación")
        {"total_encontrados": 5, "resultados": [...]}

        >>> search_in_law("BOE-A-2020-4859", articulos=["1", "2", "386"])
        {"total_encontrados": 3, "resultados": [...]}
    """
    # 1. VALIDACIÓN
    try:
        identifier = validate_boe_identifier(identifier)

        if query:
            query = validate_query_value(query)

        if articulos:
            articulos = [validate_articulo(a) for a in articulos]

        if modificados_desde:
            modificados_desde = validate_fecha(modificados_desde)

        if modificados_hasta:
            modificados_hasta = validate_fecha(modificados_hasta)

    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # Validar rango de fechas
    if modificados_desde and modificados_hasta and modificados_desde > modificados_hasta:
        return {
            "error": True,
            "codigo": "RANGO_FECHAS_INVALIDO",
            "mensaje": "modificados_desde no puede ser posterior a modificados_hasta",
            "detalles": {"desde": modificados_desde, "hasta": modificados_hasta}
        }

    # Validar que hay al menos un criterio
    if not (query or articulos or solo_modificados or modificados_desde):
        return {
            "error": True,
            "codigo": "SIN_CRITERIOS",
            "mensaje": "Debe proporcionar al menos un criterio: query, articulos, solo_modificados o modificados_desde",
            "detalles": None
        }

    # Validar límites
    limit = min(max(limit, 1), 200)
    offset = max(offset, 0)

    # 2. OBTENER ÍNDICE DE LA LEY
    base = f"/datosabiertos/api/legislacion-consolidada/id/{identifier}"
    indice_endpoint = f"{base}/texto/indice"

    indice_xml = await make_boe_raw_request(indice_endpoint, accept="application/xml")

    if indice_xml is None:
        return {
            "error": True,
            "codigo": "LEY_NO_ENCONTRADA",
            "mensaje": f"No se pudo recuperar la ley {identifier}",
            "detalles": {"identifier": identifier}
        }

    # 3. PARSEAR XML
    try:
        root = ET.fromstring(indice_xml)
        bloques = root.findall(".//bloque")
    except ET.ParseError as e:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "Error procesando respuesta de la API",
            "detalles": {"error_xml": str(e)}
        }

    if not bloques:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "La ley no contiene bloques de texto",
            "detalles": None
        }

    # Obtener fecha original de la ley
    fechas = []
    for bloque in bloques:
        fecha_elem = bloque.find("fecha_actualizacion")
        if fecha_elem is not None and fecha_elem.text:
            fechas.append(fecha_elem.text)

    fecha_ley_original = min(fechas) if fechas else ""

    # 4. FILTRAR ARTÍCULOS
    resultados = []

    for bloque in bloques:
        titulo_elem = bloque.find("titulo")
        if titulo_elem is None or titulo_elem.text is None:
            continue

        titulo = titulo_elem.text
        titulo_lower = titulo.lower()

        # Solo procesar bloques que son artículos
        if not titulo_lower.startswith("artículo"):
            continue

        id_elem = bloque.find("id")
        fecha_elem = bloque.find("fecha_actualizacion")

        block_id = id_elem.text if id_elem is not None else ""
        fecha_actualizacion = fecha_elem.text if fecha_elem is not None else ""

        num_articulo = _extraer_numero_articulo(titulo)
        es_modificado = fecha_actualizacion > fecha_ley_original if fecha_actualizacion and fecha_ley_original else False

        # Aplicar filtros

        # Filtro por lista de artículos específicos
        if articulos and num_articulo not in articulos:
            continue

        # Filtro por query en título
        if query and query.lower() not in titulo_lower:
            continue

        # Filtro por solo modificados
        if solo_modificados and not es_modificado:
            continue

        # Filtro por fecha desde
        if modificados_desde and fecha_actualizacion < modificados_desde:
            continue

        # Filtro por fecha hasta
        if modificados_hasta and fecha_actualizacion > modificados_hasta:
            continue

        resultados.append({
            "articulo": num_articulo,
            "block_id": block_id,
            "titulo": titulo,
            "fecha_actualizacion": fecha_actualizacion,
            "modificado": es_modificado
        })

    # 5. PAGINAR
    total = len(resultados)
    resultados_paginados = resultados[offset:offset + limit]
    hay_mas = (offset + limit) < total

    # 6. RETORNAR
    return {
        "identifier": identifier,
        "criterios": {
            "query": query,
            "articulos": articulos,
            "solo_modificados": solo_modificados,
            "modificados_desde": modificados_desde,
            "modificados_hasta": modificados_hasta
        },
        "total_encontrados": total,
        "offset": offset,
        "limit": limit,
        "hay_mas": hay_mas,
        "resultados": resultados_paginados
    }


@mcp.tool()
async def get_law_structure_summary(
    identifier: str,
    nivel: Literal["libros", "titulos", "capitulos"] = "capitulos"
) -> dict:
    """
    Obtiene un resumen compacto de la estructura jerárquica de una ley.

    Devuelve la organización de la ley (libros, títulos, capítulos) sin
    incluir artículos individuales. Útil para entender la estructura de
    leyes extensas antes de navegar a secciones específicas.

    Args:
        identifier: ID BOE de la ley (ej. "BOE-A-2020-4859")
        nivel: Profundidad de la estructura a devolver:
            - "libros": Solo libros (nivel más alto)
            - "titulos": Libros y títulos
            - "capitulos": Libros, títulos y capítulos (default)

    Returns:
        Diccionario con:
        - identifier: ID de la ley
        - titulo: Título completo de la ley
        - fecha_publicacion: Fecha de publicación original
        - total_articulos: Número total de artículos
        - total_modificados: Artículos modificados
        - estructura: Lista jerárquica con:
            - id: ID del bloque
            - tipo: "libro" | "titulo" | "capitulo"
            - titulo: Texto del título
            - num_articulos: Artículos en esta sección
            - num_modificados: Artículos modificados en esta sección
            - hijos: Subestructura (si aplica según nivel)

        En caso de error:
        - error: True
        - codigo: "VALIDATION_ERROR" | "LEY_NO_ENCONTRADA"
        - mensaje: Descripción del error

    Examples:
        >>> get_law_structure_summary("BOE-A-2020-4859")
        {"titulo": "Ley Concursal", "estructura": [{"tipo": "libro", ...}]}

        >>> get_law_structure_summary("BOE-A-2020-4859", nivel="libros")
        {"estructura": [{"tipo": "libro", "hijos": []}]}
    """
    # 1. VALIDACIÓN
    try:
        identifier = validate_boe_identifier(identifier)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # 2. OBTENER ÍNDICE DE LA LEY
    base = f"/datosabiertos/api/legislacion-consolidada/id/{identifier}"
    indice_endpoint = f"{base}/texto/indice"

    indice_xml = await make_boe_raw_request(indice_endpoint, accept="application/xml")

    if indice_xml is None:
        return {
            "error": True,
            "codigo": "LEY_NO_ENCONTRADA",
            "mensaje": f"No se pudo recuperar la ley {identifier}",
            "detalles": {"identifier": identifier}
        }

    # 3. PARSEAR XML
    try:
        root = ET.fromstring(indice_xml)
        bloques = root.findall(".//bloque")
    except ET.ParseError as e:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "Error procesando respuesta de la API",
            "detalles": {"error_xml": str(e)}
        }

    if not bloques:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "La ley no contiene bloques de texto",
            "detalles": None
        }

    # Obtener fecha original de la ley
    fechas = []
    for bloque in bloques:
        fecha_elem = bloque.find("fecha_actualizacion")
        if fecha_elem is not None and fecha_elem.text:
            fechas.append(fecha_elem.text)

    fecha_original = min(fechas) if fechas else ""

    # 4. EXTRAER TÍTULO DE LA LEY (bloque con id="te")
    titulo_ley = ""
    for bloque in bloques:
        id_elem = bloque.find("id")
        if id_elem is not None and id_elem.text == "te":
            titulo_elem = bloque.find("titulo")
            if titulo_elem is not None:
                titulo_ley = titulo_elem.text or ""
            break

    # Si no hay bloque "te", buscar el primer título significativo
    if not titulo_ley:
        for bloque in bloques:
            titulo_elem = bloque.find("titulo")
            if titulo_elem is not None and titulo_elem.text:
                titulo_ley = titulo_elem.text
                break

    # 5. CONSTRUIR ESTRUCTURA JERÁRQUICA
    estructura = []
    libro_actual = None
    titulo_actual = None
    capitulo_actual = None

    total_articulos = 0
    total_modificados = 0

    for bloque in bloques:
        id_elem = bloque.find("id")
        titulo_elem = bloque.find("titulo")
        fecha_elem = bloque.find("fecha_actualizacion")

        if id_elem is None or titulo_elem is None:
            continue

        id_bloque = id_elem.text or ""
        titulo_bloque = titulo_elem.text or ""
        fecha_bloque = fecha_elem.text if fecha_elem is not None else ""

        if _es_libro(id_bloque):
            libro_actual = {
                "id": id_bloque,
                "tipo": "libro",
                "titulo": titulo_bloque,
                "num_articulos": 0,
                "num_modificados": 0,
                "hijos": []
            }
            estructura.append(libro_actual)
            titulo_actual = None
            capitulo_actual = None

        elif _es_titulo(id_bloque) and nivel in ["titulos", "capitulos"]:
            titulo_actual = {
                "id": id_bloque,
                "tipo": "titulo",
                "titulo": titulo_bloque,
                "num_articulos": 0,
                "num_modificados": 0,
                "hijos": []
            }
            if libro_actual:
                libro_actual["hijos"].append(titulo_actual)
            else:
                estructura.append(titulo_actual)
            capitulo_actual = None

        elif _es_capitulo(id_bloque) and nivel == "capitulos":
            capitulo_actual = {
                "id": id_bloque,
                "tipo": "capitulo",
                "titulo": titulo_bloque,
                "num_articulos": 0,
                "num_modificados": 0,
                "hijos": []
            }
            if titulo_actual:
                titulo_actual["hijos"].append(capitulo_actual)
            elif libro_actual:
                libro_actual["hijos"].append(capitulo_actual)
            else:
                estructura.append(capitulo_actual)

        elif _es_articulo(id_bloque):
            es_modificado = fecha_bloque > fecha_original if fecha_bloque and fecha_original else False

            total_articulos += 1
            if es_modificado:
                total_modificados += 1

            # Incrementar contadores en la jerarquía
            if capitulo_actual:
                capitulo_actual["num_articulos"] += 1
                if es_modificado:
                    capitulo_actual["num_modificados"] += 1

            if titulo_actual:
                titulo_actual["num_articulos"] += 1
                if es_modificado:
                    titulo_actual["num_modificados"] += 1

            if libro_actual:
                libro_actual["num_articulos"] += 1
                if es_modificado:
                    libro_actual["num_modificados"] += 1

    # 6. RETORNAR
    return {
        "identifier": identifier,
        "titulo": titulo_ley,
        "fecha_publicacion": fecha_original,
        "total_articulos": total_articulos,
        "total_modificados": total_modificados,
        "estructura": estructura
    }


def _es_disposicion(id_bloque: str) -> bool:
    """Check if block ID is a disposition (da, dt, dd, df)."""
    return (id_bloque.startswith("da") or id_bloque.startswith("dt") or
            id_bloque.startswith("dd") or id_bloque.startswith("df"))


def _es_estructura(id_bloque: str) -> bool:
    """Check if block ID is structural (libro, título, capítulo, sección)."""
    return (_es_libro(id_bloque) or _es_titulo(id_bloque) or
            _es_capitulo(id_bloque) or re.match(r'^s\d', id_bloque) is not None)


@mcp.tool()
async def get_law_index(
    identifier: str,
    tipo_bloque: Literal["todos", "estructura", "articulos", "disposiciones"] = "todos",
    limit: int = 100,
    offset: int = 0
) -> dict:
    """
    Obtiene el índice de una ley con soporte para paginación y filtrado.

    Devuelve una lista paginada de bloques de la ley, filtrable por tipo.
    Útil para navegar leyes extensas de forma eficiente.

    Args:
        identifier: ID BOE de la ley (ej. "BOE-A-2020-4859")
        tipo_bloque: Tipo de bloques a incluir:
            - "todos": Todos los bloques (default)
            - "estructura": Solo libros, títulos, capítulos y secciones
            - "articulos": Solo artículos
            - "disposiciones": Solo disposiciones (adicionales, transitorias, etc.)
        limit: Máximo de bloques a devolver (1-500, default: 100)
        offset: Índice inicial para paginación (default: 0)

    Returns:
        Diccionario con:
        - identifier: ID de la ley
        - tipo_bloque: Filtro aplicado
        - total_bloques: Total de bloques que coinciden con el filtro
        - offset: Índice inicial usado
        - limit: Límite usado
        - hay_mas: True si hay más bloques disponibles
        - bloques: Lista de bloques con:
            - id: ID del bloque
            - titulo: Título del bloque
            - fecha_actualizacion: Fecha de última modificación
            - url: URL del bloque en la API BOE

        En caso de error:
        - error: True
        - codigo: "VALIDATION_ERROR" | "LEY_NO_ENCONTRADA"
        - mensaje: Descripción del error

    Examples:
        >>> get_law_index("BOE-A-2020-4859", limit=50)
        {"total_bloques": 800, "bloques": [...], "hay_mas": True}

        >>> get_law_index("BOE-A-2020-4859", tipo_bloque="articulos", limit=100)
        {"total_bloques": 752, "bloques": [...]}

        >>> get_law_index("BOE-A-2020-4859", tipo_bloque="estructura")
        {"total_bloques": 45, "bloques": [{"tipo": "libro", ...}]}
    """
    # 1. VALIDACIÓN
    try:
        identifier = validate_boe_identifier(identifier)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # Validar límites
    limit = min(max(limit, 1), 500)
    offset = max(offset, 0)

    # 2. OBTENER ÍNDICE DE LA LEY
    base = f"/datosabiertos/api/legislacion-consolidada/id/{identifier}"
    indice_endpoint = f"{base}/texto/indice"

    indice_xml = await make_boe_raw_request(indice_endpoint, accept="application/xml")

    if indice_xml is None:
        return {
            "error": True,
            "codigo": "LEY_NO_ENCONTRADA",
            "mensaje": f"No se pudo recuperar la ley {identifier}",
            "detalles": {"identifier": identifier}
        }

    # 3. PARSEAR XML
    try:
        root = ET.fromstring(indice_xml)
        bloques = root.findall(".//bloque")
    except ET.ParseError as e:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "Error procesando respuesta de la API",
            "detalles": {"error_xml": str(e)}
        }

    if not bloques:
        return {
            "error": True,
            "codigo": "ERROR_PARSING",
            "mensaje": "La ley no contiene bloques de texto",
            "detalles": None
        }

    # 4. FILTRAR BLOQUES
    bloques_filtrados = []

    for bloque in bloques:
        id_elem = bloque.find("id")
        titulo_elem = bloque.find("titulo")
        fecha_elem = bloque.find("fecha_actualizacion")
        url_elem = bloque.find("url_bloque")

        if id_elem is None or titulo_elem is None:
            continue

        id_bloque = id_elem.text or ""
        titulo_bloque = titulo_elem.text or ""
        fecha_bloque = fecha_elem.text if fecha_elem is not None else ""
        url_bloque = url_elem.text if url_elem is not None else f"{BOE_API_BASE}{base}/texto/bloque/{id_bloque}"

        # Aplicar filtro según tipo_bloque
        if tipo_bloque == "articulos":
            if not _es_articulo(id_bloque):
                continue
        elif tipo_bloque == "estructura":
            if not _es_estructura(id_bloque):
                continue
        elif tipo_bloque == "disposiciones":
            if not _es_disposicion(id_bloque):
                continue
        # "todos" no filtra nada

        bloques_filtrados.append({
            "id": id_bloque,
            "titulo": titulo_bloque,
            "fecha_actualizacion": fecha_bloque,
            "url": url_bloque
        })

    # 5. PAGINAR
    total = len(bloques_filtrados)
    bloques_paginados = bloques_filtrados[offset:offset + limit]
    hay_mas = (offset + limit) < total

    # 6. RETORNAR
    return {
        "identifier": identifier,
        "tipo_bloque": tipo_bloque,
        "total_bloques": total,
        "offset": offset,
        "limit": limit,
        "hay_mas": hay_mas,
        "bloques": bloques_paginados
    }


# ----------- 2. SUMARIO BOE -------------------------------

class boe_summaryParams(BaseModel):
    fecha: Annotated[str, Field(description="Fecha del sumario solicitado")]

@mcp.tool()
async def get_boe_summary(params: boe_summaryParams) -> Union[dict, str]:
    """
    Obtener sumario del BOE para una fecha (AAAAMMDD).

    Args:
        fecha: Fecha del BOE (ej: 20240501)
    """
    fecha = params.fecha

    # v1.3.0: Input validation
    try:
        fecha = validate_fecha(fecha)
    except ValidationError as e:
        return f"Error de validación: {e}"

    endpoint = f"/datosabiertos/api/boe/sumario/{fecha}"
    data = await make_boe_request(endpoint)

    if not data or "data" not in data or "sumario" not in data["data"]:
        return f"No se pudo obtener el sumario del BOE para {fecha}."

    return data

    '''
    sumario = data["data"]["sumario"]
    lineas = [f"🗓️ BOE {fecha} — {len(sumario.get('diario', []))} diarios"]
    for diario in sumario.get("diario", []):
        identificador = diario.get("sumario_diario", {}).get("identificador")
        url_pdf = diario.get("sumario_diario", {}).get("url_pdf", {}).get("texto")
        lineas.append(f"- {identificador}: {url_pdf}")
    return "\n".join(lineas)
    '''


# ----------- 2.1 SMART SUMMARY BOE (v1.5.0) ---------------


def _contar_items_seccion(seccion: dict) -> int:
    """
    Cuenta el total de items (documentos) en una sección del sumario.

    La estructura de la API es compleja: items pueden estar en:
    - departamento.item (directo)
    - departamento.epigrafe[].item (dentro de epígrafe)
    - departamento.texto.epigrafe[].item (dentro de texto.epigrafe)

    Args:
        seccion: Diccionario de una sección del sumario

    Returns:
        Número total de items en la sección
    """
    total = 0
    depts = seccion.get("departamento", [])
    if not isinstance(depts, list):
        depts = [depts] if depts else []

    for dept in depts:
        # Items directos en departamento
        items = dept.get("item", [])
        if not isinstance(items, list):
            items = [items] if items else []
        total += len(items)

        # Items en epígrafes directos
        epigrafes = dept.get("epigrafe", [])
        if not isinstance(epigrafes, list):
            epigrafes = [epigrafes] if epigrafes else []
        for ep in epigrafes:
            items_ep = ep.get("item", [])
            if not isinstance(items_ep, list):
                items_ep = [items_ep] if items_ep else []
            total += len(items_ep)

        # Items en texto.epigrafe
        texto = dept.get("texto", {})
        if texto:
            epigrafes_t = texto.get("epigrafe", [])
            if not isinstance(epigrafes_t, list):
                epigrafes_t = [epigrafes_t] if epigrafes_t else []
            for ep in epigrafes_t:
                items_t = ep.get("item", [])
                if not isinstance(items_t, list):
                    items_t = [items_t] if items_t else []
                total += len(items_t)

    return total


def _extraer_items_seccion(seccion: dict) -> list[dict]:
    """
    Extrae todos los items (documentos) de una sección con su contexto.

    Args:
        seccion: Diccionario de una sección del sumario

    Returns:
        Lista de diccionarios con info de cada documento
    """
    items_list = []
    depts = seccion.get("departamento", [])
    if not isinstance(depts, list):
        depts = [depts] if depts else []

    for dept in depts:
        dept_nombre = dept.get("nombre", "")
        dept_codigo = dept.get("codigo", "")

        # Items directos en departamento
        items = dept.get("item", [])
        if not isinstance(items, list):
            items = [items] if items else []
        for item in items:
            items_list.append(_item_to_dict(item, dept_nombre, dept_codigo, None))

        # Items en epígrafes directos
        epigrafes = dept.get("epigrafe", [])
        if not isinstance(epigrafes, list):
            epigrafes = [epigrafes] if epigrafes else []
        for ep in epigrafes:
            ep_nombre = ep.get("nombre", "")
            items_ep = ep.get("item", [])
            if not isinstance(items_ep, list):
                items_ep = [items_ep] if items_ep else []
            for item in items_ep:
                items_list.append(_item_to_dict(item, dept_nombre, dept_codigo, ep_nombre))

        # Items en texto.epigrafe
        texto = dept.get("texto", {})
        if texto:
            epigrafes_t = texto.get("epigrafe", [])
            if not isinstance(epigrafes_t, list):
                epigrafes_t = [epigrafes_t] if epigrafes_t else []
            for ep in epigrafes_t:
                ep_nombre = ep.get("nombre", "")
                items_t = ep.get("item", [])
                if not isinstance(items_t, list):
                    items_t = [items_t] if items_t else []
                for item in items_t:
                    items_list.append(_item_to_dict(item, dept_nombre, dept_codigo, ep_nombre))

    return items_list


def _item_to_dict(
    item: dict, dept_nombre: str, dept_codigo: str, epigrafe: str | None
) -> dict:
    """
    Convierte un item del sumario a diccionario estructurado.

    Args:
        item: Diccionario del item de la API
        dept_nombre: Nombre del departamento
        dept_codigo: Código del departamento
        epigrafe: Nombre del epígrafe (opcional)

    Returns:
        Diccionario estructurado del documento
    """
    url_pdf = item.get("url_pdf", {})
    if isinstance(url_pdf, dict):
        url_pdf = url_pdf.get("texto", "")

    url_html = item.get("url_html", {})
    if isinstance(url_html, dict):
        url_html = url_html.get("texto", "")

    return {
        "identificador": item.get("identificador", ""),
        "titulo": item.get("titulo", ""),
        "departamento": dept_nombre,
        "departamento_codigo": dept_codigo,
        "epigrafe": epigrafe,
        "url_pdf": url_pdf,
        "url_html": url_html,
    }


@mcp.tool()
async def get_boe_summary_metadata(fecha: str) -> dict:
    """
    Obtener resumen compacto del sumario BOE con conteo por sección.

    Esta herramienta proporciona una vista general del BOE de un día específico,
    mostrando cuántos documentos hay en cada sección. Es la herramienta recomendada
    como primer paso para explorar el BOE del día.

    NOTA: Para obtener los documentos de una sección específica, usar
    get_boe_summary_section después de esta herramienta.

    Args:
        fecha: Fecha del BOE en formato AAAAMMDD (ej: "20241202")

    Returns:
        Diccionario con:
        - fecha: Fecha solicitada
        - numero_boe: Número del boletín
        - identificador: Identificador del sumario (BOE-S-YYYY-NNN)
        - url_pdf_sumario: URL del PDF del sumario
        - total_documentos: Total de documentos en el día
        - secciones: Lista de secciones con código, nombre y num_items

        En caso de error:
        - error: True
        - codigo: Código de error (VALIDATION_ERROR, SUMARIO_NO_DISPONIBLE)
        - mensaje: Descripción del error
        - detalles: Información adicional (opcional)

    Examples:
        >>> get_boe_summary_metadata("20241202")
        {
            "fecha": "20241202",
            "numero_boe": "290",
            "total_documentos": 238,
            "secciones": [
                {"codigo": "1", "nombre": "I. Disposiciones generales", "num_items": 2},
                ...
            ]
        }
    """
    # 1. VALIDACIÓN
    try:
        fecha = validate_fecha(fecha)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    # 2. REQUEST A API
    endpoint = f"/datosabiertos/api/boe/sumario/{fecha}"
    data = await make_boe_request(endpoint)

    if not data or "data" not in data or "sumario" not in data["data"]:
        return {
            "error": True,
            "codigo": "SUMARIO_NO_DISPONIBLE",
            "mensaje": f"No hay sumario BOE disponible para {fecha}. "
                       "Puede ser domingo o festivo.",
            "detalles": None
        }

    # 3. PROCESAR DATOS
    sumario = data["data"]["sumario"]
    diario = sumario.get("diario", [])
    if isinstance(diario, list) and len(diario) > 0:
        diario = diario[0]
    elif not isinstance(diario, dict):
        diario = {}

    numero_boe = diario.get("numero", "")
    sumario_diario = diario.get("sumario_diario", {})
    identificador = sumario_diario.get("identificador", "")
    url_pdf = sumario_diario.get("url_pdf", {})
    if isinstance(url_pdf, dict):
        url_pdf = url_pdf.get("texto", "")

    # Procesar secciones
    secciones_data = diario.get("seccion", [])
    if not isinstance(secciones_data, list):
        secciones_data = [secciones_data] if secciones_data else []

    secciones = []
    total_documentos = 0

    for sec in secciones_data:
        codigo = sec.get("codigo", "")
        nombre = sec.get("nombre", "")
        num_items = _contar_items_seccion(sec)
        total_documentos += num_items
        secciones.append({
            "codigo": codigo,
            "nombre": nombre,
            "num_items": num_items
        })

    # 4. RETORNAR
    return {
        "fecha": fecha,
        "numero_boe": numero_boe,
        "identificador": identificador,
        "url_pdf_sumario": url_pdf,
        "total_documentos": total_documentos,
        "secciones": secciones
    }


@mcp.tool()
async def get_boe_summary_section(
    fecha: str,
    seccion: str,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    Obtener documentos de una sección específica del BOE con paginación.

    Esta herramienta permite explorar los documentos de una sección concreta
    del BOE, con soporte para paginación para manejar secciones con muchos
    documentos.

    Códigos de sección válidos:
    - "1": Disposiciones generales
    - "2A": Autoridades y personal - Nombramientos
    - "2B": Autoridades y personal - Oposiciones y concursos
    - "3": Otras disposiciones
    - "4": Administración de Justicia
    - "5A": Anuncios - Contratación del Sector Público
    - "5B": Anuncios - Otros anuncios oficiales
    - "5C": Anuncios - Anuncios particulares

    Args:
        fecha: Fecha del BOE en formato AAAAMMDD (ej: "20241202")
        seccion: Código de sección (ej: "1", "2A", "2B", "3", "4", "5A", "5B", "5C")
        limit: Máximo número de documentos a devolver (default: 20, max: 100)
        offset: Número de documentos a saltar para paginación (default: 0)

    Returns:
        Diccionario con:
        - fecha: Fecha solicitada
        - seccion: Info de la sección (codigo, nombre)
        - total_items: Total de documentos en la sección
        - offset: Offset actual
        - limit: Límite actual
        - hay_mas: True si hay más documentos disponibles
        - documentos: Lista de documentos con identificador, titulo, departamento, etc.

        En caso de error:
        - error: True
        - codigo: Código de error
        - mensaje: Descripción del error
        - detalles: Información adicional

    Examples:
        >>> get_boe_summary_section("20241202", "2B", limit=10)
        {
            "fecha": "20241202",
            "seccion": {"codigo": "2B", "nombre": "II. Autoridades..."},
            "total_items": 33,
            "hay_mas": True,
            "documentos": [...]
        }
    """
    # 1. VALIDACIÓN
    try:
        fecha = validate_fecha(fecha)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": {"parametro": "fecha"}
        }

    try:
        seccion = validate_seccion_boe(seccion)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": {"parametro": "seccion"}
        }

    # Validar limit y offset
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100

    if offset < 0:
        offset = 0

    # 2. REQUEST A API
    endpoint = f"/datosabiertos/api/boe/sumario/{fecha}"
    data = await make_boe_request(endpoint)

    if not data or "data" not in data or "sumario" not in data["data"]:
        return {
            "error": True,
            "codigo": "SUMARIO_NO_DISPONIBLE",
            "mensaje": f"No hay sumario BOE disponible para {fecha}. "
                       "Puede ser domingo o festivo.",
            "detalles": None
        }

    # 3. PROCESAR DATOS
    sumario = data["data"]["sumario"]
    diario = sumario.get("diario", [])
    if isinstance(diario, list) and len(diario) > 0:
        diario = diario[0]
    elif not isinstance(diario, dict):
        diario = {}

    # Buscar la sección solicitada
    secciones_data = diario.get("seccion", [])
    if not isinstance(secciones_data, list):
        secciones_data = [secciones_data] if secciones_data else []

    seccion_encontrada = None
    for sec in secciones_data:
        if sec.get("codigo", "").upper() == seccion:
            seccion_encontrada = sec
            break

    if not seccion_encontrada:
        return {
            "error": True,
            "codigo": "SECCION_NO_ENCONTRADA",
            "mensaje": f"Sección '{seccion}' no encontrada en el BOE del {fecha}",
            "detalles": {
                "secciones_disponibles": [s.get("codigo") for s in secciones_data]
            }
        }

    # Extraer items de la sección
    todos_items = _extraer_items_seccion(seccion_encontrada)
    total_items = len(todos_items)

    # Aplicar paginación
    items_paginados = todos_items[offset:offset + limit]
    hay_mas = (offset + limit) < total_items

    # 4. RETORNAR
    return {
        "fecha": fecha,
        "seccion": {
            "codigo": seccion_encontrada.get("codigo", ""),
            "nombre": seccion_encontrada.get("nombre", "")
        },
        "total_items": total_items,
        "offset": offset,
        "limit": limit,
        "hay_mas": hay_mas,
        "documentos": items_paginados
    }


@mcp.tool()
async def get_boe_document_info(identificador: str, fecha: str | None = None) -> dict:
    """
    Obtener información detallada de un documento específico del BOE.

    Esta herramienta permite obtener los detalles de un documento cuando
    se conoce su identificador (ej: BOE-A-2024-25060). Si se proporciona
    la fecha de publicación, busca en el sumario de ese día para obtener
    información completa. Si no se proporciona fecha, devuelve URLs básicas.

    NOTA: Para obtener información completa (título, departamento, etc.),
    proporciona la fecha de publicación. Si solo tienes el identificador,
    usa get_boe_summary_section para encontrar el documento en una sección.

    Args:
        identificador: Identificador del documento BOE (ej: "BOE-A-2024-25060")
        fecha: Fecha de publicación AAAAMMDD (opcional, mejora resultados)

    Returns:
        Diccionario con información del documento:
        - identificador: ID del documento
        - titulo: Título completo (si se proporciona fecha)
        - departamento: Nombre del departamento (si se proporciona fecha)
        - url_pdf: URL del PDF
        - url_html: URL de la versión HTML
        - url_xml: URL de la versión XML

        En caso de error:
        - error: True
        - codigo: Código de error (VALIDATION_ERROR, DOCUMENTO_NO_ENCONTRADO)
        - mensaje: Descripción del error
        - detalles: Información adicional

    Examples:
        >>> get_boe_document_info("BOE-A-2024-25051", "20241202")
        {
            "identificador": "BOE-A-2024-25051",
            "titulo": "Ley 5/2024, de 13 de noviembre...",
            "departamento": "COMUNIDAD AUTÓNOMA DE CANARIAS",
            ...
        }
    """
    # 1. VALIDACIÓN
    try:
        identificador = validate_boe_identifier(identificador)
    except ValidationError as e:
        return {
            "error": True,
            "codigo": "VALIDATION_ERROR",
            "mensaje": str(e),
            "detalles": None
        }

    if fecha:
        try:
            fecha = validate_fecha(fecha)
        except ValidationError as e:
            return {
                "error": True,
                "codigo": "VALIDATION_ERROR",
                "mensaje": str(e),
                "detalles": {"parametro": "fecha"}
            }

    # 2. SI HAY FECHA, BUSCAR EN SUMARIO
    if fecha:
        endpoint = f"/datosabiertos/api/boe/sumario/{fecha}"
        data = await make_boe_request(endpoint)

        if data and "data" in data and "sumario" in data["data"]:
            # Buscar el documento en el sumario
            doc_info = _buscar_documento_en_sumario(data, identificador)
            if doc_info:
                return doc_info

        # Si no se encontró en el sumario de esa fecha
        return {
            "error": True,
            "codigo": "DOCUMENTO_NO_ENCONTRADO",
            "mensaje": f"No se encontró {identificador} en el BOE del {fecha}",
            "detalles": {
                "sugerencia": "Verifique que la fecha sea correcta o use get_boe_summary_section"
            }
        }

    # 3. SIN FECHA: DEVOLVER URLs BÁSICAS
    # Construir URLs estándar del BOE
    url_html = f"https://www.boe.es/diario_boe/txt.php?id={identificador}"
    url_xml = f"https://www.boe.es/diario_boe/xml.php?id={identificador}"

    return {
        "identificador": identificador,
        "titulo": None,
        "departamento": None,
        "seccion": None,
        "epigrafe": None,
        "fecha_publicacion": None,
        "url_pdf": None,  # No podemos construir sin fecha
        "url_html": url_html,
        "url_xml": url_xml,
        "nota": "Para información completa, proporcione la fecha de publicación"
    }


def _buscar_documento_en_sumario(data: dict, identificador: str) -> dict | None:
    """
    Busca un documento por identificador en la estructura del sumario.

    Args:
        data: Respuesta completa del API de sumario
        identificador: ID del documento a buscar

    Returns:
        Diccionario con info del documento o None si no se encuentra
    """
    sumario = data["data"]["sumario"]
    diario = sumario.get("diario", [])
    if isinstance(diario, list) and len(diario) > 0:
        diario = diario[0]
    elif not isinstance(diario, dict):
        return None

    secciones = diario.get("seccion", [])
    if not isinstance(secciones, list):
        secciones = [secciones] if secciones else []

    for seccion in secciones:
        seccion_codigo = seccion.get("codigo", "")
        seccion_nombre = seccion.get("nombre", "")

        depts = seccion.get("departamento", [])
        if not isinstance(depts, list):
            depts = [depts] if depts else []

        for dept in depts:
            dept_nombre = dept.get("nombre", "")
            dept_codigo = dept.get("codigo", "")

            # Buscar en items directos
            result = _buscar_en_items(
                dept.get("item", []),
                identificador, dept_nombre, dept_codigo,
                seccion_codigo, seccion_nombre, None
            )
            if result:
                return result

            # Buscar en epígrafes
            epigrafes = dept.get("epigrafe", [])
            if not isinstance(epigrafes, list):
                epigrafes = [epigrafes] if epigrafes else []
            for ep in epigrafes:
                result = _buscar_en_items(
                    ep.get("item", []),
                    identificador, dept_nombre, dept_codigo,
                    seccion_codigo, seccion_nombre, ep.get("nombre", "")
                )
                if result:
                    return result

            # Buscar en texto.epigrafe
            texto = dept.get("texto", {})
            if texto:
                epigrafes_t = texto.get("epigrafe", [])
                if not isinstance(epigrafes_t, list):
                    epigrafes_t = [epigrafes_t] if epigrafes_t else []
                for ep in epigrafes_t:
                    result = _buscar_en_items(
                        ep.get("item", []),
                        identificador, dept_nombre, dept_codigo,
                        seccion_codigo, seccion_nombre, ep.get("nombre", "")
                    )
                    if result:
                        return result

    return None


def _buscar_en_items(
    items: list | dict,
    identificador: str,
    dept_nombre: str,
    dept_codigo: str,
    seccion_codigo: str,
    seccion_nombre: str,
    epigrafe: str | None
) -> dict | None:
    """Busca un identificador en una lista de items."""
    if not isinstance(items, list):
        items = [items] if items else []

    for item in items:
        if item.get("identificador") == identificador:
            # Extraer URL del PDF
            url_pdf = item.get("url_pdf", {})
            if isinstance(url_pdf, dict):
                url_pdf_texto = url_pdf.get("texto", "")
                pagina_inicial = url_pdf.get("pagina_inicial", "")
                pagina_final = url_pdf.get("pagina_final", "")
            else:
                url_pdf_texto = url_pdf
                pagina_inicial = ""
                pagina_final = ""

            return {
                "identificador": identificador,
                "titulo": item.get("titulo", ""),
                "departamento": dept_nombre,
                "departamento_codigo": dept_codigo,
                "seccion": {
                    "codigo": seccion_codigo,
                    "nombre": seccion_nombre
                },
                "epigrafe": epigrafe,
                "url_pdf": url_pdf_texto,
                "url_html": item.get("url_html", ""),
                "url_xml": item.get("url_xml", ""),
                "paginas": {
                    "inicial": pagina_inicial,
                    "final": pagina_final
                } if pagina_inicial else None
            }

    return None


# ----------- 3. SUMARIO BORME -----------------------------

@mcp.tool()
async def get_borme_summary(fecha: str) -> Union[dict, str]:
    """
    Obtener sumario del BORME para una fecha (AAAAMMDD).

    Args:
        fecha: Fecha del BORME (ej: 20240501)
    """
    # v1.3.0: Input validation
    try:
        fecha = validate_fecha(fecha)
    except ValidationError as e:
        return f"Error de validación: {e}"

    endpoint = f"/datosabiertos/api/borme/sumario/{fecha}"
    data = await make_boe_request(endpoint)

    if not data or "data" not in data or "sumario" not in data["data"]:
        return f"No se pudo obtener el sumario del BORME para {fecha}."

    return data

    '''
    sumario = data["data"]["sumario"]
    resultados = [f"🗓️ BORME {fecha} — {len(sumario.get('diario', []))} diarios"]
    for diario in sumario.get("diario", []):
        identificador = diario.get("sumario_diario", {}).get("identificador")
        url_pdf = diario.get("sumario_diario", {}).get("url_pdf", {}).get("texto")
        resultados.append(f"- {identificador}: {url_pdf}")
    return "\n".join(resultados)
    '''

# ----------- 4. TABLAS AUXILIARES -------------------------

@mcp.tool()
async def get_auxiliary_table(table_name: str) -> Union[dict, str]:
    """
    Consultar tablas auxiliares disponibles en la API del BOE. Dichas tabls incluyem los 
    códigos de materias, ámbitos, estados de consolidación, departamentos, rangos y relaciones.
    Estos códigos se pueden usar para usar en las queries de la función search_consolidated_laws_list
    
    Args:
        table_name: Una de las siguientes:
        'materias', 'ambitos', 'estados-consolidacion',
        'departamentos', 'rangos', 'relaciones-anteriores', 'relaciones-posteriores'
    """
    valid_tables = [
        "materias", "ambitos", "estados-consolidacion",
        "departamentos", "rangos", "relaciones-anteriores", "relaciones-posteriores"
    ]
    if table_name not in valid_tables:
        return f"Tabla no válida. Usa una de: {', '.join(valid_tables)}"

    endpoint = f"/datosabiertos/api/datos-auxiliares/{table_name}"
    data = await make_boe_request(endpoint)

    if not data:
        return f"No se pudo recuperar la tabla {table_name}."

    return data
    
    '''
    # Si data es un dict, intenta extraer la lista bajo la clave 'data'
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        rows = data["data"]
    elif isinstance(data, list):
        rows = data
    else:
        return f"No se pudo recuperar la tabla {table_name}."

    # Asegura que rows es una lista antes de hacer slicing
    rows = list(rows)

    lines = [f"📘 Tabla: {table_name}", "----------------"]
    for row in rows[:10]:  # primeros 10 elementos
        if isinstance(row, dict):
            code = row.get("codigo", "N/A")
            desc = row.get("descripcion", "Sin descripción")
            lines.append(f"{code}: {desc}")
        else:
            lines.append(str(row))
    return "\n".join(lines)
    '''

# ------------------- ENTRY POINT ---------------------------

# Main function
def main():
    """Arrancar el servidor mcp"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()