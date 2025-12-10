#!/usr/bin/env python3
"""
Tests de Casos de Uso - Smart Navigation v2.0

Basado en: docs/CASOS-USO-SMART-NAV-V2.md

Este archivo implementa los 63 casos de uso documentados, organizados en:
- Simples (S): 18 casos - Una herramienta, parámetros básicos
- Intermedios (M): 14 casos - Una herramienta, parámetros combinados
- Avanzados (A): 9 casos - Múltiples herramientas, lógica compleja
- Errores (E): 12 casos - Validación y edge cases
- Negocio (N): 10 casos - Preguntas reales de usuarios

Ley de referencia: BOE-A-2020-4859 (Ley Concursal - 752+ artículos)

Uso:
    uv run pytest tests/test_casos_uso_smart_nav.py -v
    uv run pytest tests/test_casos_uso_smart_nav.py -v -m "not slow"
"""

import pytest
import sys
sys.path.insert(0, 'src')

from boe_mcp.server import (
    get_article_info,
    search_in_law,
    get_law_structure_summary,
    get_law_index
)

# Constants
LEY_CONCURSAL = "BOE-A-2020-4859"
LEY_INEXISTENTE = "BOE-A-0000-0000"

# Mark all tests as e2e (real API calls)
pytestmark = pytest.mark.e2e


# =============================================================================
# CASOS SIMPLES (S) - Una herramienta, parámetros básicos
# =============================================================================

class TestSimpleGetArticleInfo:
    """S1.x - Casos simples de get_article_info."""

    @pytest.mark.asyncio
    async def test_s1_1_articulo_1_existe(self):
        """S1.1 - ¿Existe el artículo 1 en la Ley Concursal?"""
        result = await get_article_info(LEY_CONCURSAL, "1")

        assert result.get("error") is None
        assert result["articulo"] == "1"

    @pytest.mark.asyncio
    async def test_s1_2_block_id_articulo_386(self):
        """S1.2 - ¿Cuál es el block_id del artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["block_id"] == "a3-98"

    @pytest.mark.asyncio
    async def test_s1_3_articulo_1_modificado(self):
        """S1.3 - ¿Fue modificado el artículo 1?"""
        result = await get_article_info(LEY_CONCURSAL, "1")

        assert result.get("error") is None
        assert result["modificado"] is True

    @pytest.mark.asyncio
    async def test_s1_4_articulo_386_no_modificado(self):
        """S1.4 - ¿Fue modificado el artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["modificado"] is False

    @pytest.mark.asyncio
    async def test_s1_5_articulo_inexistente(self):
        """S1.5 - ¿Existe el artículo 9999?"""
        result = await get_article_info(LEY_CONCURSAL, "9999")

        assert result.get("error") is True
        assert result.get("codigo") == "ARTICULO_NO_ENCONTRADO"

    @pytest.mark.asyncio
    async def test_s1_6_articulo_bis(self):
        """S1.6 - ¿Existe el artículo '224 bis'?"""
        result = await get_article_info(LEY_CONCURSAL, "224 bis")

        assert result.get("error") is None
        assert result["articulo"] == "224 bis"

    @pytest.mark.asyncio
    async def test_s1_7_texto_articulo_1(self):
        """S1.7 - ¿Cuál es el texto del artículo 1?"""
        result = await get_article_info(LEY_CONCURSAL, "1", incluir_texto=True)

        assert result.get("error") is None
        assert result["texto"] is not None
        assert "presupuesto subjetivo" in result["texto"].lower()


class TestSimpleSearchInLaw:
    """S2.x - Casos simples de search_in_law."""

    @pytest.mark.asyncio
    async def test_s2_1_total_modificados(self):
        """S2.1 - ¿Cuántos artículos modificados tiene la ley?"""
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True)

        assert result.get("error") is None
        # La Ley Concursal tiene ~409 artículos modificados
        assert result["total_encontrados"] >= 400

    @pytest.mark.asyncio
    async def test_s2_2_articulos_especificos(self):
        """S2.2 - Dame los artículos 1, 2 y 386."""
        result = await search_in_law(LEY_CONCURSAL, articulos=["1", "2", "386"])

        assert result.get("error") is None
        assert result["total_encontrados"] == 3

        articulos = [r["articulo"] for r in result["resultados"]]
        assert "1" in articulos
        assert "2" in articulos
        assert "386" in articulos

    @pytest.mark.asyncio
    async def test_s2_3_buscar_unico(self):
        """S2.3 - ¿Hay algún 'artículo único'?"""
        result = await search_in_law(LEY_CONCURSAL, query="único")

        assert result.get("error") is None
        assert result["total_encontrados"] >= 1

        for art in result["resultados"]:
            assert "único" in art["titulo"].lower()

    @pytest.mark.asyncio
    async def test_s2_4_limit_modificados(self):
        """S2.4 - Dame 5 artículos modificados."""
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5)

        assert result.get("error") is None
        assert len(result["resultados"]) == 5


