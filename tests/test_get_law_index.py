"""
Tests for get_law_index tool.

Tests cover:
- Pagination
- Filtering by block type
- Error handling
"""

import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import AsyncMock, patch
from boe_mcp.server import get_law_index


# Sample XML for mocking - contains various block types
SAMPLE_INDICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<indice>
    <bloques>
        <bloque>
            <id>te</id>
            <titulo>Texto refundido de la Ley Concursal</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/te</url_bloque>
        </bloque>
        <bloque>
            <id>lp</id>
            <titulo>LIBRO PRIMERO. De la declaración de concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/lp</url_bloque>
        </bloque>
        <bloque>
            <id>ti</id>
            <titulo>TÍTULO I. Presupuestos y declaración</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/ti</url_bloque>
        </bloque>
        <bloque>
            <id>ci</id>
            <titulo>CAPÍTULO I. Presupuesto subjetivo</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/ci</url_bloque>
        </bloque>
        <bloque>
            <id>s1</id>
            <titulo>Sección 1. Generalidades</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/s1</url_bloque>
        </bloque>
        <bloque>
            <id>a1</id>
            <titulo>Artículo 1. Presupuesto subjetivo</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a1</url_bloque>
        </bloque>
        <bloque>
            <id>a2</id>
            <titulo>Artículo 2. Competencia internacional</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a2</url_bloque>
        </bloque>
        <bloque>
            <id>a3</id>
            <titulo>Artículo 3. Legitimación</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a3</url_bloque>
        </bloque>
        <bloque>
            <id>a4</id>
            <titulo>Artículo 4. Solicitud</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a4</url_bloque>
        </bloque>
        <bloque>
            <id>a5</id>
            <titulo>Artículo 5. Deber de solicitar</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a5</url_bloque>
        </bloque>
        <bloque>
            <id>da</id>
            <titulo>Disposición adicional primera</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/da</url_bloque>
        </bloque>
        <bloque>
            <id>da-2</id>
            <titulo>Disposición adicional segunda</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/da-2</url_bloque>
        </bloque>
        <bloque>
            <id>dt</id>
            <titulo>Disposición transitoria única</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/dt</url_bloque>
        </bloque>
        <bloque>
            <id>dd</id>
            <titulo>Disposición derogatoria</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/dd</url_bloque>
        </bloque>
        <bloque>
            <id>df</id>
            <titulo>Disposición final primera</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/df</url_bloque>
        </bloque>
        <bloque>
            <id>fi</id>
            <titulo>Firma</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/fi</url_bloque>
        </bloque>
    </bloques>
</indice>
"""


class TestGetLawIndexValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_invalid_identifier(self):
        """Invalid identifier returns VALIDATION_ERROR."""
        result = await get_law_index("INVALIDO")
        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"


class TestGetLawIndexLawNotFound:
    """Tests for law not found."""

    @pytest.mark.asyncio
    async def test_law_not_found(self):
        """Law not found returns LEY_NO_ENCONTRADA."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None
            result = await get_law_index("BOE-A-0000-0000")
            assert result.get("error") is True
            assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestGetLawIndexPagination:
    """Tests for pagination."""

    @pytest.mark.asyncio
    async def test_pagination_limit(self):
        """U4.1 - Limit restricts number of results."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", limit=5)

            assert result.get("error") is None
            assert len(result["bloques"]) == 5
            assert result["total_bloques"] == 16  # All blocks in sample

    @pytest.mark.asyncio
    async def test_pagination_hay_mas_true(self):
        """U4.2 - hay_mas is True when more results available."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", limit=5)

            assert result.get("error") is None
            assert result["hay_mas"] is True

    @pytest.mark.asyncio
    async def test_pagination_hay_mas_false(self):
        """hay_mas is False when all results returned."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", limit=100)

            assert result.get("error") is None
            assert result["hay_mas"] is False

    @pytest.mark.asyncio
    async def test_pagination_offset(self):
        """R4.5 - Offset skips results correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML

            # Get first page
            result1 = await get_law_index("BOE-A-2020-4859", limit=5, offset=0)

            # Get second page
            result2 = await get_law_index("BOE-A-2020-4859", limit=5, offset=5)

            assert result1.get("error") is None
            assert result2.get("error") is None

            # Results should be different
            ids1 = [b["id"] for b in result1["bloques"]]
            ids2 = [b["id"] for b in result2["bloques"]]

            # No overlap between pages
            assert not set(ids1) & set(ids2)


class TestGetLawIndexFilterArticles:
    """Tests for tipo_bloque='articulos'."""

    @pytest.mark.asyncio
    async def test_only_articles(self):
        """U4.3 - Only articles returned."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", tipo_bloque="articulos")

            assert result.get("error") is None
            assert result["total_bloques"] == 5  # a1, a2, a3, a4, a5

            # All should be articles
            for bloque in result["bloques"]:
                assert bloque["id"].startswith("a")
                assert "Artículo" in bloque["titulo"]


class TestGetLawIndexFilterStructure:
    """Tests for tipo_bloque='estructura'."""

    @pytest.mark.asyncio
    async def test_only_structure(self):
        """U4.4 - Only structural blocks returned."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", tipo_bloque="estructura")

            assert result.get("error") is None
            # Should be: lp, ti, ci, s1
            assert result["total_bloques"] == 4

            # All should be structural
            for bloque in result["bloques"]:
                id_bloque = bloque["id"]
                assert (id_bloque.startswith("lp") or id_bloque.startswith("ls") or
                        id_bloque.startswith("ti") or id_bloque.startswith("ci") or
                        id_bloque.startswith("cv") or id_bloque.startswith("s"))


class TestGetLawIndexFilterDispositions:
    """Tests for tipo_bloque='disposiciones'."""

    @pytest.mark.asyncio
    async def test_only_dispositions(self):
        """R4.4 - Only dispositions returned."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", tipo_bloque="disposiciones")

            assert result.get("error") is None
            # Should be: da, da-2, dt, dd, df
            assert result["total_bloques"] == 5

            # All should be dispositions
            for bloque in result["bloques"]:
                id_bloque = bloque["id"]
                assert (id_bloque.startswith("da") or id_bloque.startswith("dt") or
                        id_bloque.startswith("dd") or id_bloque.startswith("df"))


class TestGetLawIndexFilterAll:
    """Tests for tipo_bloque='todos'."""

    @pytest.mark.asyncio
    async def test_all_blocks(self):
        """Default 'todos' returns all blocks."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859")

            assert result.get("error") is None
            assert result["total_bloques"] == 16  # All blocks


class TestGetLawIndexTotalCorrect:
    """Tests for correct total counting."""

    @pytest.mark.asyncio
    async def test_total_with_filter(self):
        """U4.5 - total_bloques reflects filtered count."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML

            # Get articles
            result = await get_law_index("BOE-A-2020-4859", tipo_bloque="articulos", limit=2)

            assert result.get("error") is None
            # Total should be all articles, not just returned
            assert result["total_bloques"] == 5
            assert len(result["bloques"]) == 2


class TestGetLawIndexBlockData:
    """Tests for block data fields."""

    @pytest.mark.asyncio
    async def test_block_has_all_fields(self):
        """Each block has id, titulo, fecha_actualizacion, url."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_index("BOE-A-2020-4859", limit=1)

            assert result.get("error") is None
            assert len(result["bloques"]) == 1

            bloque = result["bloques"][0]
            assert "id" in bloque
            assert "titulo" in bloque
            assert "fecha_actualizacion" in bloque
            assert "url" in bloque


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
