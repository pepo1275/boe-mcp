"""
Validators for date inputs.

Security considerations:
- Strict format validation (YYYYMMDD)
- Range validation to prevent unreasonable dates
- Real date validation (no Feb 30, etc.)
"""

import re
from datetime import datetime
from .base import ValidationError


# Pattern: exactly 8 digits
FECHA_PATTERN = re.compile(r'^\d{8}$')

# Valid year range for BOE (Spanish Constitution 1978 - reasonable future)
MIN_YEAR = 1978
MAX_YEAR = 2100


def validate_fecha(fecha: str) -> str:
    """
    Validate date format YYYYMMDD.

    Args:
        fecha: Date string in format YYYYMMDD (e.g., "20241125")

    Returns:
        Validated date string (stripped)

    Raises:
        ValidationError: If format is invalid or date doesn't exist

    Examples:
        >>> validate_fecha("20241125")
        '20241125'
        >>> validate_fecha("19780606")
        '19780606'
    """
    if not fecha:
        raise ValidationError("Date is required")

    # Normalize: strip whitespace
    fecha = fecha.strip()

    # Validate format (8 digits)
    if not FECHA_PATTERN.match(fecha):
        raise ValidationError(
            f"Invalid date format: '{fecha}'. "
            f"Expected format: YYYYMMDD (e.g., 20241125)"
        )

    # Validate it's a real date
    try:
        parsed_date = datetime.strptime(fecha, "%Y%m%d")
    except ValueError:
        raise ValidationError(
            f"Invalid date: '{fecha}'. Date does not exist."
        )

    # Validate year range
    year = parsed_date.year
    if year < MIN_YEAR or year > MAX_YEAR:
        raise ValidationError(
            f"Year out of range: {year}. "
            f"Valid range: {MIN_YEAR}-{MAX_YEAR}"
        )

    return fecha


def validate_date_range(
    from_date: str | None,
    to_date: str | None
) -> tuple[str | None, str | None]:
    """
    Validate a date range (from_date <= to_date).

    Args:
        from_date: Start date in format YYYYMMDD (optional)
        to_date: End date in format YYYYMMDD (optional)

    Returns:
        Tuple of validated (from_date, to_date)

    Raises:
        ValidationError: If dates are invalid or from_date > to_date

    Examples:
        >>> validate_date_range("20240101", "20241231")
        ('20240101', '20241231')
        >>> validate_date_range(None, "20241231")
        (None, '20241231')
    """
    # Validate individual dates if provided
    if from_date:
        from_date = validate_fecha(from_date)
    if to_date:
        to_date = validate_fecha(to_date)

    # Validate range if both provided
    if from_date and to_date:
        if from_date > to_date:
            raise ValidationError(
                f"Invalid date range: from_date ({from_date}) > to_date ({to_date})"
            )

    return from_date, to_date
