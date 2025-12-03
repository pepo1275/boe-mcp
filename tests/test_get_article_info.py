"""
Tests for get_article_info tool.

Tests cover:
- Valid article lookups (unit tests with mocked API)
- Invalid inputs rejected (validation)
- Security attack patterns blocked
- Error handling (law not found, article not found)
"""

import pytest
import sys
sys.path.insert(0, 'src')

from unittest.mock import AsyncMock, patch
from boe_mcp.server import get_article_info


# Sample XML responses for mocking
SAMPLE_INDICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<indice>
    <bloques>
        <bloque>
            <id>lp</id>
            <titulo>LIBRO PRIMERO. De la declaración de concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/lp</url_bloque>
        </bloque>
        <bloque>
            <id>ti</id>
            <titulo>TÍTULO I. Presupuestos y declaración de concurso</titulo>
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
            <id>a3-72</id>
            <titulo>Artículo 224 bis. Acciones de reintegración</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a3-72</url_bloque>
        </bloque>
        <bloque>
            <id>lp-2</id>
            <titulo>LIBRO TERCERO. De la conclusión del concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/lp-2</url_bloque>
        </bloque>
        <bloque>
            <id>ti-2</id>
            <titulo>TÍTULO I. De la conclusión del concurso</titulo>
            <fecha_actualizacion>20200507</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/ti-2</url_bloque>
        </bloque>
        <bloque>
            <id>a3-98</id>
            <titulo>Artículo 386. Legitimación activa</titulo>
            <fecha_actualizacion>20220906</fecha_actualizacion>
            <url_bloque>https://www.boe.es/api/bloque/a3-98</url_bloque>
        </bloque>
    </bloques>
</indice>
"""

SAMPLE_BLOQUE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<bloque>
    <id>a1</id>
    <titulo>Artículo 1. Presupuesto subjetivo</titulo>
    <texto>
        <p>1. La declaración de concurso procederá respecto de cualquier deudor.</p>
        <p>2. El conocimiento de la solicitud de declaración de concurso...</p>
    </texto>
</bloque>
"""


class TestGetArticleInfoValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_invalid_identifier_format(self):
        """U1.5 - Invalid identifier format returns VALIDATION_ERROR."""
        result = await get_article_info("INVALIDO", "1")
        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"
        assert "identifier" in result.get("mensaje", "").lower() or "BOE" in result.get("mensaje", "")

    @pytest.mark.asyncio
    async def test_invalid_articulo_format(self):
        """U1.6 - Invalid article format returns VALIDATION_ERROR."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "abc")
            assert result.get("error") is True
            assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_path_traversal_in_identifier(self):
        """S1.1 - Path traversal in identifier blocked."""
        result = await get_article_info("../../../etc/passwd", "1")
        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_sql_injection_in_articulo(self):
        """S1.2 - SQL injection in articulo blocked."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "1; DROP TABLE")
            assert result.get("error") is True
            assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_null_byte_in_articulo(self):
        """S1.3 - Null byte injection in articulo blocked."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "1\x00")
            assert result.get("error") is True
            assert result.get("codigo") == "VALIDATION_ERROR"


class TestGetArticleInfoLawNotFound:
    """Tests for law not found scenarios."""

    @pytest.mark.asyncio
    async def test_law_not_found(self):
        """U1.5 partial - Law not found returns LEY_NO_ENCONTRADA."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = None
            result = await get_article_info("BOE-A-0000-0000", "1")
            assert result.get("error") is True
            assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestGetArticleInfoArticleNotFound:
    """Tests for article not found scenarios."""

    @pytest.mark.asyncio
    async def test_article_not_found(self):
        """U1.4 - Non-existent article returns ARTICULO_NO_ENCONTRADO."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "9999")
            assert result.get("error") is True
            assert result.get("codigo") == "ARTICULO_NO_ENCONTRADO"
            assert "9999" in result.get("mensaje", "")


class TestGetArticleInfoSuccess:
    """Tests for successful article lookups."""

    @pytest.mark.asyncio
    async def test_article_1_basic_info(self):
        """U1.1 - Article 1 returns correct basic info."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "1")

            assert result.get("error") is None
            assert result["identifier"] == "BOE-A-2020-4859"
            assert result["articulo"] == "1"
            assert result["block_id"] == "a1"
            assert "Artículo 1" in result["titulo_completo"]
            assert result["fecha_actualizacion"] == "20200507"
            assert result["fecha_ley_original"] == "20200507"
            assert result["modificado"] is False  # Same as original date

    @pytest.mark.asyncio
    async def test_article_2_modified(self):
        """Article 2 shows as modified (fecha_actualizacion > fecha_ley_original)."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "2")

            assert result.get("error") is None
            assert result["articulo"] == "2"
            assert result["fecha_actualizacion"] == "20220906"
            assert result["fecha_ley_original"] == "20200507"
            assert result["modificado"] is True

    @pytest.mark.asyncio
    async def test_article_with_bis_suffix(self):
        """U1.3 - Article with 'bis' suffix found correctly."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "224 bis")

            assert result.get("error") is None
            assert result["articulo"] == "224 bis"
            assert result["block_id"] == "a3-72"
            assert "224 bis" in result["titulo_completo"].lower()

    @pytest.mark.asyncio
    async def test_article_386_location(self):
        """U1.2 - Article 386 returns correct hierarchical location."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "386")

            assert result.get("error") is None
            assert result["articulo"] == "386"
            assert result["block_id"] == "a3-98"
            # Check hierarchical location
            ubicacion = result["ubicacion"]
            assert "LIBRO TERCERO" in (ubicacion.get("libro") or "")
            assert "TÍTULO I" in (ubicacion.get("titulo") or "")

    @pytest.mark.asyncio
    async def test_article_1_location_hierarchy(self):
        """Article 1 shows correct location in LIBRO PRIMERO."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "1")

            assert result.get("error") is None
            ubicacion = result["ubicacion"]
            assert "LIBRO PRIMERO" in (ubicacion.get("libro") or "")
            assert "TÍTULO I" in (ubicacion.get("titulo") or "")
            assert "CAPÍTULO I" in (ubicacion.get("capitulo") or "")


class TestGetArticleInfoWithText:
    """Tests for incluir_texto parameter."""

    @pytest.mark.asyncio
    async def test_without_text_default(self):
        """U1.8 - Without incluir_texto, texto is None."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "1")

            assert result.get("error") is None
            assert result["texto"] is None

    @pytest.mark.asyncio
    async def test_with_text_included(self):
        """U1.7 - With incluir_texto=True, texto is populated."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            # First call returns index, second returns block
            mock_request.side_effect = [SAMPLE_INDICE_XML, SAMPLE_BLOQUE_XML]
            result = await get_article_info("BOE-A-2020-4859", "1", incluir_texto=True)

            assert result.get("error") is None
            assert result["texto"] is not None
            assert "declaración de concurso" in result["texto"]


class TestGetArticleInfoCaseNormalization:
    """Tests for case normalization."""

    @pytest.mark.asyncio
    async def test_lowercase_identifier_normalized(self):
        """Lowercase identifier is normalized to uppercase."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("boe-a-2020-4859", "1")

            assert result.get("error") is None
            assert result["identifier"] == "BOE-A-2020-4859"

    @pytest.mark.asyncio
    async def test_uppercase_bis_normalized(self):
        """Uppercase suffix is normalized to lowercase."""
        with patch('boe_mcp.server.make_boe_raw_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = SAMPLE_INDICE_XML
            result = await get_article_info("BOE-A-2020-4859", "224 BIS")

            assert result.get("error") is None
            assert result["articulo"] == "224 bis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
