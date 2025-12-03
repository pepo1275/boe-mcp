"""
Validators for BOE identifiers and block IDs.

Security considerations:
- Whitelist approach for block_id patterns
- Protection against path traversal attacks
- Strict regex patterns for identifiers
"""

import re
from .base import ValidationError


# Pattern: BOE-A-2015-10566 or BOE-B-2020-12345
# A = Disposiciones generales, B = Anuncios
BOE_IDENTIFIER_PATTERN = re.compile(r'^BOE-[AB]-\d{4}-\d{1,6}$')

# Valid block_id patterns (whitelist approach)
# Updated based on real BOE data analysis (BOE-A-2020-4859 Ley Concursal)
BLOCK_ID_PATTERNS = [
    # Articles: a1, a22, a1-2 (art 10), a3-112 (art 37 bis)
    re.compile(r'^a\d{1,4}(-\d{1,4})?$'),
    # Additional dispositions: da, da-2, da-3
    re.compile(r'^da(-\d{1,2})?$'),
    # Transitory dispositions: dt, dt-2
    re.compile(r'^dt(-\d{1,2})?$'),
    # Derogatory dispositions: dd, dd-2
    re.compile(r'^dd(-\d{1,2})?$'),
    # Final dispositions: df, df-2
    re.compile(r'^df(-\d{1,2})?$'),
    # Preamble
    re.compile(r'^pr$'),
    # Signature
    re.compile(r'^fi$'),
    # Annexes: an, an1, an-2
    re.compile(r'^an\d?(-\d{1,2})?$'),
    # Initial note
    re.compile(r'^no$'),
    # Index
    re.compile(r'^in$'),
    # Exposition
    re.compile(r'^ex$'),
    # Artículo único
    re.compile(r'^au$'),
    # Texto (título de la ley)
    re.compile(r'^te$'),
    # Books: lp (libro primero), ls (libro segundo), lp-2
    re.compile(r'^l[ps](-\d{1,2})?$'),
    # Titles: ti, ti-2, ti-3
    re.compile(r'^ti(-\d{1,2})?$'),
    # Chapters: ci, ci-2, cv, cv-2 (capítulo quinto)
    re.compile(r'^c[iv](-\d{1,2})?$'),
    # Sections and subsections: s1, s2-3, s4-16
    re.compile(r'^s\d{1,2}(-\d{1,2})?$'),
]


def validate_boe_identifier(identifier: str) -> str:
    """
    Validate BOE identifier format.

    Args:
        identifier: BOE identifier string (e.g., "BOE-A-2015-10566")

    Returns:
        Normalized identifier (uppercase, stripped)

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_boe_identifier("BOE-A-2015-10566")
        'BOE-A-2015-10566'
        >>> validate_boe_identifier("boe-a-2015-10566")
        'BOE-A-2015-10566'
    """
    if not identifier:
        raise ValidationError("BOE identifier is required")

    # Normalize: strip whitespace, uppercase
    identifier = identifier.strip().upper()

    # Validate format
    if not BOE_IDENTIFIER_PATTERN.match(identifier):
        raise ValidationError(
            f"Invalid BOE identifier format: '{identifier}'. "
            f"Expected format: BOE-A-YYYY-NNNNN (e.g., BOE-A-2015-10566)"
        )

    return identifier


def validate_block_id(block_id: str) -> str:
    """
    Validate block_id format using whitelist approach.

    Security: Prevents path traversal and injection attacks by only
    allowing known valid patterns.

    Args:
        block_id: Block identifier string (e.g., "a1", "da1", "dd")

    Returns:
        Normalized block_id (lowercase, stripped)

    Raises:
        ValidationError: If format is invalid or contains dangerous characters

    Examples:
        >>> validate_block_id("a1")
        'a1'
        >>> validate_block_id("DA10")
        'da10'
    """
    if not block_id:
        raise ValidationError("block_id is required")

    # Normalize: strip whitespace, lowercase
    block_id = block_id.strip().lower()

    # Security: Check for path traversal attempts
    if '..' in block_id or '/' in block_id or '\\' in block_id:
        raise ValidationError(
            f"block_id contains invalid characters: '{block_id}'"
        )

    # Security: Check for null bytes
    if '\x00' in block_id:
        raise ValidationError(
            f"block_id contains invalid characters"
        )

    # Whitelist validation
    for pattern in BLOCK_ID_PATTERNS:
        if pattern.match(block_id):
            return block_id

    raise ValidationError(
        f"Invalid block_id format: '{block_id}'. "
        f"Valid formats: a1, da1, dt1, dd, df, pr, fi, an, no, in, etc."
    )
