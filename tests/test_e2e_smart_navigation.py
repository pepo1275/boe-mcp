"""
E2E Tests for Smart Navigation v2.0 tools against real BOE API.

These tests call the real BOE API to validate that the tools work correctly
with actual data. They are marked with pytest.mark.e2e and can be skipped
in CI/CD pipelines using: pytest -m "not e2e"

Test Law: BOE-A-2020-4859 (Ley Concursal - 752 articles)
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

# Test constants
LEY_CONCURSAL = "BOE-A-2020-4859"
LEY_INEXISTENTE = "BOE-A-0000-0000"


# Mark all tests in this module as e2e (can be skipped with -m "not e2e")
pytestmark = pytest.mark.e2e


class TestGetArticleInfoE2E:
    """E2E tests for get_article_info against real BOE API."""

    @pytest.mark.asyncio
    async def test_article_1_exists(self):
        """E1.1 - Article 1 of Ley Concursal exists and returns correct data."""
        result = await get_article_info(LEY_CONCURSAL, "1")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["identifier"] == LEY_CONCURSAL
        assert result["articulo"] == "1"
        assert result["block_id"].startswith("a")
        assert "Artículo 1" in result["titulo_completo"]
        assert len(result["fecha_actualizacion"]) == 8  # AAAAMMDD
        assert len(result["fecha_ley_original"]) == 8
        assert isinstance(result["modificado"], bool)
        assert isinstance(result["ubicacion"], dict)

    @pytest.mark.asyncio
    async def test_article_386_location(self):
        """E1.2 - Article 386 returns correct hierarchical location."""
        result = await get_article_info(LEY_CONCURSAL, "386")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["articulo"] == "386"

        # Verify hierarchical location exists
        ubicacion = result["ubicacion"]
        assert ubicacion is not None
        # Article 386 should be in a book (LIBRO)
        assert ubicacion.get("libro") is not None or ubicacion.get("titulo") is not None

    @pytest.mark.asyncio
    async def test_article_with_bis_suffix(self):
        """E1.3 - Article with 'bis' suffix found correctly."""
        # Ley Concursal has several "bis" articles
        result = await get_article_info(LEY_CONCURSAL, "224 bis")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["articulo"] == "224 bis"
        assert "224 bis" in result["titulo_completo"].lower()

    @pytest.mark.asyncio
    async def test_article_not_found(self):
        """E1.4 - Non-existent article returns proper error."""
        result = await get_article_info(LEY_CONCURSAL, "9999")

        assert result.get("error") is True
        assert result.get("codigo") == "ARTICULO_NO_ENCONTRADO"
        assert "9999" in result.get("mensaje", "")

    @pytest.mark.asyncio
    async def test_law_not_found(self):
        """E1.5 - Non-existent law returns proper error."""
        result = await get_article_info(LEY_INEXISTENTE, "1")

        assert result.get("error") is True
        assert result.get("codigo") == "LEY_NO_ENCONTRADA"

    @pytest.mark.asyncio
    async def test_article_with_text(self):
        """E1.6 - Article with incluir_texto=True returns text content."""
        result = await get_article_info(LEY_CONCURSAL, "1", incluir_texto=True)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["texto"] is not None
        assert len(result["texto"]) > 50  # Text should have substantial content

    @pytest.mark.asyncio
    async def test_article_without_text_default(self):
        """E1.7 - Article without incluir_texto returns texto=None."""
        result = await get_article_info(LEY_CONCURSAL, "1")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["texto"] is None


class TestSearchInLawE2E:
    """E2E tests for search_in_law against real BOE API."""

    @pytest.mark.asyncio
    async def test_search_modified_articles(self):
        """E2.1 - Search for modified articles returns results."""
        result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=10)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["total_encontrados"] > 0
        assert len(result["resultados"]) <= 10

        # All returned articles should be modified
        for art in result["resultados"]:
            assert art["modificado"] is True

    @pytest.mark.asyncio
    async def test_search_specific_articles(self):
        """E2.2 - Search for specific article list."""
        result = await search_in_law(LEY_CONCURSAL, articulos=["1", "2", "386"])

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["total_encontrados"] == 3

        articulos_encontrados = [r["articulo"] for r in result["resultados"]]
        assert "1" in articulos_encontrados
        assert "2" in articulos_encontrados
        assert "386" in articulos_encontrados

    @pytest.mark.asyncio
    async def test_search_by_query(self):
        """E2.3 - Search by text query in titles.

        Note: Real BOE API article titles are just "Artículo N" without descriptions,
        so we search for "único" which matches "Artículo único".
        """
        result = await search_in_law(LEY_CONCURSAL, query="único")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["total_encontrados"] > 0

        # All results should contain "único" in title
        for art in result["resultados"]:
            assert "único" in art["titulo"].lower()

    @pytest.mark.asyncio
    async def test_search_by_date_range(self):
        """E2.4 - Search by modification date range."""
        result = await search_in_law(
            LEY_CONCURSAL,
            modificados_desde="20220101",
            modificados_hasta="20221231"
        )

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"

        # All results should be in date range
        for art in result["resultados"]:
            assert "20220101" <= art["fecha_actualizacion"] <= "20221231"

    @pytest.mark.asyncio
    async def test_search_pagination(self):
        """E2.5 - Pagination works correctly."""
        # Get first page
        result1 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=0)
        # Get second page
        result2 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=5)

        assert result1.get("error") is None
        assert result2.get("error") is None

        # Results should be different
        arts1 = [r["articulo"] for r in result1["resultados"]]
        arts2 = [r["articulo"] for r in result2["resultados"]]

        # No overlap between pages
        assert not set(arts1) & set(arts2)

    @pytest.mark.asyncio
    async def test_search_no_criteria_error(self):
        """E2.6 - Search without criteria returns error."""
        result = await search_in_law(LEY_CONCURSAL)

        assert result.get("error") is True
        assert result.get("codigo") == "SIN_CRITERIOS"


class TestGetLawStructureSummaryE2E:
    """E2E tests for get_law_structure_summary against real BOE API."""

    @pytest.mark.asyncio
    async def test_structure_default(self):
        """E3.1 - Get full structure (default nivel=capitulos)."""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["identifier"] == LEY_CONCURSAL
        assert "Concursal" in result["titulo"] or "concursal" in result["titulo"].lower()
        assert result["total_articulos"] > 700  # Ley Concursal has ~752 articles
        assert result["total_modificados"] >= 0
        assert len(result["estructura"]) > 0

    @pytest.mark.asyncio
    async def test_structure_books_only(self):
        """E3.2 - Get structure at nivel=libros."""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"

        # Should have books
        assert len(result["estructura"]) > 0

        # All items should be books
        for item in result["estructura"]:
            assert item["tipo"] == "libro"
            # At libros level, hijos should be empty
            assert item["hijos"] == []

    @pytest.mark.asyncio
    async def test_structure_titulos(self):
        """E3.3 - Get structure at nivel=titulos."""
        result = await get_law_structure_summary(LEY_CONCURSAL, nivel="titulos")

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"

        # Find a book with titles
        has_book_with_titles = False
        for item in result["estructura"]:
            if item["tipo"] == "libro" and len(item["hijos"]) > 0:
                has_book_with_titles = True
                for hijo in item["hijos"]:
                    assert hijo["tipo"] == "titulo"
                    # At titulos level, grandchildren should be empty
                    assert hijo["hijos"] == []
                break

        assert has_book_with_titles, "Should have at least one book with titles"

    @pytest.mark.asyncio
    async def test_structure_article_counts(self):
        """E3.4 - Article counts are correct per section."""
        result = await get_law_structure_summary(LEY_CONCURSAL)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"

        # Sum of all book article counts should equal total
        total_from_books = sum(item["num_articulos"] for item in result["estructura"] if item["tipo"] == "libro")

        # Allow for articles not in any book
        assert total_from_books <= result["total_articulos"]

    @pytest.mark.asyncio
    async def test_structure_law_not_found(self):
        """E3.5 - Non-existent law returns error."""
        result = await get_law_structure_summary(LEY_INEXISTENTE)

        assert result.get("error") is True
        assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestGetLawIndexE2E:
    """E2E tests for get_law_index against real BOE API."""

    @pytest.mark.asyncio
    async def test_index_all_blocks(self):
        """E4.1 - Get all blocks with pagination."""
        result = await get_law_index(LEY_CONCURSAL, limit=50)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["identifier"] == LEY_CONCURSAL
        assert result["tipo_bloque"] == "todos"
        assert result["total_bloques"] > 750  # Ley Concursal has many blocks
        assert len(result["bloques"]) == 50
        assert result["hay_mas"] is True

    @pytest.mark.asyncio
    async def test_index_articles_only(self):
        """E4.2 - Filter to articles only."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos", limit=100)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["tipo_bloque"] == "articulos"

        # All blocks should be articles
        for bloque in result["bloques"]:
            assert bloque["titulo"].lower().startswith("artículo")

    @pytest.mark.asyncio
    async def test_index_structure_only(self):
        """E4.3 - Filter to structural blocks only."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="estructura", limit=100)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["tipo_bloque"] == "estructura"

        # All blocks should be structural (LIBRO, TÍTULO, CAPÍTULO, Sección)
        for bloque in result["bloques"]:
            titulo_upper = bloque["titulo"].upper()
            is_structural = any(
                keyword in titulo_upper
                for keyword in ["LIBRO", "TÍTULO", "CAPÍTULO", "SECCIÓN"]
            )
            assert is_structural, f"Block '{bloque['titulo']}' is not structural"

    @pytest.mark.asyncio
    async def test_index_dispositions_only(self):
        """E4.4 - Filter to dispositions only."""
        result = await get_law_index(LEY_CONCURSAL, tipo_bloque="disposiciones", limit=100)

        assert result.get("error") is None, f"Error: {result.get('mensaje')}"
        assert result["tipo_bloque"] == "disposiciones"

        # All blocks should be dispositions
        for bloque in result["bloques"]:
            titulo_lower = bloque["titulo"].lower()
            is_disposition = any(
                keyword in titulo_lower
                for keyword in ["disposición", "adicional", "transitoria", "derogatoria", "final"]
            )
            assert is_disposition, f"Block '{bloque['titulo']}' is not a disposition"

    @pytest.mark.asyncio
    async def test_index_pagination_offset(self):
        """E4.5 - Pagination offset works correctly."""
        # Get first page
        result1 = await get_law_index(LEY_CONCURSAL, limit=10, offset=0)
        # Get second page
        result2 = await get_law_index(LEY_CONCURSAL, limit=10, offset=10)

        assert result1.get("error") is None
        assert result2.get("error") is None

        # Results should be different
        ids1 = [b["id"] for b in result1["bloques"]]
        ids2 = [b["id"] for b in result2["bloques"]]

        # No overlap between pages
        assert not set(ids1) & set(ids2)

    @pytest.mark.asyncio
    async def test_index_law_not_found(self):
        """E4.6 - Non-existent law returns error."""
        result = await get_law_index(LEY_INEXISTENTE)

        assert result.get("error") is True
        assert result.get("codigo") == "LEY_NO_ENCONTRADA"


class TestSecurityE2E:
    """E2E Security tests - verify malicious inputs are rejected."""

    @pytest.mark.asyncio
    async def test_path_traversal_identifier(self):
        """S1.1 - Path traversal in identifier blocked."""
        result = await get_article_info("../../../etc/passwd", "1")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_sql_injection_articulo(self):
        """S1.2 - SQL injection in articulo blocked."""
        result = await get_article_info(LEY_CONCURSAL, "1; DROP TABLE")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_null_byte_injection(self):
        """S1.3 - Null byte injection blocked."""
        result = await get_article_info(LEY_CONCURSAL, "1\x00")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_xss_in_query(self):
        """S1.4 - XSS in query blocked."""
        result = await search_in_law(LEY_CONCURSAL, query="<script>alert('xss')</script>")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_command_injection_identifier(self):
        """S1.5 - Command injection in identifier blocked."""
        result = await get_article_info("BOE-A-2020-4859; rm -rf /", "1")

        assert result.get("error") is True
        assert result.get("codigo") == "VALIDATION_ERROR"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
