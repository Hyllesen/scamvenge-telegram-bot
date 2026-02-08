"""Custom exceptions for the Telegram Store Follow Bot."""


class InvalidImageError(Exception):
    """Raised when an image does not contain the required keywords."""
    pass


class OCRError(Exception):
    """Raised when OCR processing fails."""
    pass


class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass
