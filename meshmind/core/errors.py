"""Custom exceptions for MeshMind."""


class MeshMindError(Exception):
    """Base exception for MeshMind errors."""
    pass


class ConfigError(MeshMindError):
    """Configuration loading error."""
    pass


class StorageError(MeshMindError):
    """Error during storage operations."""
    pass


class NotFoundError(MeshMindError):
    """Raised when an entity or memory is not found."""
    pass


class ValidationError(MeshMindError):
    """Raised when validation of input data fails."""
    pass