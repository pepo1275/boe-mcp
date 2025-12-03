"""
Validators for article identifiers.

Security considerations:
- Whitelist approach for article number patterns
- Protection against injection attacks
- Strict regex patterns for article numbers with Latin suffixes
"""

import re
from .base import ValidationError


# Valid Latin ordinal suffixes used in Spanish legal articles
LATIN_SUFFIXES = [
    "bis", "ter", "quater", "quinquies", "sexies",
    "septies", "octies", "nonies", "decies"
]

# Pattern: number (1-4 digits) optionally followed by Latin suffix
# Examples: "1", "386", "224 bis", "37 quater"
# Also accepts "único" for single-article laws
ARTICULO_PATTERN = re.compile(
    r'^(\d{1,4}(\s+(' + '|'.join(LATIN_SUFFIXES) + r'))?|único)$',
    re.IGNORECASE
)


def validate_articulo(articulo: str) -> str:
    """
    Validate article number format.

    Args:
        articulo: Article number string (e.g., "1", "386", "224 bis", "único")

    Returns:
        Normalized article number (stripped, lowercase for suffixes)

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_articulo("1")
        '1'
        >>> validate_articulo("386")
        '386'
        >>> validate_articulo("224 bis")
        '224 bis'
        >>> validate_articulo("ÚNICO")
        'único'
    """
    if not articulo:
        raise ValidationError("Article number is required")

    # Normalize: strip whitespace
    articulo = articulo.strip()

    # Security: Check for null bytes
    if '\x00' in articulo:
        raise ValidationError("Article number contains invalid characters")

    # Security: Check for path traversal attempts
    if '..' in articulo or '/' in articulo or '\\' in articulo:
        raise ValidationError("Article number contains invalid characters")

    # Security: Check for injection patterns
    if ';' in articulo or '--' in articulo or '\'' in articulo or '"' in articulo:
        raise ValidationError("Article number contains invalid characters")

    # Normalize multiple spaces to single space
    articulo = ' '.join(articulo.split())

    # Convert to lowercase for comparison
    articulo_lower = articulo.lower()

    # Validate format
    if not ARTICULO_PATTERN.match(articulo_lower):
        raise ValidationError(
            f"Invalid article number format: '{articulo}'. "
            f"Expected formats: '1', '386', '224 bis', '37 quater', 'único'"
        )

    return articulo_lower
