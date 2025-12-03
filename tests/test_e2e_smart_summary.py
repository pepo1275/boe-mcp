"""
E2E Tests for Smart Summary tools (v1.5.0).

Tests the new BOE summary tools:
- get_boe_summary_metadata
- get_boe_summary_section
- get_boe_document_info

These tests call the real BOE API.
"""

import pytest

from boe_mcp.server import (
    get_boe_summary_metadata,
    get_boe_summary_section,
    get_boe_document_info,
)

# Mark all tests in this module as E2E (require network)
pytestmark = pytest.mark.e2e


# =============================================================================
# Test get_boe_summary_metadata
# =============================================================================


class TestGetBoeSummaryMetadataE2E:
    """E2E tests for get_boe_summary_metadata."""

    @pytest.mark.asyncio
    async def test_metadata_dia_laboral(self):
        """E1.1: Día laboral debe devolver 8 secciones con items."""
        result = await get_boe_summary_metadata("20241202")

        assert "error" not in result
        assert result["fecha"] == "20241202"
        assert result["numero_boe"] != ""
        assert result["total_documentos"] > 0
        assert len(result["secciones"]) == 8

        # Verificar estructura de secciones
        for seccion in result["secciones"]:
            assert "codigo" in seccion
            assert "nombre" in seccion
            assert "num_items" in seccion
            assert isinstance(seccion["num_items"], int)

    @pytest.mark.asyncio
    async def test_metadata_domingo(self):
        """E1.2: Domingo sin publicaciones debe devolver error."""
        result = await get_boe_summary_metadata("20241201")  # Domingo

        assert result.get("error") is True
        assert result["codigo"] == "SUMARIO_NO_DISPONIBLE"
        assert "20241201" in result["mensaje"]

    @pytest.mark.asyncio
    async def test_metadata_fecha_invalida(self):
        """E1.3: Fecha inválida debe devolver error de validación."""
        result = await get_boe_summary_metadata("invalida")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_metadata_fecha_formato_incorrecto(self):
        """E1.4: Fecha con formato incorrecto debe devolver error."""
        result = await get_boe_summary_metadata("2024-12-02")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_metadata_conteo_total_correcto(self):
        """E1.5: El total de documentos debe ser la suma de todas las secciones."""
        result = await get_boe_summary_metadata("20241202")

        assert "error" not in result

        suma_secciones = sum(s["num_items"] for s in result["secciones"])
        assert result["total_documentos"] == suma_secciones


# =============================================================================
# Test get_boe_summary_section
# =============================================================================


class TestGetBoeSummarySectionE2E:
    """E2E tests for get_boe_summary_section."""

    @pytest.mark.asyncio
    async def test_section_con_items(self):
        """E2.1: Sección con items debe devolver documentos."""
        result = await get_boe_summary_section("20241202", "2B")

        assert "error" not in result
        assert result["fecha"] == "20241202"
        assert result["seccion"]["codigo"] == "2B"
        assert result["total_items"] > 0
        assert len(result["documentos"]) > 0

        # Verificar estructura de documentos
        doc = result["documentos"][0]
        assert "identificador" in doc
        assert "titulo" in doc
        assert "departamento" in doc
        assert "url_pdf" in doc

    @pytest.mark.asyncio
    async def test_section_paginacion(self):
        """E2.3: Paginación debe limitar resultados."""
        result = await get_boe_summary_section("20241202", "2B", limit=5, offset=0)

        assert "error" not in result
        assert len(result["documentos"]) <= 5
        assert result["limit"] == 5
        assert result["offset"] == 0

        if result["total_items"] > 5:
            assert result["hay_mas"] is True

    @pytest.mark.asyncio
    async def test_section_pagina_2(self):
        """E2.4: Segunda página debe tener documentos diferentes."""
        result1 = await get_boe_summary_section("20241202", "2B", limit=5, offset=0)
        result2 = await get_boe_summary_section("20241202", "2B", limit=5, offset=5)

        assert "error" not in result1
        assert "error" not in result2

        if result1["total_items"] > 5:
            # Los identificadores deben ser diferentes
            ids1 = {d["identificador"] for d in result1["documentos"]}
            ids2 = {d["identificador"] for d in result2["documentos"]}
            assert ids1.isdisjoint(ids2), "Las páginas deben tener documentos diferentes"

    @pytest.mark.asyncio
    async def test_section_codigo_invalido(self):
        """E2.5: Código de sección inválido debe devolver error."""
        result = await get_boe_summary_section("20241202", "99")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_section_normaliza_minuscula(self):
        """E2.6: Sección en minúscula debe normalizarse."""
        result = await get_boe_summary_section("20241202", "2b")

        assert "error" not in result
        assert result["seccion"]["codigo"] == "2B"

    @pytest.mark.asyncio
    async def test_section_domingo(self):
        """E2.7: Domingo debe devolver error de sumario no disponible."""
        result = await get_boe_summary_section("20241201", "1")

        assert result.get("error") is True
        assert result["codigo"] == "SUMARIO_NO_DISPONIBLE"

    @pytest.mark.asyncio
    async def test_section_limit_maximo(self):
        """E2.8: Limit mayor a 100 debe ajustarse a 100."""
        result = await get_boe_summary_section("20241202", "5A", limit=200)

        assert "error" not in result
        assert result["limit"] == 100


