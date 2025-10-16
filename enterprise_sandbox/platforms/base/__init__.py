"""
Platform Base Module

This module provides the base classes and interfaces for all platform implementations
in EnterpriseArena.
"""

from .platform import BasePlatform, PlatformCredentials, QueryResult, ActionResult, PlatformType, ActionType
from .exceptions import (
    PlatformConnectionError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    PlatformError
)
from .utils import PlatformUtils

__all__ = [
    "BasePlatform",
    "PlatformCredentials", 
    "QueryResult",
    "ActionResult",
    "PlatformType",
    "ActionType",
    "PlatformConnectionError",
    "AuthenticationError",
    "RateLimitError", 
    "ValidationError",
    "PlatformError",
    "PlatformUtils"
]
