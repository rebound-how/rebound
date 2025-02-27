import logging
from contextlib import contextmanager
from typing import Dict, Iterator

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.resources import Resource, get_aggregated_resources
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.span import Span

try:
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.propagators.cloud_trace_propagator import (
        CloudTraceFormatPropagator,
    )
    from opentelemetry.resourcedetector.gcp_resource_detector import (
        GoogleCloudResourceDetector,
    )

    HAS_GCP_EXPORTER = True
except ImportError:
    HAS_GCP_EXPORTER = False

from reliably_app.config import Settings

__all__ = ["setup_exporter", "instrument_app", "span"]

logger = logging.getLogger("reliably_app")


def instrument_app(app: FastAPI) -> None:  # pragma: no cover
    """
    Configure various OLTP instrumentations to record traces, metrics and
    events of our application.
    """
    provider = trace.get_tracer_provider()
    LoggingInstrumentor().instrument(
        tracer_provider=provider, set_logging_format=False
    )
    AsyncPGInstrumentor().instrument(tracer_provider=provider)
    SQLAlchemyInstrumentor().instrument(
        tracer_provider=provider,
        engine=app.db_engine.sync_engine,  # type: ignore
        enable_commenter=True,
        commenter_options={},
    )
    # HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
    )


def setup_exporter(settings: Settings) -> None:  # pragma: no cover
    resource = Resource(attributes={"service.name": settings.OTEL_SERVICE_NAME})

    if settings.OTEL_GCP_EXPORTER:
        resources = get_aggregated_resources(
            [GoogleCloudResourceDetector(raise_on_error=True)],
            initial_resource=resource,
        )
        provider = TracerProvider(resource=resources)
        exporter = CloudTraceSpanExporter()
        set_global_textmap(CloudTraceFormatPropagator())
    else:
        collector_endpoint = str(settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        if not collector_endpoint:
            return

        headers = {}
        if settings.OTEL_EXPORTER_OTLP_HEADERS:
            for s in settings.OTEL_EXPORTER_OTLP_HEADERS.split(","):
                k, v = s.split("=", 1)
                headers[k] = v

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(  # type: ignore
            endpoint=collector_endpoint, headers=headers
        )

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    trace.get_tracer(__name__)


@contextmanager
def span(
    name: str,
    attributes: Dict[str, str] | None = None,
    record_exception: bool = True,
    set_status_on_exc: bool = True,
) -> Iterator[Span]:
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(
        name,
        attributes=attributes,
        record_exception=record_exception,
        set_status_on_exception=set_status_on_exc,
    ) as span:
        yield span