# =============================================================================
# Test get_boe_document_info
# =============================================================================


class TestGetBoeDocumentInfoE2E:
    """E2E tests for get_boe_document_info."""

    @pytest.mark.asyncio
    async def test_documento_con_fecha(self):
        """E3.1: Documento con fecha debe devolver datos completos."""
        # Primero obtenemos un identificador real del sumario
        section_result = await get_boe_summary_section("20241202", "1", limit=1)
        assert "error" not in section_result
        assert len(section_result["documentos"]) > 0

        doc_id = section_result["documentos"][0]["identificador"]

        # Ahora probamos get_boe_document_info CON fecha
        result = await get_boe_document_info(doc_id, "20241202")

        assert "error" not in result
        assert result["identificador"] == doc_id
        assert result["titulo"] != ""
        assert result["url_pdf"] != ""
        assert result["url_html"] != ""
        assert result["departamento"] is not None

    @pytest.mark.asyncio
    async def test_documento_sin_fecha(self):
        """E3.2: Documento sin fecha devuelve URLs básicas y nota."""
        result = await get_boe_document_info("BOE-A-2024-25051")

        assert "error" not in result
        assert result["identificador"] == "BOE-A-2024-25051"
        assert result["titulo"] is None  # Sin fecha no hay título
        assert result["url_html"] is not None
        assert result["url_xml"] is not None
        assert "nota" in result

    @pytest.mark.asyncio
    async def test_documento_id_invalido(self):
        """E3.3: ID inválido debe devolver error de validación."""
        result = await get_boe_document_info("INVALID")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_documento_id_formato_incorrecto(self):
        """E3.4: ID con formato incorrecto debe devolver error."""
        result = await get_boe_document_info("BOE-X-2024-123")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_documento_normaliza_minuscula(self):
        """E3.5: ID en minúscula debe normalizarse."""
        # Primero obtenemos un ID real
        section_result = await get_boe_summary_section("20241202", "1", limit=1)
        assert "error" not in section_result

        doc_id = section_result["documentos"][0]["identificador"]
        doc_id_lower = doc_id.lower()

        # Con fecha para obtener datos completos
        result = await get_boe_document_info(doc_id_lower, "20241202")

        assert "error" not in result
        assert result["identificador"] == doc_id  # Debe estar normalizado

    @pytest.mark.asyncio
    async def test_documento_fecha_incorrecta(self):
        """E3.6: Documento con fecha incorrecta devuelve error."""
        result = await get_boe_document_info("BOE-A-2024-25051", "20241201")  # Domingo

        assert result.get("error") is True
        assert result["codigo"] == "DOCUMENTO_NO_ENCONTRADO"


# =============================================================================
# Test de seguridad
# =============================================================================


class TestSecuritySmartSummaryE2E:
    """Security tests for Smart Summary tools."""

    @pytest.mark.asyncio
    async def test_injection_en_fecha_metadata(self):
        """Injection en fecha debe ser rechazada."""
        result = await get_boe_summary_metadata("20241202; DROP TABLE")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_injection_en_seccion(self):
        """Injection en sección debe ser rechazada."""
        result = await get_boe_summary_section("20241202", "1; DROP TABLE")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_injection_en_identificador(self):
        """Injection en identificador debe ser rechazada."""
        result = await get_boe_document_info("BOE-A-2024-12345; DROP TABLE")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_path_traversal_en_fecha(self):
        """Path traversal en fecha debe ser rechazado."""
        result = await get_boe_summary_metadata("../../../etc/passwd")

        assert result.get("error") is True
        assert result["codigo"] == "VALIDATION_ERROR"


# =============================================================================
# Test de integración de flujo completo
# =============================================================================


class TestFlowIntegrationE2E:
    """Integration tests simulating real user flows."""

    @pytest.mark.asyncio
    async def test_flujo_completo_exploracion_boe(self):
        """
        Simula el flujo completo de exploración del BOE:
        1. Obtener metadata del día
        2. Seleccionar una sección
        3. Obtener detalles de un documento
        """
        # Paso 1: Metadata
        metadata = await get_boe_summary_metadata("20241202")
        assert "error" not in metadata
        assert metadata["total_documentos"] > 0

        # Encontrar una sección con items
        seccion_con_items = None
        for sec in metadata["secciones"]:
            if sec["num_items"] > 0:
                seccion_con_items = sec["codigo"]
                break

        assert seccion_con_items is not None, "Debe haber al menos una sección con items"

        # Paso 2: Obtener documentos de esa sección
        section = await get_boe_summary_section("20241202", seccion_con_items, limit=5)
        assert "error" not in section
        assert len(section["documentos"]) > 0

        # Paso 3: Obtener detalles de un documento (con fecha para info completa)
        doc_id = section["documentos"][0]["identificador"]
        doc_info = await get_boe_document_info(doc_id, "20241202")
        assert "error" not in doc_info
        assert doc_info["identificador"] == doc_id

        # Verificar que tenemos información completa
        assert doc_info["titulo"] != ""
        assert doc_info["url_pdf"] != ""
