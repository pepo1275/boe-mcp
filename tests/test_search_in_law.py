"""
Tests for search_in_law tool.

Tests cover:
- Filtering by modification status
- Filtering by article list
- Filtering by text query
- Filtering by date range
- Pagination
- Error handling
"""

import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import AsyncMock, patch
from boe_mcp.server import search_in_law


# Sample XML for mocking - articles with different modification dates
SAMPLE_INDICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<indice>
    <bloques>
        <bloque>
            <id>lp</id>
            <titulo>LIBRO PRIMERO. De la declaración de concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a1</id>
            <titulo>Artículo 1. Presupuesto subjetivo</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a2</id>
            <titulo>Artículo 2. Competencia internacional</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a3</id>
            <titulo>Artículo 3. Legitimación para solicitar el concurso</titulo>
            <fecha_actualizacion>20210315</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a3-72</id>
            <titulo>Artículo 224 bis. Acciones de reintegración</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a3-98</id>
            <titulo>Artículo 386. Legitimación activa</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a4</id>
            <titulo>Artículo 4. Solicitud por el deudor</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a5</id>
            <titulo>Artículo 5. Deber de solicitar el concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
    </bloques>
</indice>
"""


class TestSearchInLawValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_invalid_identifier(self):
        """Invalid identifier returns VALIDATION_ERROR."""
        result = await search_in_law("INVALIDO", solo_modificados=True)
        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_no_criteria_error(self):
        """U2.9 - No criteria returns SIN_CRITERIOS error."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859")
            assert result.get("error") is True
            assert result.get("codigo") == "SIN_CRITERIOS"

    @pytest.mark.asyncio
    async def test_invalid_date_range(self):
        """U2.10 - desde > hasta returns RANGO_FECHAS_INVALIDO."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law(
                "BOE-A-2020-4859",
                modificados_desde="20221231",
                modificados_hasta="20220101"
            )
            assert result.get("error") is True
            assert result.get("codigo") == "RANGO_FECHAS_INVALIDO"


class TestSearchInLawByModification:
    """Tests for filtering by modification status."""

    @pytest.mark.asyncio
    async def test_only_modified_articles(self):
        """U2.1 - solo_modificados=True returns only modified articles."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", solo_modificados=True)

            assert result.get("error") is None
            assert result["total_encontrados"] > 0

            # All returned articles should be modified
            for art in result["resultados"]:
                assert art["modificado"] is True

    @pytest.mark.asyncio
    async def test_modified_count(self):
        """Modified articles are: 2, 3, 224 bis, 386 (4 total)."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", solo_modificados=True)

            assert result.get("error") is None
            assert result["total_encontrados"] == 4


class TestSearchInLawByArticleList:
    """Tests for filtering by specific article numbers."""

    @pytest.mark.asyncio
    async def test_specific_articles(self):
        """U2.2 - articulos=["1","2"] returns exactly those articles."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", articulos=["1", "2"])

            assert result.get("error") is None
            assert result["total_encontrados"] == 2

            articulos_encontrados = [r["articulo"] for r in result["resultados"]]
            assert "1" in articulos_encontrados
            assert "2" in articulos_encontrados

    @pytest.mark.asyncio
    async def test_article_with_suffix(self):
        """Article with bis suffix found correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", articulos=["224 bis"])

            assert result.get("error") is None
            assert result["total_encontrados"] == 1
            assert result["resultados"][0]["articulo"] == "224 bis"


class TestSearchInLawByQuery:
    """Tests for filtering by text query."""

    @pytest.mark.asyncio
    async def test_query_legitimacion(self):
        """U2.3 - query="legitimación" finds matching articles."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", query="legitimación")

            assert result.get("error") is None
            assert result["total_encontrados"] == 2  # Art 3 and Art 386

            # All results should contain "legitimación"
            for art in result["resultados"]:
                assert "legitimación" in art["titulo"].lower()

    @pytest.mark.asyncio
    async def test_query_case_insensitive(self):
        """Query is case-insensitive."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", query="LEGITIMACIÓN")

            assert result.get("error") is None
            assert result["total_encontrados"] == 2


class TestSearchInLawByDateRange:
    """Tests for filtering by date range."""

    @pytest.mark.asyncio
    async def test_modified_desde(self):
        """U2.4 - modificados_desde filters correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", modificados_desde="20220101")

            assert result.get("error") is None

            # All results should have fecha >= 20220101
            for art in result["resultados"]:
                assert art["fecha_actualizacion"] >= "20220101"

    @pytest.mark.asyncio
    async def test_modified_hasta(self):
        """U2.5 - modificados_hasta filters correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law("BOE-A-2020-4859", modificados_desde="20200101", modificados_hasta="20210101")

            assert result.get("error") is None

            # All results should have fecha <= 20210101
            for art in result["resultados"]:
                assert art["fecha_actualizacion"] <= "20210101"


class TestSearchInLawCombinedFilters:
    """Tests for combined filters."""

    @pytest.mark.asyncio
    async def test_modified_and_query(self):
        """U2.6 - Combined filters work together."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law(
                "BOE-A-2020-4859",
                solo_modificados=True,
                query="legitimación"
            )

            assert result.get("error") is None

            # All results should be modified AND contain "legitimación"
            for art in result["resultados"]:
                assert art["modificado"] is True
                assert "legitimación" in art["titulo"].lower()


class TestSearchInLawPagination:
    """Tests for pagination."""

    @pytest.mark.asyncio
    async def test_pagination_limit(self):
        """Limit restricts number of results."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law(
                "BOE-A-2020-4859",
                solo_modificados=True,
                limit=2
            )

            assert result.get("error") is None
            assert len(result["resultados"]) == 2
            assert result["total_encontrados"] == 4
            assert result["hay_mas"] is True

    @pytest.mark.asyncio
    async def test_pagination_offset(self):
        """U2.7 - Offset skips results correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML

            # Get first page
            result1 = await search_in_law(
                "BOE-A-2020-4859",
                solo_modificados=True,
                limit=2,
                offset=0
            )

            # Get second page
            result2 = await search_in_law(
                "BOE-A-2020-4859",
                solo_modificados=True,
                limit=2,
                offset=2
            )

            assert result1.get("error") is None
            assert result2.get("error") is None

            # Results should be different
            arts1 = [r["articulo"] for r in result1["resultados"]]
            arts2 = [r["articulo"] for r in result2["resultados"]]

            # No overlap between pages
            assert not set(arts1) & set(arts2)

    @pytest.mark.asyncio
    async def test_hay_mas_false(self):
        """U2.8 - hay_mas is False when all results fit."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law(
                "BOE-A-2020-4859",
                solo_modificados=True,
                limit=100  # More than total modified
            )

            assert result.get("error") is None
            assert result["hay_mas"] is False


class TestSearchInLawLawNotFound:
    """Tests for law not found."""

    @pytest.mark.asyncio
    async def test_law_not_found(self):
        """Law not found returns LEY_NO_ENCONTRADA."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None
            result = await search_in_law("BOE-A-0000-0000", solo_modificados=True)

            assert result.get("error") is True
            assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestSearchInLawCriteria:
    """Tests for criteria reporting."""

    @pytest.mark.asyncio
    async def test_criteria_in_response(self):
        """Response includes the criteria used."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await search_in_law(
                "BOE-A-2020-4859",
                query="legitimación",
                solo_modificados=True
            )

            assert result.get("error") is None
            assert result["criterios"]["query"] == "legitimación"
            assert result["criterios"]["solo_modificados"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
