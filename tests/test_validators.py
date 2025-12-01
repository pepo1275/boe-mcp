"""
Tests for BOE-MCP input validators.

Tests cover:
- Valid inputs are accepted
- Invalid inputs are rejected
- Security attack patterns are blocked
- Edge cases are handled correctly
"""

import pytest
import sys
sys.path.insert(0, 'src')

from boe_mcp.validators import (
    ValidationError,
    validate_boe_identifier,
    validate_block_id,
    validate_fecha,
    validate_date_range,
    validate_query_value,
    validate_codigo,
)


class TestBoeIdentifier:
    """Tests for validate_boe_identifier."""

    def test_valid_identifier_section_a(self):
        """Valid BOE-A identifier."""
        assert validate_boe_identifier("BOE-A-2015-10566") == "BOE-A-2015-10566"

    def test_valid_identifier_section_b(self):
        """Valid BOE-B identifier."""
        assert validate_boe_identifier("BOE-B-2020-12345") == "BOE-B-2020-12345"

    def test_lowercase_normalized(self):
        """Lowercase input is normalized to uppercase."""
        assert validate_boe_identifier("boe-a-2015-10566") == "BOE-A-2015-10566"

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        assert validate_boe_identifier("  BOE-A-2015-10566  ") == "BOE-A-2015-10566"

    def test_empty_raises(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="required"):
            validate_boe_identifier("")

    def test_none_raises(self):
        """None raises ValidationError."""
        with pytest.raises(ValidationError, match="required"):
            validate_boe_identifier(None)

    def test_missing_section_letter(self):
        """Missing section letter (A/B) raises error."""
        with pytest.raises(ValidationError, match="Invalid BOE identifier"):
            validate_boe_identifier("BOE-2015-10566")

    def test_invalid_section_letter(self):
        """Invalid section letter raises error."""
        with pytest.raises(ValidationError, match="Invalid BOE identifier"):
            validate_boe_identifier("BOE-C-2015-10566")

    def test_path_traversal_attack(self):
        """Path traversal attempt is rejected."""
        with pytest.raises(ValidationError, match="Invalid BOE identifier"):
            validate_boe_identifier("../../../etc/passwd")

    def test_short_number(self):
        """Short number (1 digit) is valid."""
        assert validate_boe_identifier("BOE-A-2015-1") == "BOE-A-2015-1"


class TestBlockId:
    """Tests for validate_block_id."""

    def test_article_simple(self):
        """Simple article ID."""
        assert validate_block_id("a1") == "a1"

    def test_article_large(self):
        """Large article number."""
        assert validate_block_id("a1234") == "a1234"

    def test_disposicion_adicional(self):
        """Additional disposition."""
        assert validate_block_id("da10") == "da10"

    def test_disposicion_transitoria(self):
        """Transitory disposition."""
        assert validate_block_id("dt1") == "dt1"

    def test_disposicion_derogatoria(self):
        """Derogatory disposition (without number)."""
        assert validate_block_id("dd") == "dd"

    def test_disposicion_derogatoria_numbered(self):
        """Derogatory disposition (with number)."""
        assert validate_block_id("dd1") == "dd1"

    def test_disposicion_final(self):
        """Final disposition."""
        assert validate_block_id("df") == "df"
        assert validate_block_id("df1") == "df1"
        assert validate_block_id("df10") == "df10"

    def test_preambulo(self):
        """Preamble."""
        assert validate_block_id("pr") == "pr"

    def test_firma(self):
        """Signature."""
        assert validate_block_id("fi") == "fi"

    def test_anexo(self):
        """Annex."""
        assert validate_block_id("an") == "an"
        assert validate_block_id("an1") == "an1"

    def test_uppercase_normalized(self):
        """Uppercase is normalized to lowercase."""
        assert validate_block_id("A1") == "a1"
        assert validate_block_id("DA10") == "da10"

    def test_whitespace_stripped(self):
        """Whitespace is stripped."""
        assert validate_block_id("  a1  ") == "a1"

    def test_empty_raises(self):
        """Empty string raises error."""
        with pytest.raises(ValidationError, match="required"):
            validate_block_id("")

    def test_path_traversal_dotdot(self):
        """Path traversal with .. is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_block_id("../../../etc")

    def test_path_traversal_slash(self):
        """Path traversal with / is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_block_id("a1/../../etc")

    def test_path_traversal_backslash(self):
        """Path traversal with \\ is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_block_id("a1\\..\\etc")

    def test_null_byte(self):
        """Null byte injection is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_block_id("a1\x00")

    def test_invalid_format(self):
        """Invalid format raises error."""
        with pytest.raises(ValidationError, match="Invalid block_id"):
            validate_block_id("articulo1")

    def test_invalid_format_xyz(self):
        """Unknown format raises error."""
        with pytest.raises(ValidationError, match="Invalid block_id"):
            validate_block_id("xyz")


