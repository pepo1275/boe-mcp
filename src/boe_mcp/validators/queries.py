"""
Validators for query and code inputs.

Security considerations:
- Protection against query injection patterns
- Control character filtering
- Length limits to prevent DoS
- Numeric code validation
"""

import re
from .base import ValidationError


# Maximum query length (prevent DoS via extremely long queries)
MAX_QUERY_LENGTH = 500

# Suspicious patterns that may indicate injection attempts
# Note: We use a conservative approach to avoid false positives
INJECTION_PATTERNS = [
    re.compile(r'\)\s*(OR|AND)\s*\(', re.IGNORECASE),  # SQL-like injection
    re.compile(r'[\x00-\x1f]'),                         # Control characters
    re.compile(r'\*{3,}'),                              # Excessive wildcards
    re.compile(r'<[^>]*script', re.IGNORECASE),        # XSS script tags
    re.compile(r'javascript:', re.IGNORECASE),          # javascript: URLs
    re.compile(r'on\w+\s*=', re.IGNORECASE),           # Event handlers (onclick=, onerror=)
]


def validate_query_value(query: str | None) -> str | None:
    """
    Validate search query value.

    Security: Filters out potential injection patterns while allowing
    legitimate legal search terms.

    Args:
        query: Search query string

    Returns:
        Validated query string (stripped) or None if empty

    Raises:
        ValidationError: If query contains suspicious patterns or is too long

    Examples:
        >>> validate_query_value("Ley 40/2015")
        'Ley 40/2015'
        >>> validate_query_value("protección de datos")
        'protección de datos'
    """
    if not query:
        return None

    # Normalize: strip whitespace
    query = query.strip()

    if not query:
        return None

    # Length check
    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query too long: {len(query)} characters. "
            f"Maximum: {MAX_QUERY_LENGTH}"
        )

    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if pattern.search(query):
            raise ValidationError(
                "Query contains invalid patterns"
            )

    return query


def validate_codigo(codigo: str | None) -> str | None:
    """
    Validate numeric code (departamento, rango, materia, etc.).

    Args:
        codigo: Numeric code string

    Returns:
        Validated code string or None if empty

    Raises:
        ValidationError: If code contains non-numeric characters

    Examples:
        >>> validate_codigo("1300")
        '1300'
        >>> validate_codigo("5140")
        '5140'
    """
    if not codigo:
        return None

    # Normalize: strip whitespace
    codigo = codigo.strip()

    if not codigo:
        return None

    # Must be numeric only
    if not codigo.isdigit():
        raise ValidationError(
            f"Code must be numeric: '{codigo}'"
        )

    return codigo