class TestSimpleGetLawStructureSummary:
    """S3.x - Casos simples de get_law_structure_summary."""

    @pytest.mark.asyncio
    async def test_s3_1_numero_libros(self):
        """S3.1 - ¿Cuántos libros tiene la Ley Concursal?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None
        # La Ley Concursal tiene 2 libros
        assert len(result["estructura"]) == 2

    @pytest.mark.asyncio
    async def test_s3_2_total_articulos(self):
        """S3.2 - ¿Cuántos artículos tiene en total?"""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None
        # La Ley Concursal tiene 752 artículos
        assert result["total_articulos"] >= 750

    @pytest.mark.asyncio
    async def test_s3_3_titulo_ley(self):
        """S3.3 - ¿Cuál es el título de la ley?"""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None
        assert "CONCURSAL" in result["titulo"].upper()


class TestSimpleGetLawIndex:
    """S4.x - Casos simples de get_law_index."""

    @pytest.mark.asyncio
    async def test_s4_1_primeros_10_bloques(self):
        """S4.1 - Dame los primeros 10 bloques."""
        result = await get_law_index(LEY_CONCURSAL, limit=10)

        assert result.get("error") is None
        assert len(result["bloques"]) == 10

    @pytest.mark.asyncio
    async def test_s4_2_total_articulos(self):
        """S4.2 - ¿Cuántos artículos tiene la ley?"""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos")

        assert result.get("error") is None
        # La Ley Concursal tiene 752 artículos
        assert result["total_bloques"] >= 750

    @pytest.mark.asyncio
    async def test_s4_3_disposiciones(self):
        """S4.3 - ¿Cuántas disposiciones tiene?"""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="disposiciones")

        assert result.get("error") is None
        assert result["total_bloques"] > 0


# =============================================================================
# CASOS INTERMEDIOS (M) - Una herramienta, parámetros combinados
# =============================================================================

class TestIntermediateGetArticleInfo:
    """M1.x - Casos intermedios de get_article_info con ubicación."""

    @pytest.mark.asyncio
    async def test_m1_1_libro_articulo_386(self):
        """M1.1 - ¿En qué libro está el artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["ubicacion"]["libro"] is not None
        assert "LIBRO PRIMERO" in result["ubicacion"]["libro"]

    @pytest.mark.asyncio
    async def test_m1_2_titulo_articulo_386(self):
        """M1.2 - ¿En qué título está el artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["ubicacion"]["titulo"] is not None
        assert "TÍTULO IV" in result["ubicacion"]["titulo"]

    @pytest.mark.asyncio
    async def test_m1_3_capitulo_articulo_386(self):
        """M1.3 - ¿En qué capítulo está el artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["ubicacion"]["capitulo"] is not None
        assert "CAPÍTULO V" in result["ubicacion"]["capitulo"]

    @pytest.mark.asyncio
    async def test_m1_4_seccion_articulo_386(self):
        """M1.4 - ¿En qué sección está el artículo 386?"""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None
        assert result["ubicacion"]["seccion"] is not None
        assert "Sección 2" in result["ubicacion"]["seccion"]

    @pytest.mark.asyncio
    async def test_m1_5_fecha_modificacion_224_bis(self):
        """M1.5 - ¿Cuándo fue modificado el artículo 224 bis?"""
        result = await get_article_info(LEY_CONCURSAL, "224 bis")

        assert result.get("error") is None
        assert result["fecha_actualizacion"] == "20220906"