class TestFecha:
    """Tests for validate_fecha."""

    def test_valid_date(self):
        """Valid date."""
        assert validate_fecha("20241125") == "20241125"

    def test_first_day_of_year(self):
        """First day of year."""
        assert validate_fecha("20240101") == "20240101"

    def test_last_day_of_year(self):
        """Last day of year."""
        assert validate_fecha("20241231") == "20241231"

    def test_min_year(self):
        """Minimum valid year (1978 - Spanish Constitution)."""
        assert validate_fecha("19780606") == "19780606"

    def test_whitespace_stripped(self):
        """Whitespace is stripped."""
        assert validate_fecha("  20241125  ") == "20241125"

    def test_empty_raises(self):
        """Empty string raises error."""
        with pytest.raises(ValidationError, match="required"):
            validate_fecha("")

    def test_wrong_format_dashes(self):
        """Wrong format with dashes raises error."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_fecha("2024-11-25")

    def test_wrong_format_slashes(self):
        """Wrong format with slashes raises error."""
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_fecha("25/11/2024")

    def test_invalid_month(self):
        """Invalid month (13) raises error."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_fecha("20241325")

    def test_invalid_day(self):
        """Invalid day (Feb 30) raises error."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_fecha("20240230")

    def test_year_too_old(self):
        """Year before 1978 raises error."""
        with pytest.raises(ValidationError, match="out of range"):
            validate_fecha("19770101")

    def test_year_too_future(self):
        """Year after 2100 raises error."""
        with pytest.raises(ValidationError, match="out of range"):
            validate_fecha("21010101")


class TestDateRange:
    """Tests for validate_date_range."""

    def test_valid_range(self):
        """Valid date range."""
        result = validate_date_range("20240101", "20241231")
        assert result == ("20240101", "20241231")

    def test_same_date(self):
        """Same date for both is valid."""
        result = validate_date_range("20241125", "20241125")
        assert result == ("20241125", "20241125")

    def test_only_from(self):
        """Only from_date provided."""
        result = validate_date_range("20240101", None)
        assert result == ("20240101", None)

    def test_only_to(self):
        """Only to_date provided."""
        result = validate_date_range(None, "20241231")
        assert result == (None, "20241231")

    def test_both_none(self):
        """Both None is valid."""
        result = validate_date_range(None, None)
        assert result == (None, None)

    def test_invalid_range(self):
        """from_date > to_date raises error."""
        with pytest.raises(ValidationError, match="Invalid date range"):
            validate_date_range("20241231", "20240101")


class TestQueryValue:
    """Tests for validate_query_value."""

    def test_valid_query(self):
        """Valid search query."""
        assert validate_query_value("Ley 40/2015") == "Ley 40/2015"

    def test_query_with_accents(self):
        """Query with Spanish accents."""
        assert validate_query_value("protección de datos") == "protección de datos"

    def test_query_with_numbers(self):
        """Query with numbers."""
        assert validate_query_value("artículo 22.1.a)") == "artículo 22.1.a)"

    def test_whitespace_stripped(self):
        """Whitespace is stripped."""
        assert validate_query_value("  Ley 40/2015  ") == "Ley 40/2015"

    def test_empty_returns_none(self):
        """Empty string returns None."""
        assert validate_query_value("") is None

    def test_none_returns_none(self):
        """None returns None."""
        assert validate_query_value(None) is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only returns None."""
        assert validate_query_value("   ") is None

    def test_injection_or(self):
        """SQL-like OR injection is blocked."""
        with pytest.raises(ValidationError, match="invalid patterns"):
            validate_query_value('") OR ("1"="1')

    def test_injection_and(self):
        """SQL-like AND injection is blocked."""
        with pytest.raises(ValidationError, match="invalid patterns"):
            validate_query_value(') AND (1=1')

    def test_control_characters(self):
        """Control characters are blocked."""
        with pytest.raises(ValidationError, match="invalid patterns"):
            validate_query_value("test\x00value")

    def test_excessive_wildcards(self):
        """Excessive wildcards are blocked."""
        with pytest.raises(ValidationError, match="invalid patterns"):
            validate_query_value("test***value")

    def test_too_long(self):
        """Query over 500 chars raises error."""
        long_query = "a" * 501
        with pytest.raises(ValidationError, match="too long"):
            validate_query_value(long_query)

    def test_max_length_ok(self):
        """Query at exactly 500 chars is valid."""
        query = "a" * 500
        assert validate_query_value(query) == query


class TestCodigo:
    """Tests for validate_codigo."""

    def test_valid_codigo(self):
        """Valid numeric code."""
        assert validate_codigo("1300") == "1300"

    def test_valid_codigo_5digits(self):
        """5-digit code."""
        assert validate_codigo("51400") == "51400"

    def test_whitespace_stripped(self):
        """Whitespace is stripped."""
        assert validate_codigo("  1300  ") == "1300"

    def test_empty_returns_none(self):
        """Empty string returns None."""
        assert validate_codigo("") is None

    def test_none_returns_none(self):
        """None returns None."""
        assert validate_codigo(None) is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only returns None."""
        assert validate_codigo("   ") is None

    def test_non_numeric(self):
        """Non-numeric raises error."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_codigo("13a0")

    def test_injection_attempt(self):
        """SQL injection attempt is blocked."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_codigo("13;DROP TABLE")

    def test_negative(self):
        """Negative number raises error."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_codigo("-1300")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
