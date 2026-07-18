class AuthError(Exception):
    """Base exception class for all authentication and authorization errors."""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ConfigurationError(AuthError):
    """Exception raised when Clerk configuration is invalid or missing."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class TokenExpiredError(AuthError):
    """Exception raised when the provided JWT token has expired."""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, status_code=401)


class InvalidTokenError(AuthError):
    """Exception raised when the provided JWT token is invalid."""
    def __init__(self, message: str = "Invalid authentication token"):
        super().__init__(message, status_code=401)


class MissingTokenError(AuthError):
    """Exception raised when the authentication token is missing from the request."""
    def __init__(self, message: str = "Authentication token is missing"):
        super().__init__(message, status_code=401)
