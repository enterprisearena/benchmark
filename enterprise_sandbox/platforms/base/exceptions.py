"""
Platform Exceptions

This module defines custom exceptions for platform-related operations.
"""


class PlatformError(Exception):
    """Base exception for all platform-related errors."""
    
    def __init__(self, message: str, platform_type: str = None, error_code: str = None):
        """
        Initialize platform error.
        
        Args:
            message: Error message
            platform_type: Type of platform where error occurred
            error_code: Platform-specific error code
        """
        super().__init__(message)
        self.platform_type = platform_type
        self.error_code = error_code


class PlatformConnectionError(PlatformError):
    """Exception raised when platform connection fails."""
    
    def __init__(self, message: str, platform_type: str = None, original_error: Exception = None):
        """
        Initialize connection error.
        
        Args:
            message: Error message
            platform_type: Type of platform where connection failed
            original_error: Original exception that caused the connection failure
        """
        super().__init__(message, platform_type)
        self.original_error = original_error


class AuthenticationError(PlatformError):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str, platform_type: str = None, error_code: str = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            platform_type: Type of platform where authentication failed
            error_code: Platform-specific authentication error code
        """
        super().__init__(message, platform_type, error_code)


class RateLimitError(PlatformError):
    """Exception raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, platform_type: str = None, retry_after: int = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            platform_type: Type of platform where rate limit was exceeded
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message, platform_type)
        self.retry_after = retry_after


class ValidationError(PlatformError):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str, platform_type: str = None, field_name: str = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            platform_type: Type of platform where validation failed
            field_name: Name of the field that failed validation
        """
        super().__init__(message, platform_type)
        self.field_name = field_name


class QueryError(PlatformError):
    """Exception raised when query execution fails."""
    
    def __init__(self, message: str, platform_type: str = None, query: str = None):
        """
        Initialize query error.
        
        Args:
            message: Error message
            platform_type: Type of platform where query failed
            query: The query that failed
        """
        super().__init__(message, platform_type)
        self.query = query


class ActionError(PlatformError):
    """Exception raised when action execution fails."""
    
    def __init__(self, message: str, platform_type: str = None, action_type: str = None):
        """
        Initialize action error.
        
        Args:
            message: Error message
            platform_type: Type of platform where action failed
            action_type: Type of action that failed
        """
        super().__init__(message, platform_type)
        self.action_type = action_type


class SchemaError(PlatformError):
    """Exception raised when schema operations fail."""
    
    def __init__(self, message: str, platform_type: str = None, object_type: str = None):
        """
        Initialize schema error.
        
        Args:
            message: Error message
            platform_type: Type of platform where schema operation failed
            object_type: Type of object involved in the schema operation
        """
        super().__init__(message, platform_type)
        self.object_type = object_type


class ConfigurationError(PlatformError):
    """Exception raised when platform configuration is invalid."""
    
    def __init__(self, message: str, platform_type: str = None, config_key: str = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            platform_type: Type of platform with configuration issues
            config_key: Configuration key that caused the error
        """
        super().__init__(message, platform_type)
        self.config_key = config_key


class TimeoutError(PlatformError):
    """Exception raised when platform operations timeout."""
    
    def __init__(self, message: str, platform_type: str = None, timeout_seconds: int = None):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            platform_type: Type of platform where timeout occurred
            timeout_seconds: Timeout duration in seconds
        """
        super().__init__(message, platform_type)
        self.timeout_seconds = timeout_seconds


class DataError(PlatformError):
    """Exception raised when data processing fails."""
    
    def __init__(self, message: str, platform_type: str = None, data_type: str = None):
        """
        Initialize data error.
        
        Args:
            message: Error message
            platform_type: Type of platform where data processing failed
            data_type: Type of data that caused the error
        """
        super().__init__(message, platform_type)
        self.data_type = data_type
