"""
Tests for get_law_structure_summary tool.

Tests cover:
- Structure extraction at different levels
- Article counting per section
- Modified article counting
- Error handling
"""

import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import AsyncMock, patch
from boe_mcp.server import get_law_structure_summary


# Sample XML for mocking - law with books, titles, chapters, and articles
SAMPLE_INDICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<indice>
    <bloques>
        <bloque>
            <id>te</id>
            <titulo>Real Decreto Legislativo 1/2020, de 5 de mayo, por el que se aprueba el texto refundido de la Ley Concursal</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>lp</id>
            <titulo>LIBRO PRIMERO. De la declaración de concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>ti</id>
            <titulo>TÍTULO I. Presupuestos y declaración de concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>ci</id>
            <titulo>CAPÍTULO I. Presupuesto subjetivo</titulo>
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
            <id>ci-2</id>
            <titulo>CAPÍTULO II. Presupuesto objetivo</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a3</id>
            <titulo>Artículo 3. Presupuesto objetivo</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>ti-2</id>
            <titulo>TÍTULO II. Competencia y procedimiento</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a4</id>
            <titulo>Artículo 4. Competencia judicial</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>lp-2</id>
            <titulo>LIBRO SEGUNDO. De la administración concursal</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>ti-3</id>
            <titulo>TÍTULO I. Nombramiento</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a5</id>
            <titulo>Artículo 5. Nombramiento</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a6</id>
            <titulo>Artículo 6. Requisitos</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>ls</id>
            <titulo>LIBRO TERCERO. De la conclusión del concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
        <bloque>
            <id>a7</id>
            <titulo>Artículo 7. Conclusión</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
        </bloque>
    </bloques>
</indice>
"""


class TestGetLawStructureSummaryValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_invalid_identifier(self):
        """Invalid identifier returns VALIDATION_ERROR."""
        result = await get_law_structure_summary("INVALIDO")
        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"


class TestGetLawStructureSummaryLawNotFound:
    """Tests for law not found."""

    @pytest.mark.asyncio
    async def test_law_not_found(self):
        """Law not found returns LEY_NO_ENCONTRADA."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None
            result = await get_law_structure_summary("BOE-A-0000-0000")
            assert result.get("error") is True
            assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestGetLawStructureSummaryBasic:
    """Tests for basic structure extraction."""

    @pytest.mark.asyncio
    async def test_returns_law_title(self):
        """Returns law title from 'te' block."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None
            assert "Ley Concursal" in result["titulo"]

    @pytest.mark.asyncio
    async def test_returns_fecha_publicacion(self):
        """Returns earliest date as fecha_publicacion."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None
            assert result["fecha_publicacion"] == "20200507"

    @pytest.mark.asyncio
    async def test_total_articulos_count(self):
        """Counts total articles correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None
            assert result["total_articulos"] == 7  # a1-a7

    @pytest.mark.asyncio
    async def test_total_modificados_count(self):
        """Counts modified articles correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None
            # Modified: a2, a4, a6 (fecha > 20200507)
            assert result["total_modificados"] == 3


class TestGetLawStructureSummaryLevelBooks:
    """Tests for nivel='libros'."""

    @pytest.mark.asyncio
    async def test_books_only(self):
        """U3.3 - nivel='libros' returns only books."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859", nivel="libros")

            assert result.get("error") is None
            assert len(result["estructura"]) == 3  # LIBRO PRIMERO, SEGUNDO, TERCERO

            # All items should be books
            for item in result["estructura"]:
                assert item["tipo"] == "libro"

            # Books should have empty hijos at this level
            for item in result["estructura"]:
                assert item["hijos"] == []

    @pytest.mark.asyncio
    async def test_books_have_article_counts(self):
        """Books count articles correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859", nivel="libros")

            assert result.get("error") is None

            # Find LIBRO PRIMERO (lp)
            libro1 = next((b for b in result["estructura"] if b["id"] == "lp"), None)
            assert libro1 is not None
            assert libro1["num_articulos"] == 4  # a1, a2, a3, a4


class TestGetLawStructureSummaryLevelTitles:
    """Tests for nivel='titulos'."""

    @pytest.mark.asyncio
    async def test_books_and_titles(self):
        """U3.4 - nivel='titulos' returns books with titles, without chapters."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859", nivel="titulos")

            assert result.get("error") is None

            # Find LIBRO PRIMERO (lp)
            libro1 = next((b for b in result["estructura"] if b["id"] == "lp"), None)
            assert libro1 is not None

            # Should have titles as children
            assert len(libro1["hijos"]) > 0
            for hijo in libro1["hijos"]:
                assert hijo["tipo"] == "titulo"
                # Titles should have empty hijos (no chapters at this level)
                assert hijo["hijos"] == []


class TestGetLawStructureSummaryLevelChapters:
    """Tests for nivel='capitulos' (default)."""

    @pytest.mark.asyncio
    async def test_full_hierarchy(self):
        """Default nivel includes chapters."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None

            # Find LIBRO PRIMERO (lp)
            libro1 = next((b for b in result["estructura"] if b["id"] == "lp"), None)
            assert libro1 is not None

            # Find TÍTULO I
            titulo1 = next((t for t in libro1["hijos"] if t["id"] == "ti"), None)
            assert titulo1 is not None

            # Should have chapters as children
            assert len(titulo1["hijos"]) > 0
            for hijo in titulo1["hijos"]:
                assert hijo["tipo"] == "capitulo"


class TestGetLawStructureSummaryArticleCounts:
    """Tests for article counting per section."""

    @pytest.mark.asyncio
    async def test_chapter_article_count(self):
        """U3.5 - Chapters count their articles."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None

            # Find CAPÍTULO I (ci) - should have a1, a2
            libro1 = next((b for b in result["estructura"] if b["id"] == "lp"), None)
            titulo1 = next((t for t in libro1["hijos"] if t["id"] == "ti"), None)
            capitulo1 = next((c for c in titulo1["hijos"] if c["id"] == "ci"), None)

            assert capitulo1 is not None
            assert capitulo1["num_articulos"] == 2  # a1, a2

    @pytest.mark.asyncio
    async def test_chapter_modified_count(self):
        """U3.6 - Chapters count modified articles."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859")

            assert result.get("error") is None

            # Find CAPÍTULO I (ci) - a2 is modified
            libro1 = next((b for b in result["estructura"] if b["id"] == "lp"), None)
            titulo1 = next((t for t in libro1["hijos"] if t["id"] == "ti"), None)
            capitulo1 = next((c for c in titulo1["hijos"] if c["id"] == "ci"), None)

            assert capitulo1 is not None
            assert capitulo1["num_modificados"] == 1  # Only a2


class TestGetLawStructureSummaryBooks:
    """Tests for book identification."""

    @pytest.mark.asyncio
    async def test_libro_segundo_identified(self):
        """LIBRO SEGUNDO (lp-2) identified correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859", nivel="libros")

            assert result.get("error") is None

            # Find LIBRO SEGUNDO (lp-2)
            libro2 = next((b for b in result["estructura"] if b["id"] == "lp-2"), None)
            assert libro2 is not None
            assert "SEGUNDO" in libro2["titulo"]

    @pytest.mark.asyncio
    async def test_libro_tercero_identified(self):
        """LIBRO TERCERO (ls) identified correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_law_structure_summary("BOE-A-2020-4859", nivel="libros")

            assert result.get("error") is None

            # Find LIBRO TERCERO (ls)
            libro3 = next((b for b in result["estructura"] if b["id"] == "ls"), None)
            assert libro3 is not None
            assert "TERCERO" in libro3["titulo"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