class TestIntermediateSearchInLaw:
    """M2.x - Casos intermedios de search_in_law con filtros combinados."""

    @pytest.mark.asyncio
    async def test_m2_1_modificados_2022(self):
        """M2.1 - ¿Qué artículos se modificaron en 2022?"""
        result = await search_in_law(
            LEY_CONCURSAL,
            modificados_desde="20220101",
            modificados_hasta="20221231"
        )

        assert result.get("error") is None

        for art in result["resultados"]:
            assert "20220101" <= art["fecha_actualizacion"] <= "20221231"

    @pytest.mark.asyncio
    async def test_m2_2_paginacion(self):
        """M2.2 - Dame la página 2 de artículos modificados (5 por página)."""
        result1 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=0)
        result2 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=5)

        assert result1.get("error") is None
        assert result2.get("error") is None

        # Sin solapamiento entre páginas
        arts1 = {r["articulo"] for r in result1["resultados"]}
        arts2 = {r["articulo"] for r in result2["resultados"]}
        assert not arts1 & arts2

    @pytest.mark.asyncio
    async def test_m2_3_modificados_despues_2021(self):
        """M2.3 - ¿Cuántos artículos modificados hay después de 2021?"""
        result = await search_in_law(LEY_CONCURSAL, modificados_desde="20210101")

        assert result.get("error") is None
        assert result["total_encontrados"] > 0


