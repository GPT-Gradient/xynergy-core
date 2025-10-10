"""
OpenTelemetry distributed tracing setup for Xynergy platform.
Phase 3: Reliability & Monitoring

Provides end-to-end request tracing across microservices.
"""

import os
import logging
from typing import Optional
from contextlib import contextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    logging.warning("OpenTelemetry not installed. Tracing will be disabled.")

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
TRACING_ENABLED = os.getenv("ENABLE_TRACING", "false").lower() in ("true", "1", "yes")

logger = logging.getLogger(__name__)


def setup_tracing(service_name: str, enable: Optional[bool] = None) -> Optional[trace.Tracer]:
    """
    Initialize OpenTelemetry distributed tracing for a service.

    This function:
    1. Sets up Google Cloud Trace exporter
    2. Configures automatic instrumentation for FastAPI and HTTPX
    3. Returns a tracer for manual span creation

    Args:
        service_name: Name of the service (e.g., "marketing-engine")
        enable: Override ENABLE_TRACING environment variable

    Returns:
        Tracer instance if tracing is enabled, None otherwise

    Usage:
        # In service main.py after creating FastAPI app:
        from shared.tracing import setup_tracing

        app = FastAPI(title="My Service")
        tracer = setup_tracing("my-service")

        # Optional: Manual span creation
        if tracer:
            with tracer.start_as_current_span("expensive_operation"):
                # ... code to trace ...
                pass
    """
    # Check if tracing should be enabled
    should_enable = enable if enable is not None else TRACING_ENABLED

    if not should_enable:
        logger.info(f"[{service_name}] Tracing disabled (set ENABLE_TRACING=true to enable)")
        return None

    if not TRACING_AVAILABLE:
        logger.warning(f"[{service_name}] Tracing requested but OpenTelemetry not installed")
        logger.warning("Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-gcp-trace opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-httpx")
        return None

    try:
        # Create resource with service name
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Configure Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)

        # Add batch span processor (batches spans for efficiency)
        span_processor = BatchSpanProcessor(cloud_trace_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Auto-instrument FastAPI (traces all HTTP requests)
        FastAPIInstrumentor.instrument()

        # Auto-instrument HTTPX (traces service-to-service calls)
        HTTPXClientInstrumentor.instrument()

        logger.info(f"[{service_name}] Distributed tracing enabled (Cloud Trace)")

        # Return tracer for manual span creation
        return trace.get_tracer(service_name)

    except Exception as e:
        logger.error(f"[{service_name}] Failed to initialize tracing: {e}")
        return None


@contextmanager
def trace_operation(operation_name: str, tracer: Optional[trace.Tracer] = None, **attributes):
    """
    Context manager for tracing a specific operation.

    Args:
        operation_name: Name of the operation to trace
        tracer: Tracer instance (optional if setup_tracing was called)
        **attributes: Additional attributes to add to the span

    Usage:
        with trace_operation("database_query", query="SELECT * FROM users"):
            result = execute_query()
    """
    if tracer is None:
        # Try to get current tracer
        tracer = trace.get_tracer(__name__)

    if tracer and TRACING_ENABLED:
        with tracer.start_as_current_span(operation_name) as span:
            # Add custom attributes
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            yield span
    else:
        # Tracing disabled, just yield None
        yield None


def add_trace_attributes(**attributes):
    """
    Add attributes to the current span.

    Useful for adding context to auto-instrumented spans.

    Args:
        **attributes: Key-value pairs to add as span attributes

    Usage:
        from shared.tracing import add_trace_attributes

        @app.post("/generate")
        async def generate_content(request: Request):
            add_trace_attributes(
                user_id=request.user_id,
                content_type="blog_post"
            )
            # ... rest of handler ...
    """
    if not TRACING_ENABLED or not TRACING_AVAILABLE:
        return

    try:
        current_span = trace.get_current_span()
        if current_span:
            for key, value in attributes.items():
                current_span.set_attribute(key, str(value))
    except Exception as e:
        logger.debug(f"Failed to add trace attributes: {e}")


def trace_ai_generation(
    model: str,
    prompt_length: int,
    max_tokens: int,
    tracer: Optional[trace.Tracer] = None
):
    """
    Specialized tracing for AI generation operations.

    Args:
        model: AI model name
        prompt_length: Length of the prompt in characters
        max_tokens: Maximum tokens to generate
        tracer: Tracer instance

    Returns:
        Context manager for the AI generation span

    Usage:
        with trace_ai_generation("gpt-4", len(prompt), 500):
            response = await generate_content(prompt)
    """
    return trace_operation(
        "ai_generation",
        tracer=tracer,
        model=model,
        prompt_length=prompt_length,
        max_tokens=max_tokens
    )


def trace_database_query(
    operation: str,
    collection: Optional[str] = None,
    tracer: Optional[trace.Tracer] = None
):
    """
    Specialized tracing for database operations.

    Args:
        operation: Operation type (e.g., "query", "insert", "update")
        collection: Database collection/table name
        tracer: Tracer instance

    Returns:
        Context manager for the database operation span

    Usage:
        with trace_database_query("insert", "campaigns"):
            db.collection("campaigns").add(campaign_data)
    """
    attrs = {"operation": operation}
    if collection:
        attrs["collection"] = collection

    return trace_operation(f"database_{operation}", tracer=tracer, **attrs)


def trace_service_call(
    service_name: str,
    endpoint: str,
    tracer: Optional[trace.Tracer] = None
):
    """
    Specialized tracing for service-to-service calls.

    Args:
        service_name: Name of the service being called
        endpoint: API endpoint being called
        tracer: Tracer instance

    Returns:
        Context manager for the service call span

    Usage:
        with trace_service_call("ai-routing-engine", "/route"):
            response = await client.post(url, json=data)
    """
    return trace_operation(
        f"service_call_{service_name}",
        tracer=tracer,
        service=service_name,
        endpoint=endpoint
    )


# Convenience function to check if tracing is active
def is_tracing_enabled() -> bool:
    """Check if distributed tracing is currently enabled."""
    return TRACING_ENABLED and TRACING_AVAILABLE
