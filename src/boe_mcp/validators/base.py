"""
Base validation classes and utilities.
"""


class ValidationError(ValueError):
    """
    Error raised when input validation fails.

    Inherits from ValueError for compatibility with existing error handling.
    """
    pass