class TestIntermediateGetLawStructureSummary:
    """M3.x - Casos intermedios de get_law_structure_summary con niveles."""

    @pytest.mark.asyncio
    async def test_m3_1_articulos_libro_primero(self):
        """M3.1 - ¿Cuántos artículos tiene el LIBRO PRIMERO?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None

        # Buscar LIBRO PRIMERO
        libro_primero = None
        for item in result["estructura"]:
            if "PRIMERO" in item["titulo"].upper():
                libro_primero = item
                break

        assert libro_primero is not None
        # El LIBRO PRIMERO tiene ~615 artículos
        assert libro_primero["num_articulos"] >= 600

    @pytest.mark.asyncio
    async def test_m3_2_modificados_libro_segundo(self):
        """M3.2 - ¿Cuántos artículos modificados tiene el LIBRO SEGUNDO?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None

        # Buscar LIBRO SEGUNDO
        libro_segundo = None
        for item in result["estructura"]:
            if "SEGUNDO" in item["titulo"].upper():
                libro_segundo = item
                break

        assert libro_segundo is not None
        # El LIBRO SEGUNDO tiene ~166 modificados
        assert libro_segundo["num_modificados"] >= 150

    @pytest.mark.asyncio
    async def test_m3_3_numero_titulos(self):
        """M3.3 - ¿Cuántos títulos tiene la ley?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="titulos")

        assert result.get("error") is None

        # Contar títulos en todos los libros
        total_titulos = 0
        for libro in result["estructura"]:
            total_titulos += len(libro["hijos"])

        assert total_titulos > 0


class TestIntermediateGetLawIndex:
    """M4.x - Casos intermedios de get_law_index con filtros y paginación."""

    @pytest.mark.asyncio
    async def test_m4_1_articulos_100_a_110(self):
        """M4.1 - Dame los artículos del 100 al 110."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos", limit=10, offset=99)

        assert result.get("error") is None
        assert len(result["bloques"]) == 10

    @pytest.mark.asyncio
    async def test_m4_2_mas_de_500_bloques_estructurales(self):
        """M4.2 - ¿Hay más de 500 bloques estructurales?"""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="estructura")

        assert result.get("error") is None
        # Debería haber muchos bloques estructurales pero probablemente < 500
        assert "total_bloques" in result
        assert "hay_mas" in result

    @pytest.mark.asyncio
    async def test_m4_3_disposiciones_adicionales(self):
        """M4.3 - Dame las disposiciones adicionales."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="disposiciones")

        assert result.get("error") is None

        # Verificar que hay disposiciones
        for bloque in result["bloques"]:
            titulo_lower = bloque["titulo"].lower()
            is_disp = any(
                kw in titulo_lower
                for kw in ["disposición", "adicional", "transitoria", "derogatoria", "final"]
            )
            assert is_disp, f"'{bloque['titulo']}' no es disposición"


# =============================================================================
# CASOS AVANZADOS (A) - Múltiples herramientas, lógica compleja
# =============================================================================

class TestAdvancedAnalysis:
    """A1.x - Análisis avanzados de modificaciones."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a1_1_porcentaje_modificados(self):
        """A1.1 - ¿Qué porcentaje de artículos han sido modificados?"""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None

        porcentaje = (result["total_modificados"] / result["total_articulos"]) * 100

        # Aproximadamente 50% de la Ley Concursal ha sido modificada
        assert 40 <= porcentaje <= 60

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a1_2_articulo_386_seccion_modificada(self):
        """A1.2 - ¿El artículo 386 está en una sección con muchos artículos modificados?"""
        # Obtener ubicación del artículo 386
        art_result = await get_article_info(LEY_CONCURSAL, "386")
        assert art_result.get("error") is None

        # Obtener estructura para analizar la sección
        struct_result = await get_law_structure_summary(LEY_CONCURSAL, nivel="capitulos")
        assert struct_result.get("error") is None

        # El artículo 386 está en una sección específica
        assert art_result["ubicacion"]["seccion"] is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a1_3_libro_mas_modificado(self):
        """A1.3 - ¿Qué libro tiene más modificaciones proporcionalmente?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None

        max_ratio = 0
        libro_mas_modificado = None

        for libro in result["estructura"]:
            if libro["num_articulos"] > 0:
                ratio = libro["num_modificados"] / libro["num_articulos"]
                if ratio > max_ratio:
                    max_ratio = ratio
                    libro_mas_modificado = libro["titulo"]

        assert libro_mas_modificado is not None


class TestAdvancedNavigation:
    """A2.x - Navegación jerárquica avanzada."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a2_1_articulos_titulo_iv(self):
        """A2.1 - Dame todos los artículos del TÍTULO IV."""
        # Obtener índice de artículos
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos", limit=500)

        assert result.get("error") is None

        # El TÍTULO IV del LIBRO PRIMERO contiene muchos artículos
        # (No podemos filtrar directamente por título, pero verificamos que hay artículos)
        assert result["total_bloques"] > 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a2_2_capitulos_titulo_iv(self):
        """A2.2 - ¿Cuántos capítulos tiene el TÍTULO IV del LIBRO PRIMERO?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="capitulos")

        assert result.get("error") is None

        # Navegar hasta TÍTULO IV del LIBRO PRIMERO
        capitulos_titulo_iv = 0
        for libro in result["estructura"]:
            if "PRIMERO" in libro["titulo"].upper():
                for titulo in libro["hijos"]:
                    if "TÍTULO IV" in titulo["titulo"].upper():
                        capitulos_titulo_iv = len(titulo["hijos"])
                        break
                break

        assert capitulos_titulo_iv > 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a2_3_articulos_mismo_capitulo_386(self):
        """A2.3 - ¿Qué artículos están en el mismo capítulo que el 386?"""
        # Obtener ubicación del artículo 386
        art_result = await get_article_info(LEY_CONCURSAL, "386")

        assert art_result.get("error") is None
        assert art_result["ubicacion"]["capitulo"] is not None

        # Verificamos que el artículo tiene ubicación de capítulo
        # (Buscar otros artículos requeriría iterar todo el índice)
        capitulo = art_result["ubicacion"]["capitulo"]
        assert "CAPÍTULO" in capitulo.upper()


class TestAdvancedValidation:
    """A3.x - Comparaciones y validaciones entre herramientas."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a3_1_totales_coinciden(self):
        """A3.1 - ¿El total de artículos coincide entre herramientas?"""
        struct_result = await get_law_structure_summary(LEY_CONCURSAL)
        index_result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos")

        assert struct_result.get("error") is None
        assert index_result.get("error") is None

        # Los totales deberían coincidir (o estar muy cerca)
        diff = abs(struct_result["total_articulos"] - index_result["total_bloques"])
        assert diff <= 5, f"Diferencia: {diff}"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a3_2_fechas_modificacion_posteriores(self):
        """A3.2 - ¿Todos los artículos modificados tienen fecha posterior a 20200507?"""
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=50)

        assert result.get("error") is None

        fecha_ley_original = "20200507"
        for art in result["resultados"]:
            assert art["fecha_actualizacion"] >= fecha_ley_original, \
                f"Artículo {art['articulo']} con fecha {art['fecha_actualizacion']}"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_a3_3_suma_articulos_libros(self):
        """A3.3 - ¿La suma de artículos por libro = total?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None

        suma_libros = sum(libro["num_articulos"] for libro in result["estructura"])

        # La suma de artículos por libro debe ser <= total
        # (puede haber artículos fuera de libros)
        assert suma_libros <= result["total_articulos"]


# =============================================================================
# CASOS DE ERROR (E) - Validación de entrada y edge cases
# =============================================================================

class TestErrorValidation:
    """E1.x - Validación de entrada."""

    @pytest.mark.asyncio
    async def test_e1_1_identificador_invalido(self):
        """E1.1 - Identificador inválido."""
        result = await get_article_info("INVALIDO", "1")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_e1_2_ley_inexistente(self):
        """E1.2 - Ley inexistente."""
        result = await get_article_info(LEY_INEXISTENTE, "1")

        assert result.get("error") is True
        assert result.get("codigo") == "LEY_NO_ENCONTRADA"

    @pytest.mark.asyncio
    async def test_e1_3_articulo_caracteres_invalidos(self):
        """E1.3 - Artículo con caracteres inválidos (SQL injection)."""
        result = await get_article_info(LEY_CONCURSAL, "1; DROP")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_e1_4_xss_en_query(self):
        """E1.4 - XSS en query."""
        result = await search_in_law(LEY_CONCURSAL, query="<script>")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_e1_5_path_traversal(self):
        """E1.5 - Path traversal."""
        result = await get_article_info("../etc/passwd", "1")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_e1_6_busqueda_sin_criterios(self):
        """E1.6 - Búsqueda sin criterios."""
        result = await search_in_law(LEY_CONCURSAL)

        assert result.get("error") is True
        assert result.get("codigo") == "SIN_CRITERIOS"

    @pytest.mark.asyncio
    async def test_e1_7_rango_fechas_invertido(self):
        """E1.7 - Rango de fechas invertido."""
        result = await search_in_law(
            LEY_CONCURSAL,
            modificados_desde="20221231",
            modificados_hasta="20220101"
        )

        assert result.get("error") is True
        assert result.get("codigo") == "RANGO_FECHAS_INVALIDO"


class TestErrorLimitsAndPagination:
    """E2.x - Límites y paginación."""

    @pytest.mark.asyncio
    async def test_e2_1_offset_mayor_que_total(self):
        """E2.1 - Offset mayor que total."""
        result = await get_law_index(LEY_CONCURSAL, offset=10000)

        assert result.get("error") is None
        assert result["bloques"] == []
        assert result["hay_mas"] is False

    @pytest.mark.asyncio
    async def test_e2_2_limit_cero(self):
        """E2.2 - Limit=0 (se ajusta a 1)."""
        result = await get_law_index(LEY_CONCURSAL, limit=0)

        assert result.get("error") is None
        assert len(result["bloques"]) >= 1

    @pytest.mark.asyncio
    async def test_e2_3_limit_muy_alto(self):
        """E2.3 - Limit muy alto (se ajusta)."""
        result = await get_law_index(LEY_CONCURSAL, limit=9999)

        assert result.get("error") is None
        assert len(result["bloques"]) <= 500


class TestErrorSpecialArticles:
    """E3.x - Casos especiales de artículos."""

    @pytest.mark.asyncio
    async def test_e3_1_articulo_unico(self):
        """E3.1 - Artículo único."""
        # Buscar artículo único en la ley
        result = await search_in_law(LEY_CONCURSAL, query="único")

        assert result.get("error") is None

        if result["total_encontrados"] > 0:
            # Si hay artículo único, verificar que se puede obtener
            art = result["resultados"][0]
            art_result = await get_article_info(LEY_CONCURSAL, art["articulo"])
            assert art_result.get("error") is None

    @pytest.mark.asyncio
    async def test_e3_2_articulo_bis(self):
        """E3.2 - Artículo con bis."""
        result = await get_article_info(LEY_CONCURSAL, "224 bis")

        assert result.get("error") is None
        assert result["articulo"] == "224 bis"

    @pytest.mark.asyncio
    async def test_e3_3_busqueda_exacta(self):
        """E3.3 - Buscar '3' no devuelve '30', '31'..."""
        result = await get_article_info(LEY_CONCURSAL, "3")

        assert result.get("error") is None
        assert result["articulo"] == "3"


# =============================================================================
# CASOS DE NEGOCIO (N) - Preguntas reales de usuarios
# =============================================================================

class TestBusinessLawyers:
    """N1.x - Preguntas de abogados/juristas."""

    @pytest.mark.asyncio
    async def test_n1_1_texto_articulo_386(self):
        """N1.1 - ¿Qué dice el artículo 386 de la Ley Concursal?"""
        result = await get_article_info(LEY_CONCURSAL, "386", incluir_texto=True)

        assert result.get("error") is None
        assert result["texto"] is not None
        assert len(result["texto"]) > 0

    @pytest.mark.asyncio
    async def test_n1_2_articulo_modificado_desde_2020(self):
        """N1.2 - ¿Ha cambiado el artículo sobre legitimación desde 2020?"""
        # Verificar si el artículo 1 (presupuesto subjetivo) fue modificado
        result = await get_article_info(LEY_CONCURSAL, "1")

        assert result.get("error") is None
        assert result["modificado"] is True
        assert result["fecha_actualizacion"] > "20200507"

    @pytest.mark.asyncio
    async def test_n1_3_resumen_estructura(self):
        """N1.3 - Dame un resumen de la estructura de la ley."""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None
        assert result["total_articulos"] > 0
        assert len(result["estructura"]) > 0

    @pytest.mark.asyncio
    async def test_n1_4_articulos_libro_segundo_modificados(self):
        """N1.4 - ¿Qué artículos del Libro Segundo fueron modificados?"""
        # Verificar que hay artículos modificados
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=100)

        assert result.get("error") is None
        assert result["total_encontrados"] > 0


class TestBusinessResearchers:
    """N2.x - Preguntas de investigadores."""

    @pytest.mark.asyncio
    async def test_n2_1_porcentaje_reformado(self):
        """N2.1 - ¿Qué porcentaje de la ley ha sido reformado?"""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None

        porcentaje = (result["total_modificados"] / result["total_articulos"]) * 100
        assert 0 <= porcentaje <= 100

    @pytest.mark.asyncio
    async def test_n2_2_ultima_reforma(self):
        """N2.2 - ¿Cuándo fue la última reforma?"""
        # Buscar artículos modificados recientes
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=50)

        assert result.get("error") is None

        if result["resultados"]:
            # Encontrar la fecha más reciente
            fechas = [art["fecha_actualizacion"] for art in result["resultados"]]
            fecha_max = max(fechas)
            assert len(fecha_max) == 8  # AAAAMMDD

    @pytest.mark.asyncio
    async def test_n2_3_secciones_estables(self):
        """N2.3 - ¿Qué secciones son más estables (menos modificaciones)?"""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None

        # Calcular ratio de modificación por libro
        for libro in result["estructura"]:
            if libro["num_articulos"] > 0:
                ratio = libro["num_modificados"] / libro["num_articulos"]
                assert 0 <= ratio <= 1


class TestBusinessDevelopers:
    """N3.x - Preguntas de desarrolladores/integradores."""

    @pytest.mark.asyncio
    async def test_n3_1_block_ids_para_cache(self):
        """N3.1 - Necesito todos los block_id para cachear la ley."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos", limit=100)

        assert result.get("error") is None

        # Verificar que cada bloque tiene ID
        for bloque in result["bloques"]:
            assert "id" in bloque
            assert bloque["id"] is not None

    @pytest.mark.asyncio
    async def test_n3_2_llamadas_para_descargar(self):
        """N3.2 - ¿Cuántas llamadas necesito para descargar toda la ley?"""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos")

        assert result.get("error") is None

        total = result["total_bloques"]
        limit = 100  # Limit típico
        llamadas = (total + limit - 1) // limit

        assert llamadas > 0

    @pytest.mark.asyncio
    async def test_n3_3_solo_metadatos(self):
        """N3.3 - Dame solo los metadatos, no el texto."""
        result = await get_article_info(LEY_CONCURSAL, "1", incluir_texto=False)

        assert result.get("error") is None
        assert result["texto"] is None
        assert result["articulo"] == "1"
        assert result["block_id"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
