"""Custom exceptions for gurkerlcli."""


class GurkerlError(Exception):
    """Base exception for all gurkerl errors."""

    pass


class AuthenticationError(GurkerlError):
    """Authentication failed."""

    pass


class NotFoundError(GurkerlError):
    """Resource not found."""

    pass


class RateLimitError(GurkerlError):
    """Rate limit exceeded."""

    pass


class APIError(GurkerlError):
    """Generic API error."""

    pass
