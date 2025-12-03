"""
Validators for BOE section codes.

Section codes are used to filter BOE daily summaries by section.
"""

from .base import ValidationError


# Valid BOE section codes
# Source: BOE API response structure
SECCIONES_BOE_VALIDAS = {"1", "2A", "2B", "3", "4", "5A", "5B", "5C"}

# Section code descriptions for error messages
SECCIONES_BOE_DESCRIPCION = {
    "1": "Disposiciones generales",
    "2A": "Autoridades y personal - Nombramientos",
    "2B": "Autoridades y personal - Oposiciones y concursos",
    "3": "Otras disposiciones",
    "4": "Administración de Justicia",
    "5A": "Anuncios - Contratación del Sector Público",
    "5B": "Anuncios - Otros anuncios oficiales",
    "5C": "Anuncios - Anuncios particulares",
}


def validate_seccion_boe(seccion: str) -> str:
    """
    Validate BOE section code.

    Args:
        seccion: Section code string (e.g., "1", "2A", "2B", "3", "4", "5A", "5B", "5C")

    Returns:
        Normalized section code (uppercase, stripped)

    Raises:
        ValidationError: If section code is invalid

    Examples:
        >>> validate_seccion_boe("1")
        '1'
        >>> validate_seccion_boe("2a")
        '2A'
        >>> validate_seccion_boe(" 2B ")
        '2B'
    """
    if not seccion:
        raise ValidationError("Section code is required")

    # Normalize: strip whitespace, uppercase
    seccion = seccion.strip().upper()

    if seccion not in SECCIONES_BOE_VALIDAS:
        valid_list = ", ".join(sorted(SECCIONES_BOE_VALIDAS))
        raise ValidationError(
            f"Invalid BOE section code: '{seccion}'. "
            f"Valid codes: {valid_list}"
        )

    return seccion
