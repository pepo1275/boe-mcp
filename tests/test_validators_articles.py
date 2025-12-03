"""
Tests for article number validator.

Tests cover:
- Valid article numbers are accepted
- Invalid inputs are rejected
- Security attack patterns are blocked
- Latin suffixes (bis, ter, etc.) are handled correctly
"""

import pytest
import sys
sys.path.insert(0, 'src')

from boe_mcp.validators import ValidationError, validate_articulo


class TestValidateArticulo:
    """Tests for validate_articulo."""

    # V1.1 - Simple number
    def test_simple_number(self):
        """Simple article number."""
        assert validate_articulo("1") == "1"

    # V1.2 - High number
    def test_high_number(self):
        """High article number."""
        assert validate_articulo("386") == "386"

    # V1.3 - With bis suffix
    def test_bis_suffix(self):
        """Article with bis suffix."""
        assert validate_articulo("224 bis") == "224 bis"

    # V1.4 - With quater suffix
    def test_quater_suffix(self):
        """Article with quater suffix."""
        assert validate_articulo("37 quater") == "37 quater"

    # V1.5 - Único
    def test_unico(self):
        """Artículo único."""
        assert validate_articulo("único") == "único"

    # V1.6 - Whitespace stripped
    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        assert validate_articulo("  386  ") == "386"

    # V1.7 - Uppercase normalized
    def test_uppercase_normalized(self):
        """Uppercase is normalized to lowercase."""
        assert validate_articulo("ÚNICO") == "único"
        assert validate_articulo("224 BIS") == "224 bis"

    # V1.8 - Empty raises
    def test_empty_raises(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match="required"):
            validate_articulo("")

    # V1.9 - None raises
    def test_none_raises(self):
        """None raises ValidationError."""
        with pytest.raises(ValidationError, match="required"):
            validate_articulo(None)

    # V1.10 - Invalid text
    def test_invalid_text(self):
        """Invalid text raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid article number"):
            validate_articulo("abc")

    # V1.11 - Negative number
    def test_negative_number(self):
        """Negative number raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid article number"):
            validate_articulo("-1")

    # V1.12 - SQL injection blocked
    def test_sql_injection(self):
        """SQL injection is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("1; DROP TABLE")

    # V1.13 - Path traversal blocked
    def test_path_traversal(self):
        """Path traversal is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("../../../etc")

    # Additional tests for all Latin suffixes
    def test_ter_suffix(self):
        """Article with ter suffix."""
        assert validate_articulo("37 ter") == "37 ter"

    def test_quinquies_suffix(self):
        """Article with quinquies suffix."""
        assert validate_articulo("37 quinquies") == "37 quinquies"

    def test_sexies_suffix(self):
        """Article with sexies suffix."""
        assert validate_articulo("37 sexies") == "37 sexies"

    def test_septies_suffix(self):
        """Article with septies suffix."""
        assert validate_articulo("37 septies") == "37 septies"

    def test_octies_suffix(self):
        """Article with octies suffix."""
        assert validate_articulo("100 octies") == "100 octies"

    def test_nonies_suffix(self):
        """Article with nonies suffix."""
        assert validate_articulo("100 nonies") == "100 nonies"

    def test_decies_suffix(self):
        """Article with decies suffix."""
        assert validate_articulo("100 decies") == "100 decies"

    # Security tests
    def test_null_byte_blocked(self):
        """Null byte injection is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("1\x00")

    def test_backslash_blocked(self):
        """Backslash is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("1\\2")

    def test_quotes_blocked(self):
        """Quotes are blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("1'")
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo('1"')

    def test_sql_comment_blocked(self):
        """SQL comment is blocked."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_articulo("1--")

    # Edge cases
    def test_max_digits(self):
        """Maximum 4 digits allowed."""
        assert validate_articulo("9999") == "9999"

    def test_too_many_digits(self):
        """More than 4 digits rejected."""
        with pytest.raises(ValidationError, match="Invalid article number"):
            validate_articulo("10000")

    def test_multiple_spaces_normalized(self):
        """Multiple spaces between number and suffix normalized."""
        assert validate_articulo("224   bis") == "224 bis"

    def test_invalid_suffix(self):
        """Invalid suffix rejected."""
        with pytest.raises(ValidationError, match="Invalid article number"):
            validate_articulo("224 invalid")

    def test_suffix_without_number(self):
        """Suffix without number rejected."""
        with pytest.raises(ValidationError, match="Invalid article number"):
            validate_articulo("bis")

    def test_zero_article(self):
        """Article 0 is valid (some laws have it)."""
        assert validate_articulo("0") == "0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
