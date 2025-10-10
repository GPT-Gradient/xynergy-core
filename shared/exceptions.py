"""
Centralized exception hierarchy for Xynergy platform.
Phase 3: Reliability & Monitoring

Provides specific, actionable exceptions for better error handling and debugging.
"""

from typing import Dict, Optional, Any
from datetime import datetime


class XynergyException(Exception):
    """
    Base exception for all Xynergy platform errors.

    All custom exceptions should inherit from this class for consistent handling.

    Attributes:
        message: Human-readable error description
        error_code: Machine-readable error code (defaults to class name)
        details: Additional context about the error
        timestamp: When the error occurred
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "exception_type": self.__class__.__name__
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# ============================================================================
# Service Communication Errors
# ============================================================================

class ServiceCommunicationError(XynergyException):
    """
    Raised when service-to-service communication fails.

    Use this for HTTP errors, network issues, or service unavailability.
    """
    pass


class ServiceTimeoutError(ServiceCommunicationError):
    """
    Raised when a service request times out.

    Indicates the service didn't respond within the expected timeframe.
    """
    def __init__(self, service_name: str, timeout_seconds: float, **kwargs):
        super().__init__(
            message=f"Service '{service_name}' timed out after {timeout_seconds}s",
            details={"service": service_name, "timeout": timeout_seconds, **kwargs}
        )


class ServiceUnavailableError(ServiceCommunicationError):
    """
    Raised when a service is unavailable (503, connection refused, etc.).

    Indicates the service is down or unreachable.
    """
    def __init__(self, service_name: str, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Service '{service_name}' is unavailable{': ' + reason if reason else ''}",
            details={"service": service_name, "reason": reason, **kwargs}
        )


class CircuitBreakerOpenError(ServiceCommunicationError):
    """
    Raised when circuit breaker is open (too many recent failures).

    Indicates the service is being protected from further requests.
    """
    def __init__(self, service_name: str, failures: int, **kwargs):
        super().__init__(
            message=f"Circuit breaker open for '{service_name}' ({failures} failures)",
            details={"service": service_name, "failures": failures, **kwargs}
        )


# ============================================================================
# AI/ML Errors
# ============================================================================

class AIGenerationError(XynergyException):
    """
    Raised when AI content generation fails.

    Base class for all AI-related errors.
    """
    pass


class ModelNotLoadedError(AIGenerationError):
    """
    Raised when attempting to use an AI model that isn't loaded.

    Indicates the model needs to be loaded before use.
    """
    def __init__(self, model_name: str, **kwargs):
        super().__init__(
            message=f"Model '{model_name}' is not loaded",
            details={"model": model_name, **kwargs}
        )


class InvalidPromptError(AIGenerationError):
    """
    Raised when AI prompt validation fails.

    Indicates the prompt contains invalid content or format.
    """
    def __init__(self, reason: str, prompt_preview: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Invalid prompt: {reason}",
            details={"reason": reason, "prompt_preview": prompt_preview, **kwargs}
        )


class AIProviderError(AIGenerationError):
    """
    Raised when external AI provider (OpenAI, Abacus) returns an error.

    Indicates an issue with the external API.
    """
    def __init__(self, provider: str, status_code: Optional[int] = None, provider_message: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"AI provider '{provider}' error{': ' + provider_message if provider_message else ''}",
            details={"provider": provider, "status_code": status_code, "provider_message": provider_message, **kwargs}
        )


class TokenLimitExceededError(AIGenerationError):
    """
    Raised when AI generation exceeds token limits.

    Indicates the request or response is too long.
    """
    def __init__(self, requested: int, limit: int, **kwargs):
        super().__init__(
            message=f"Token limit exceeded: requested {requested}, limit {limit}",
            details={"requested": requested, "limit": limit, **kwargs}
        )


# ============================================================================
# Data Validation Errors
# ============================================================================

class DataValidationError(XynergyException):
    """
    Raised when data validation fails.

    Use this for Pydantic validation errors, schema mismatches, etc.
    """
    def __init__(self, field: Optional[str] = None, reason: Optional[str] = None, **kwargs):
        message = "Data validation failed"
        if field and reason:
            message = f"Validation failed for '{field}': {reason}"
        elif reason:
            message = f"Validation failed: {reason}"

        super().__init__(
            message=message,
            details={"field": field, "reason": reason, **kwargs}
        )


class RequiredFieldMissingError(DataValidationError):
    """Raised when a required field is missing from input data."""
    def __init__(self, field_name: str, **kwargs):
        super().__init__(
            field=field_name,
            reason="required field missing",
            **kwargs
        )


# ============================================================================
# Database Errors
# ============================================================================

class DatabaseError(XynergyException):
    """
    Raised when database operations fail.

    Base class for all database-related errors.
    """
    pass


class FirestoreError(DatabaseError):
    """Raised when Firestore operations fail."""
    def __init__(self, operation: str, collection: Optional[str] = None, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Firestore {operation} failed{': ' + reason if reason else ''}",
            details={"operation": operation, "collection": collection, "reason": reason, **kwargs}
        )


class BigQueryError(DatabaseError):
    """Raised when BigQuery operations fail."""
    def __init__(self, query_type: str, dataset: Optional[str] = None, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"BigQuery {query_type} failed{': ' + reason if reason else ''}",
            details={"query_type": query_type, "dataset": dataset, "reason": reason, **kwargs}
        )


class RecordNotFoundError(DatabaseError):
    """Raised when a database record is not found."""
    def __init__(self, record_type: str, record_id: str, **kwargs):
        super().__init__(
            message=f"{record_type} not found: {record_id}",
            details={"record_type": record_type, "record_id": record_id, **kwargs}
        )


# ============================================================================
# Resource Errors
# ============================================================================

class ResourceExhaustedError(XynergyException):
    """
    Raised when resource limits are exceeded.

    Base class for quota, rate limit, and capacity errors.
    """
    pass


class RateLimitExceededError(ResourceExhaustedError):
    """
    Raised when rate limit is exceeded.

    Indicates the client should back off and retry later.
    """
    def __init__(self, limit_type: str, limit_value: int, current_value: int, retry_after_seconds: Optional[int] = None, **kwargs):
        super().__init__(
            message=f"Rate limit exceeded: {current_value}/{limit_value} {limit_type}",
            details={
                "limit_type": limit_type,
                "limit_value": limit_value,
                "current_value": current_value,
                "retry_after_seconds": retry_after_seconds,
                **kwargs
            }
        )


class QuotaExceededError(ResourceExhaustedError):
    """Raised when GCP quota or service quota is exceeded."""
    def __init__(self, quota_type: str, quota_limit: Optional[int] = None, **kwargs):
        super().__init__(
            message=f"Quota exceeded: {quota_type}",
            details={"quota_type": quota_type, "quota_limit": quota_limit, **kwargs}
        )


class MemoryExhaustedError(ResourceExhaustedError):
    """Raised when service runs out of memory."""
    def __init__(self, current_mb: float, limit_mb: float, **kwargs):
        super().__init__(
            message=f"Memory exhausted: {current_mb:.0f}MB / {limit_mb:.0f}MB",
            details={"current_mb": current_mb, "limit_mb": limit_mb, **kwargs}
        )


# ============================================================================
# Authentication & Authorization Errors
# ============================================================================

class AuthenticationError(XynergyException):
    """
    Raised when authentication fails.

    Indicates invalid or missing credentials.
    """
    def __init__(self, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Authentication failed{': ' + reason if reason else ''}",
            details={"reason": reason, **kwargs}
        )


class InvalidAPIKeyError(AuthenticationError):
    """Raised when API key is invalid or missing."""
    def __init__(self, **kwargs):
        super().__init__(reason="Invalid or missing API key", **kwargs)


class AuthorizationError(XynergyException):
    """
    Raised when authorization fails.

    Indicates the user doesn't have permission for the requested action.
    """
    def __init__(self, action: str, resource: Optional[str] = None, **kwargs):
        message = f"Not authorized to {action}"
        if resource:
            message += f" on {resource}"

        super().__init__(
            message=message,
            details={"action": action, "resource": resource, **kwargs}
        )


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigurationError(XynergyException):
    """
    Raised when service configuration is invalid or missing.

    Indicates a setup or deployment issue.
    """
    def __init__(self, config_key: str, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Configuration error for '{config_key}'{': ' + reason if reason else ''}",
            details={"config_key": config_key, "reason": reason, **kwargs}
        )


class MissingEnvironmentVariableError(ConfigurationError):
    """Raised when required environment variable is not set."""
    def __init__(self, var_name: str, **kwargs):
        super().__init__(
            config_key=var_name,
            reason="environment variable not set",
            **kwargs
        )


# ============================================================================
# Content & Publishing Errors
# ============================================================================

class ContentError(XynergyException):
    """Base class for content-related errors."""
    pass


class ContentValidationError(ContentError):
    """Raised when content fails validation (quality, safety, etc.)."""
    def __init__(self, reason: str, content_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Content validation failed: {reason}",
            details={"reason": reason, "content_type": content_type, **kwargs}
        )


class PlagiarismDetectedError(ContentError):
    """Raised when plagiarism is detected in content."""
    def __init__(self, similarity_percent: float, source: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Plagiarism detected: {similarity_percent:.1f}% similar{' to ' + source if source else ''}",
            details={"similarity_percent": similarity_percent, "source": source, **kwargs}
        )


class PublishingError(ContentError):
    """Raised when content publishing fails."""
    def __init__(self, platform: str, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Failed to publish to {platform}{': ' + reason if reason else ''}",
            details={"platform": platform, "reason": reason, **kwargs}
        )


# ============================================================================
# Workflow & Orchestration Errors
# ============================================================================

class WorkflowError(XynergyException):
    """Base class for workflow orchestration errors."""
    pass


class WorkflowStepFailedError(WorkflowError):
    """Raised when a workflow step fails."""
    def __init__(self, step_name: str, workflow_id: str, reason: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Workflow step '{step_name}' failed in workflow {workflow_id}{': ' + reason if reason else ''}",
            details={"step_name": step_name, "workflow_id": workflow_id, "reason": reason, **kwargs}
        )


class WorkflowTimeoutError(WorkflowError):
    """Raised when a workflow exceeds its timeout."""
    def __init__(self, workflow_id: str, timeout_seconds: float, **kwargs):
        super().__init__(
            message=f"Workflow {workflow_id} timed out after {timeout_seconds}s",
            details={"workflow_id": workflow_id, "timeout_seconds": timeout_seconds, **kwargs}
        )
