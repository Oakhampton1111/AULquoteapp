"""Application exceptions."""

class AppError(Exception):
    """Base exception for application errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code

class AuthenticationError(AppError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(AppError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)

class ValidationError(AppError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class BusinessError(AppError):
    """Raised when a business rule is violated."""
    
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, status_code=400)

class RateLimitError(AppError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

class IntegrationError(AppError):
    """Raised when an external service integration fails."""
    
    def __init__(self, message: str = "Integration error"):
        super().__init__(message, status_code=502)
